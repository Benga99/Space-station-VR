'''
------------------------------------------------------------

Copyright (C) 2020, Brain Products GmbH, Gilching

This file is part of BrainVision LSL Viewer

BrainVision LSL Viewer is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyCorder. If not, see <http://www.gnu.org/licenses/>.

------------------------------------------------------------

@author: Norbert Hauser
@date: 23.03.2020
@version: 1.0
'''

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtCharts import QtCharts

# for PySide2 support at least pyqtgraph 0.11.0 is needed
# pip install git+https://github.com/pyqtgraph/pyqtgraph@develop
import pyqtgraph as pg

import numpy as np
import shiboken2 as sip
import ctypes
from operator import itemgetter
import copy
import time

from lxml import etree
from lxml import objectify 

from base.modbase import ModuleBase
from base.modbase import RecordingMode, ChannelGroup, ErrorSeverity, EventType, ModuleEvent, TranslateUnits

class ScopeDisplay(ModuleBase):
    """ Oscilloscope """
    def __init__(self, usethread = True, queuesize = 20, name = 'ScopeDisplay', instance = 0):
        super().__init__(usethread, queuesize, name, instance)
        
        # the XML version
        self.xmlVersion = 1

        # get the default settings
        self.settings = ScopeSettings()

        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        # create the display pane
        self.displayPane = QtWidgets.QFrame()
        self.displayPane.setFrameShape(QtWidgets.QFrame.Panel)
        self.displayPane.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.displayPane.setBackgroundRole(QtGui.QPalette.Base)
        self.displayPane.setAutoFillBackground(True)
        #self.displayPane.setContentsMargins(0, 0, 0, 0)

        self.chart = MyChart(parent=self.displayPane)

        self.legendWidget = ChartLegend(self.chart)
        self.legendWidget.setContentsMargins(4, 12, 0, 35)
        self.legendWidget.labelSelected.connect(self.onChannelSelected)


        self.displayLayout = QtWidgets.QHBoxLayout(self.displayPane)
        self.displayLayout.setContentsMargins(0, 0, 0, 0)
        
        self.displayLayout.addWidget(self.legendWidget)
        self.displayLayout.addWidget(self.chart)


        # create the online configuration pane
        self.onlineConfiguration = OnlineConfigurationPane(self)
        self.onlineConfiguration.settingsChanged.connect(self.onSettingsChanged)
        self.onlineConfiguration.baselineRequested.connect(self.onBaselineRequested)
        self.onlineConfiguration.triggerPositionChanged.connect(self.onTriggerPositionChanged)

        self.dataavailable = False
        self.data = None
        self.params = None
        self.xsize = 1500
        self.binning = 300
        self.binningoffset = 0  
        self.selectedChannel = ""

        # trigger
        self.triggerPhase = 'pre'
        self.preTriggerData = None


        # start self.timerEvent() to update display asynchronously
        self.displayTimer = self.startTimer(10, QtCore.Qt.PreciseTimer)
        self.redisplay = False
        self.baselineRequestNow = False

        self.inputMarkers = []

        self.triggerPositionMarker = TriggerPositionMarker(self)

    def terminate(self):
        self.killTimer(self.displayTimer)

    def onSettingsChanged(self, settings):
        rearange = self.settings.timebase != settings.timebase
        rearange |= self.settings.DisplayChannels != settings.DisplayChannels
        rearange |= self.settings.group != settings.group
        rearange |= self.settings.DisplayOffset != settings.DisplayOffset
        self._thLock.acquire()
        self.settings = copy.deepcopy(settings)
        if rearange:
            self.arrangeTraces()
        self._thLock.release()
        
    def onBaselineRequested(self):
        self._thLock.acquire()
        self.baselineRequestNow = True
        self._thLock.release()

    def onTriggerPositionChanged(self, index):
        self._thLock.acquire()
        self.settings.triggerPosition = index
        self.resetDisplay()
        if self.preTriggerData != None:
            self.preTriggerData.eeg_channels = np.empty((self.preTriggerData.eeg_channels.shape[0],0))
            self.preTriggerData.sample_channel = np.empty((1,0))
            self.preTriggerData.markers = []
        self.triggerPhase = 'pre'
        self.redisplay = True
        self.triggerPositionMarker.update()
        self._thLock.release()

    def onChannelSelected(self, index):
        channelName = self.channelGroupProperties[index].name
        self.send_event(ModuleEvent(self._object_name, 
                                    EventType.COMMAND, 
                                    info="ChannelSelected",
                                    cmd_value = channelName))

    def setDefault(self):
        ''' Set all module parameters to default values
        '''
        self.settings = ScopeSettings()

    def process_update(self, params):
        self.params = params
        if not params is None:
            self.defineChannelGroups(params)
            self.arrangeTraces()
            # prepare the pre- and post trigger buffers
            self.preTriggerData = copy.copy(params)
            self.preTriggerData.eeg_channels = np.empty((params.eeg_channels.shape[0],0))
            self.preTriggerData.sample_channel = np.empty((1,0))
            self.triggerPhase = 'pre'

        self.onlineConfiguration.updateUI(self.settings)
        return params

    def get_display_pane(self):
        return self.displayPane

    def get_online_configuration(self):
        return self.onlineConfiguration

    def process_input(self, datablock):
        # don't display impedance date
        if datablock.recording_mode == RecordingMode.IMPEDANCE:
            return
        # keep the data block
        self.data = datablock
        self.dataavailable = True       
        if self.data is None:
            return

        # normal display
        if self.settings.triggerPosition == 0:
            self.updateDisplayBuffer()
            return

        # triggered display
        preSamples = int(self.settings.triggerPosition * self.settings.timebase / 10.0 * self.data.sample_rate + 0.5)
        postSamples = int(min(self.settings.timebase * self.data.sample_rate, self.data.sample_rate / 2.0))

        # any trigger available?
        triggerIndex = np.empty(0)
        if self.triggerPhase == 'pre' and len(self.data.markers) > 0 and self.preTriggerData.sample_channel.shape[1] >= preSamples:
            triggerPos = self.data.markers[0].position
            triggerIndex = np.nonzero(self.data.sample_channel[0]==triggerPos)[0]
            

        if self.triggerPhase == 'pre':
            if triggerIndex.shape[0] > 0:
                idx = triggerIndex[0]
                self.preTriggerData.eeg_channels = np.append(self.preTriggerData.eeg_channels, self.data.eeg_channels[:,:idx], 1)
                self.preTriggerData.sample_channel = np.append(self.preTriggerData.sample_channel, self.data.sample_channel[:,:idx], 1)
                self.preTriggerData.eeg_channels = self.preTriggerData.eeg_channels[:,-preSamples:]
                self.preTriggerData.sample_channel = self.preTriggerData.sample_channel[:,-preSamples:]
                self.triggerPhase = 'post'
                self.preTriggerData.eeg_channels = np.append(self.preTriggerData.eeg_channels, self.data.eeg_channels[:,idx:], 1)
                self.preTriggerData.sample_channel = np.append(self.preTriggerData.sample_channel, self.data.sample_channel[:,idx:], 1)
            else:
                self.preTriggerData.eeg_channels = np.append(self.preTriggerData.eeg_channels, self.data.eeg_channels, 1)
                self.preTriggerData.sample_channel = np.append(self.preTriggerData.sample_channel, self.data.sample_channel, 1)
                self.preTriggerData.eeg_channels = self.preTriggerData.eeg_channels[:,-preSamples:]
                self.preTriggerData.sample_channel = self.preTriggerData.sample_channel[:,-preSamples:]
                
            # add new markers
            self.preTriggerData.markers.extend(self.data.markers) 
            # remove old markers
            min_sc = self.preTriggerData.sample_channel[0].min()
            for marker in self.preTriggerData.markers[:]:
                if marker.position < min_sc:
                    self.preTriggerData.markers.remove(marker)
            
            
        elif self.triggerPhase == 'post':
            self.preTriggerData.eeg_channels = np.append(self.preTriggerData.eeg_channels, self.data.eeg_channels, 1)
            self.preTriggerData.sample_channel = np.append(self.preTriggerData.sample_channel, self.data.sample_channel, 1)
            # add new markers
            self.preTriggerData.markers.extend(self.data.markers) 
            if self.preTriggerData.eeg_channels.shape[1] > postSamples:
                self.data.eeg_channels = self.preTriggerData.eeg_channels
                self.data.sample_channel = self.preTriggerData.sample_channel
                self.data.markers = self.preTriggerData.markers[:]
                self.resetDisplay()
                self.triggerPhase = 'display'             

        elif self.triggerPhase == 'display':
            self.preTriggerData.eeg_channels = np.empty((self.data.eeg_channels.shape[0],0))
            self.preTriggerData.sample_channel = np.empty((1,0))
            self.preTriggerData.markers = []

        # update display buffers
        self.updateDisplayBuffer()


    def process_output(self):
        ''' Send data out to next module
        '''
        if not self.dataavailable:
            return None
        self.dataavailable = False
        return self.data
    
    def defineChannelGroups(self, data):
        # find all groups
        self.settings.groups = [ChannelGroup.ALL]
        for property in data.channel_properties:
            if not property.group in self.settings.groups:
                self.settings.groups.append(property.group)
        # get channel indices for each group
        for group in self.settings.groups:
            select = lambda x: ((x.group == group) or (group == ChannelGroup.ALL))
            m = np.array(list(map(select, data.channel_properties)))
            self.settings.groupChannelIndices[group] = np.nonzero(m)[0]
        
        # validate and set the current selected group
        if len(self.settings.groups) == 1:
            # no amplifier groups available
            self.settings.group = None
        else:
            if self.settings.group not in self.settings.groups:
                if ChannelGroup.EEG in self.settings.groups:
                    # set the EEG group as default if available
                    self.settings.group = ChannelGroup.EEG
                    # set the number of display channels for this group
                    indices = self.settings.ChannelIndices
                    if not indices is None and len(indices) > 1:
                        nc = min(32, len(indices))
                        #self.settings.DisplayChannels = nc
                elif len(self.settings.groups) > 1:
                    # else take the first amplifier group
                    self.settings.group = self.settings.groups[1]
                else:
                    self.settings.group = None



    def selectChannelGroups(self, data):
        if self.settings.ChannelIndices is None:
            self.channelGroupData = data.eeg_channels[:]
            self.channelGroupProperties = data.channel_properties[:]
        else:
            s = self.settings.DisplayOffset
            e = s + self.settings.DisplayChannels
            slc = self.settings.ChannelIndices[s:e]
            self.channelGroupData = data.eeg_channels[slc]
            self.channelGroupProperties = data.channel_properties[slc]


    def arrangeTraces(self):
        # select the requested channel group
        self.selectChannelGroups(self.params)
        
        # remove existing traces from chart
        self.chart.removeAllSeries()

        # insert new traces
        for property in self.channelGroupProperties:
            self.chart.addSeries(property)

        # update Y axis scale
        self.chart.setYScale(0, len(self.chart.series())+1.0)

        # update sample buffer
        self.setTimebase(self.settings.timebase)

        self.chart.setData(self.xValues, self.displayBuffer)

        self.legendWidget.UpdateItems()
        self.redisplay = True

    def setTimebase(self, timebase):
        self.settings.timebase = timebase
        
        # calculate new binning value for current sample rate
        inputsize = self.params.sample_rate * self.settings.timebase
        self.binning = max([1,int(inputsize / self.xsize)])
        self.binningoffset = 0
        
        # calculate new ring buffer size
        traces = len(self.chart.series())
        self.dtX = self.binning / self.params.sample_rate 
        self.xValues = np.arange(0.0, self.settings.timebase + self.dtX, self.dtX)
        self.channelBuffer = np.zeros((traces, len(self.xValues)), 'd' )    # channel buffer
        self.scBuffer = np.zeros((1, len(self.xValues)), np.uint64 )        # sample counter buffer
        self.displayBuffer = np.zeros((traces, len(self.xValues)), 'd' )    # channel display transfer buffer
        self.baseLines = np.zeros((traces, 1), 'd')                         # baseline correction buffer

        # set the polygon x and y values
        offset = self.getDisplayOffset(traces)
        self.displayBuffer += offset

        # reset buffer pointer
        self.writePointer = 0 
        
        # request new baseline values
        self.baselineRequest = True

        # update X axis scale
        self.chart.setXScale(0, self.settings.timebase)

        # prepare to remove all markers
        self.chart.Markers.removeAllMarkers()
        self.inputMarkers = []

    def resetDisplay(self):
        # reset the display
        self.writePointer = 0
        self.binningoffset = 0
        self.baselineRequest = True
        # prepare to remove all markers (not a good idea, resetDisplay can be called from another thread)
        #self.chart.Markers.removeAllMarkers()
        self.inputMarkers = []

    def updateDisplayBuffer(self):
        # triggered display?
        triggered = self.settings.triggerPosition > 0
        if self.triggerPhase != 'display' and triggered:
            return

        # select the requested channel group
        self.selectChannelGroups(self.data)
        
        # anything to display?
        if self.channelGroupData.shape[0] == 0:
            return
        
        # calculate downsampling size
        points = self.channelGroupData.shape[1]
        down = int(points / (self.data.sample_rate * self.dtX))

        # down sample and copy raw data to ring buffer
        channel = 0
        for buf in self.channelBuffer:
            if self.channelGroupData.shape[0] > channel:
                r = -self.channelGroupData[channel][self.binningoffset::self.binning]
                if triggered:
                    bufindex = np.arange(self.writePointer, min(self.writePointer + len(r), self.channelBuffer.shape[1])) 
                    buf.put(bufindex, r, mode='clip')
                else:
                    bufindex = np.arange(self.writePointer, self.writePointer + len(r)) 
                    buf.put(bufindex, r, mode='wrap')
            channel += 1
        # down sample and copy sample counter buffer
        r = self.data.sample_channel[0][self.binningoffset::self.binning]
        if triggered:
            bufindex = np.arange(self.writePointer, min(self.writePointer + len(r), self.scBuffer.shape[1])) 
            self.scBuffer[0].put(bufindex, r, mode='clip')
        else:
            bufindex = np.arange(self.writePointer, self.writePointer + len(r)) 
            self.scBuffer[0].put(bufindex, r, mode='wrap')

        # update write pointer
        self.writePointer += len(r)
        buffersize = self.channelBuffer.shape[1]
        # wrap around occurred?
        if self.writePointer >= buffersize:
            # yes, adjust write pointer
            if triggered:
                self.triggerPhase = 'pre'
                self.writePointer = self.channelBuffer.shape[1]-1
            else:
                while self.writePointer >= buffersize:
                    self.writePointer -= buffersize
            # request new baseline values 
            self.baselineRequest = True
            

        # calculate signal baselines for display baseline correction
        if self.baselineRequest:
            if len(r) <= 20:
                self.baselineRequest = False
                self.baseLines = self.channelBuffer[:,0].reshape(-1,1)
            elif self.writePointer > 10:
                self.baselineRequest = False
                self.baseLines = np.mean(self.channelBuffer[:,5:10], axis=1).reshape(-1,1)

        if self.baselineRequestNow:
            self.baselineRequestNow = False
            # use channel values at current write pointer position as new baselines 
            self.baseLines = self.channelBuffer[:,self.writePointer].reshape(-1,1)


        # calculate new binning offset
        self.binningoffset = self.binning - (points - self.binningoffset - (len(r)-1) * self.binning)
        
        # normalize and offset ring buffer values
        channels = self.channelBuffer.shape[0]
        rangeY = self.chart.rangeY()
        scale = rangeY / self.settings.Scale / 10.0
        offset = self.getDisplayOffset(channels)
        bottomMargin = -2.0             # no margin, clip below window
        topMargin = channels + 1.0      # no margin, clip above window
        
        # baseline correction
        if self.settings.baseLineCorrection:
            buf = (self.channelBuffer - self.baseLines) * scale + offset
        else:
            buf = self.channelBuffer * scale + offset

        # clip to visible area
        #buf.clip(bottomMargin, topMargin, out=self.displayBuffer)
        self.displayBuffer = buf[:]
        
        # add EEG marker to marker transfer list
        if triggered:
            max_sc = self.scBuffer[0].max()
            for marker in self.data.markers[:]:
                if marker.position > max_sc:
                    self.data.markers.remove(marker)
            self.inputMarkers.extend(self.data.markers)
        else:
            self.inputMarkers.extend(self.data.markers)
        
        # redisplay everything
        #if self.receive_data_available() < 3:
        self.redisplay = True

    def getDisplayOffset(self, channels):
        ''' display channel distribution
        '''
        offset = np.arange(channels, 0, -1).reshape(-1,1) - 0.0
        return offset


    def setPolylineValues(self, polygon, xdata=None, ydata=None):
        ''' Convert numpy series data to QPolygon(F) polyline
        '''
        size = len(polygon)

        dtype, tinfo = np.float, np.finfo
        bufferaddress = sip.getCppPointer(polygon.data())[0]
        buffersize = 2*size*tinfo(dtype).dtype.itemsize    
        buffer = (ctypes.c_byte * buffersize).from_address(bufferaddress)

        memory = np.frombuffer(buffer, np.float)
        if xdata is not None:
            memory[:(size-1)*2+1:2] = xdata
        if ydata is not None:
            memory[1:(size-1)*2+2:2] = ydata

        return polygon

    def timerEvent(self, e):
        ''' Timer event to update display
        '''
        if self.redisplay:
            t = time.perf_counter()
            # acquire thread lock 
            self._thLock.acquire()
            self.redisplay = False

            try:
                # add trigger markers
                for marker in self.inputMarkers:
                    diffpos = np.int64(self.scBuffer[0] - marker.position)
                    idx = np.abs(diffpos).argmin(0)
                    x = self.xValues[idx]
                    self.chart.Markers.addMarker(marker.position, x, marker.description)
                # remove processed markers
                self.inputMarkers = []
            
                # remove old markers
                min_sc = self.scBuffer[0].min()
                self.chart.Markers.removeMarkers(min_sc)

                # check color attributes
                updateLegend = False
                series = self.chart.series()
                for idx in range(self.channelGroupProperties.shape[0]):
                    if self.selectedChannel == self.channelGroupProperties[idx].name:
                        color = QtCore.Qt.green
                    else:
                        color = self.channelGroupProperties[idx].color
                    series[idx].setColor(QtGui.QColor(color))

                    
                # copy ring buffer to display
                t = time.perf_counter()
                self.chart.setData(self.xValues, self.displayBuffer)
                dt = (time.perf_counter() - t) * 1000.0
                #print("%.0f ms"%dt)

            except Exception as e:
                self.send_exception(e)

            # release thread lock 
            self._thLock.release()


    def getXML(self):
        ''' Get module properties for XML configuration file
        @return: objectify XML element::
            e.g.
            <ScopeDisplay instance="0" version="1">
                <timebase>1000</timebase>
                ...
            </ScopeDisplay>
        '''
        settings = self.settings.getXML()
        E = objectify.E
        cfg = E.ScopeDisplay(settings,
                           version=str(self.xmlVersion),
                           instance=str(self._instance),
                           module="display")
        return cfg
        
    def setXML(self, xml):
        ''' Set module properties from XML configuration file
        @param xml: complete objectify XML configuration tree, 
        module will search for matching values
        '''
        # search my configuration data
        displays = xml.xpath("//ScopeDisplay[@module='display' and @instance='%i']"%(self._instance))
        if len(displays) == 0:
            # configuration data not found, leave everything unchanged
            return      
        
        # we should have only one display instance from this type
        cfg = displays[0]   
        
        # check version, has to be lower or equal than current version
        version = cfg.get("version")
        if (version == None) or (int(version) > self.xmlVersion):
            self.send_event(ModuleEvent(self._object_name, EventType.ERROR, "XML Configuration: wrong version"))
            return
        version = int(version)
        
        # get the values
        try:
            settings = cfg.Settings
            self.settings.setXML(settings, version)
            self.onlineConfiguration.updateUI(self.settings)
       
        except Exception as e:
            self.send_exception(e, severity=ErrorSeverity.NOTIFY)

'''
------------------------------------------------------------
Chart
------------------------------------------------------------
'''

class MyChart(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.traces = []

        self.plotItem.setContentsMargins(5, 5, 10, 0)

        # add a marker display 
        self.Markers = MarkerItems()
        self.plotItem.addItem(self.Markers)

        # disable the context menu
        self.setMenuEnabled(False) 

        # redirect the 'auto' button
        self.plotItem.autoBtn.clicked.disconnect(self.plotItem.autoBtnClicked)
        self.plotItem.autoBtn.clicked.connect(self.autoBtnClicked)

        self.xRange = (0, 1)
        self.yRange = (0, 1)

        yaxis = self.getAxis('left')
        yaxis.showLabel(False)
        yaxis.setStyle(showValues=False)
        yaxis.setStyle(tickLength=-10)
        yaxis.setTickSpacing(1, 1)
        yaxis.setScale(2.0)

        yaxisRight = self.getAxis('right')
        yaxisRight.showLabel(False)
        yaxisRight.setStyle(showValues=False)
        yaxisRight.setStyle(tickLength=-10)
        yaxisRight.setTickSpacing(1, 1)
        yaxisRight.setScale(2.0)
        yaxisRight.show()

        xaxis = self.getAxis('bottom')
        xaxis.showLabel(True)
        xaxis.setGrid(128)

        xaxisTop = self.getAxis('top')
        xaxisTop.showLabel(False)
        xaxisTop.setStyle(showValues=False)
        xaxisTop.show()

    def setXScale(self, min, max):
        self.setXRange(min, max, padding=0)
        self.xRange = (min, max)

        if max < 0.1:
            major = 0.05
            minor = 5
        elif max < 1.0:
            major = 0.1
            minor = 5
        elif max > 10.0:
            major = 10.0
            minor = 10
        else:
            major = 1.0
            minor = 5
        #xaxis = self.getAxis('bottom')
        #xaxis.setTickSpacing(major, minor)



    def setYScale(self, min, max):
        self.setYRange(min, max, padding=0)
        self.yRange = (min, max)

        yaxis = self.getAxis('left')
        yaxis.setTickSpacing(1, 1)
        yaxis.setScale(10.0/self.rangeY())

        yaxisRight = self.getAxis('right')
        yaxisRight.setTickSpacing(1, 1)
        yaxisRight.setScale(10.0/self.rangeY())

    def rangeY(self):
        return self.yRange[1] - self.yRange[0]

    def removeAllSeries(self):
        for t in self.traces:
            self.removeItem(t)
        self.traces = []

    def addSeries(self, property):
        trace = MyCurveItem(name=property.name, unit=property.unit)
        trace.setColor(QtGui.QColor(property.color))
        self.traces.append(trace)
        self.addItem(trace)

    def series(self):
        return self.traces

    def setData(self, xValues, yValues):
        idx = 0
        for t in self.traces:
            t.setData(xValues, yValues[idx])
            idx += 1
        
    def autoBtnClicked(self, clicked):
        self.setXRange(*self.xRange, padding=0)
        self.setYRange(*self.yRange, padding=0)


class MyCurveItem(pg.PlotCurveItem):
    colorChanged = QtCore.Signal(QtGui.QColor)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = QtGui.QColor(0, 0, 0)
        self.setPen(self.color)
        self.unit = kwargs["unit"]

    def setColor(self, color):
        if color != self.color:
            self.color = color
            self.setPen(color)
            self.colorChanged.emit(color)

'''
------------------------------------------------------------
Legend
------------------------------------------------------------
'''

class ChartLegend(QtWidgets.QFrame):
    labelSelected = QtCore.Signal(int)
    def __init__(self, chart, *args):
        super().__init__()
        self.chart = chart
        self.setLayout(QtWidgets.QVBoxLayout())
        self.items = []

    def UpdateItems(self):
        self.clearLayout()
        self.items = []
        for idx, s in enumerate(self.chart.series()):
            legend = s.name() + " [" + TranslateUnits(s.unit) + "]"
            l = LegendItem(idx, legend)
            l.setColor(s.color)
            l.selected.connect(self.itemSelected)
            s.colorChanged.connect(l.setColor)
            self.items.append(l)
            self.layout().addStretch()
            self.layout().addWidget(l)
        self.layout().addStretch()

    def clearLayout(self):
        while self.layout().count():
            child = self.layout().takeAt(0)
            if child.widget() is not None:
                child.widget().hide()
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

    def itemSelected(self, index):
        self.labelSelected.emit(index)


class LegendItem(QtWidgets.QPushButton):
    selected = QtCore.Signal(int)
    def __init__(self, index, *args, **kwargs):
        QtWidgets.QPushButton.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.setFlat(True)
        self.setMinimumHeight(10)
        self.index = index
        self.clicked.connect(self.labelClicked)

    def sizeHint(self):
        w = self.fontMetrics().width("   {}   ".format(self.text()))
        h = QtWidgets.QPushButton.sizeHint(self).height()
        return QtCore.QSize(w, h)

    def setColor(self, color):
        p = self.palette()
        p.setColor(QtGui.QPalette.ButtonText, color);
        self.setPalette(p)

    def labelClicked(self, state):
        self.selected.emit(self.index)



'''
------------------------------------------------------------
Markers
------------------------------------------------------------
'''

class MarkerItems(pg.UIGraphicsItem):
    def __init__(self, *args, **kwargs):
        super().__init__()
        
        self.yrange = [0.03, 0.04]
        self.markers = []
        pen = (150,150,0)
        self.setPen(pen)
        self.path = QtGui.QPainterPath()
        self.setZValue(10)
        self.font = QtGui.QFont("arial", 8)


    def setPen(self, *args, **kwargs):
        self.pen = pg.mkPen(*args, **kwargs)

    def dataBounds(self, *args, **kargs):
        return None  ## item should never affect view autoscaling

    def addMarker(self, sampleCounter, xValue, label):
        m = MarkerItem(sampleCounter, xValue, label, self.font)
        self.markers.append(m)
        self.rebuildTicks()

    def removeMarkers(self, samplecounter):
        rebuild = False
        for marker in self.markers[:]:
            if marker.sampleCounter < samplecounter:
                self.markers.remove(marker)
                rebuild = True
        if rebuild:
            self.rebuildTicks()

    def removeAllMarkers(self):
        self.markers = []
        self.rebuildTicks()

    def rebuildTicks(self):
        self.path = QtGui.QPainterPath()
        for marker in self.markers:
            x = marker.xPosition
            self.path.moveTo(x, 0.)
            self.path.lineTo(x, 1.)
        self.update()

    def paint(self, p, *args):
        super().paint(p, *args)

        br = self.boundingRect()
        h = br.height()
        br.setY(br.y() + self.yrange[0] * h)
        br.setHeight((self.yrange[1] - self.yrange[0]) * h)
        p.translate(0, br.y())
        p.scale(1.0, br.height())
        p.setPen(self.pen)
        p.drawPath(self.path)

        t = time.perf_counter()
        p.save();
        p.setFont(self.font)
        ti = p.transform().inverted()[0]
        p.setTransform(ti, True)

        for marker in self.markers:
            label = marker.text
            textRect = QtCore.QRectF(marker.textRect)
            localPos = QtCore.QRectF(marker.xPosition, br.y(), br.width(), br.height())
            devicePos = self.mapRectToDevice(localPos)
            y = devicePos.bottom() + textRect.height()
            x = devicePos.left() - textRect.width()/2
            textRect.translate(x, y)
            p.drawText(textRect, label, QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            #p.drawRect(textRect)

        p.restore();
        dt = (time.perf_counter() - t) * 1000.0
        #print("%.0f ms"%dt)


class MarkerItem():
    def __init__(self, samplecounter, xvalue, text, font):
        self.sampleCounter = samplecounter
        self.xPosition = xvalue
        self.text = text
        self.font = font
        fm = QtGui.QFontMetrics(self.font)
        self.textRect = fm.boundingRect(text.replace(' ', '_'))






'''
------------------------------------------------------------
Trigger Position Marker
------------------------------------------------------------
'''

class TriggerPositionMarker(pg.UIGraphicsItem):

    def __init__(self, scope):
        super().__init__()
        scope.chart.plotItem.addItem(self)
        self.scope = scope
        self.setZValue(100)
        self.penLight = pg.mkPen(QtGui.QColor(QtCore.Qt.yellow))
        self.penDark = pg.mkPen(QtGui.QColor(QtCore.Qt.darkYellow))

    def dataBounds(self, *args, **kargs):
        return None  ## item should never affect view autoscaling


    def paint(self, painter, *args):
        super().paint(painter, *args)
        if self.scope.settings.triggerPosition == 0 or self.scope.params is None:
            return

        br = self.boundingRect()
        painter.translate(0, br.y())
        painter.scale(1.0, br.height())

        preSamples = int(self.scope.settings.triggerPosition * self.scope.settings.timebase / 10.0 * self.scope.params.sample_rate + 0.5)
        #posX =  self.scope.settings.timebase * self.scope.settings.triggerPosition / 10 
        posX = preSamples / self.scope.params.sample_rate
        anchor = QtCore.QPointF()
        anchor.setY(1.0)
        anchor.setX(posX)

        w = 0.008 * br.width()
        h = -0.01 
        p1 = QtCore.QPointF(anchor.x()-w, anchor.y())
        p2 = QtCore.QPointF(p1.x()+2*w, p1.y())
        p3 = QtCore.QPointF(p1.x()+w, p1.y()+h)
        path = QtGui.QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        path.lineTo(p1)

        p1 = QtCore.QPointF(anchor.x(), 0)
        p2 = QtCore.QPointF(anchor.x(), 1)
        painter.setPen(self.penLight)
        painter.drawLine(p1, p2)

        painter.setBrush(QtCore.Qt.darkYellow)
        painter.setPen(self.penDark)
        painter.drawPath(path)


'''
------------------------------------------------------------
Settings
------------------------------------------------------------
'''

class ScopeSettings(object):
    def __init__(self):
        self.timebase = 5.0                             # time base in seconds per screen
        self.baseLineCorrection = True
        self.group = ChannelGroup.EEG                   # current selected channel group 
        self.groups = [ChannelGroup.EEG]                # available channel groups
        self.groupScales = {ChannelGroup.EEG:500.0}     # scales for available channel groups
        self.displayChannels = {ChannelGroup.EEG:32}    # number of display channels
        self.groupChannelIndices = {}                   # available channel indices in groups
        self.groupDisplayOffset = {}                    # first display channel in groups
        self.triggerPosition = 0                        # triggered display position in division 0=free running

    @property
    def Scale(self):
        scale = 1000.0
        if self.group in self.groupScales:
            scale = self.groupScales[self.group]
        return scale
    @Scale.setter
    def Scale(self, scale):
        self.groupScales[self.group] = scale

    @property
    def DisplayChannels(self):
        channels = 32
        if self.group in self.displayChannels:
            channels = self.displayChannels[self.group]
        return channels
    @DisplayChannels.setter
    def DisplayChannels(self, channels):
        self.displayChannels[self.group] = channels

    @property
    def DisplayOffset(self):
        offset = 0
        if self.group in self.groupDisplayOffset:
            offset = self.groupDisplayOffset[self.group]
        return offset
    @DisplayOffset.setter
    def DisplayOffset(self, offset):
        self.groupDisplayOffset[self.group] = offset

    @property
    def ChannelIndices(self):
        indices = None
        if self.group in self.groupChannelIndices:
            indices = self.groupChannelIndices[self.group]
        return indices

    def getXML(self):
        E = objectify.E
      
        scales = E.scales()
        for key,value in self.groupScales.items():
            keyname = ChannelGroup.Name[key]
            scales[keyname] = value

        channels = E.channels()
        for key,value in self.displayChannels.items():
            keyname = ChannelGroup.Name[key]
            channels[keyname] = value

        settings = E.Settings(
            E.timebase(self.timebase),
            E.baseline(self.baseLineCorrection),
            E.trigger(self.triggerPosition),
            scales,
            channels,
            )
        return settings

    def setXML(self, cfg, version):
        self.timebase = cfg.timebase.pyval
        self.baseLineCorrection = cfg.baseline.pyval
        self.triggerPosition = cfg.trigger.pyval
        for channel in cfg.channels.iterchildren():
            try:
                key = ChannelGroup.Name.index(channel.tag)
                self.displayChannels[key] = channel.pyval
            except:
                pass
        for scale in cfg.scales.iterchildren():
            try:
                key = ChannelGroup.Name.index(scale.tag)
                self.groupScales[key] = scale.pyval
            except:
                pass

'''
------------------------------------------------------------
ONLINE GUI
------------------------------------------------------------
'''

class OnlineConfigurationPane(QtWidgets.QFrame):
    settingsChanged = QtCore.Signal(ScopeSettings)
    baselineRequested = QtCore.Signal()
    triggerPositionChanged = QtCore.Signal(int)
    def __init__(self, module, *args):
        super().__init__()
        self.module = module
        self.settings = copy.deepcopy(module.settings)

        # make it nice ;-)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setObjectName("groupBox")
        self.groupBox.setTitle("Display")

        self.labelTimebase = QtWidgets.QLabel("Timebase")
        self.cbTimebase = QtWidgets.QComboBox()
        self.cbTimebase.setObjectName("cbTimebase")
        self.unitTimebase = QtWidgets.QLabel("/Page")
        times =  {"0.1 s":0.1, "0.05 s":0.05, "0.2 s":0.2, "0.5 s":0.5, 
                  "1 s":1.0, "2 s":2.0, "5 s":5.0,
                  "10 s":10.0, "20 s":20.0, "50 s":50.0
                  }
        self.cbTimebase.clear()
        for text, val in sorted(list(times.items()), key=itemgetter(1)):
            self.cbTimebase.addItem(text, val)   


        self.labelScale = QtWidgets.QLabel("Scale")
        self.cbScale = QtWidgets.QComboBox()
        self.cbScale.setObjectName("cbScale")
        #self.unitScale = QtWidgets.QLabel("/Div")
        #scales = {"0.5 µV":0.5, "1 µV":1.0, "2 µV":2.0, "5 µV":5.0, 
        #          "10 µV":10.0, "20 µV":20.0, "50 µV":50.0,
        #          "100 µV":100.0, "200 µV":200.0, "500 µV":500.0,
        #          "1 mV":1000.0, "2 mV":2000.0, "5 mV":5000.0,
        #          "10 mV":10000.0, "20 mV":20000.0, "50 mV":50000.0,
        #          "100 mV":100000.0, "200 mV":200000.0, "500 mV":500000.0,
        #          "1 V":1000000.0, "2 V":2000000.0, "5 V":5000000.0
        #          }
        self.unitScale = QtWidgets.QLabel("Units/Div")
        scales = {"0.5":0.5, "1":1.0, "2":2.0, "5":5.0, 
                  "10":10.0, "20":20.0, "50":50.0,
                  "100":100.0, "200":200.0, "500":500.0,
                  "1e3":1000.0, "2e3":2000.0, "5e3":5000.0,
                  "10e3":10000.0, "20e3":20000.0, "50e3":50000.0,
                  "100e3":100000.0, "200e3":200000.0, "500e3":500000.0,
                  "1e6":1000000.0, "2e6":2000000.0, "5e6":5000000.0
                  }
        self.cbScale.clear()
        for text, val in sorted(list(scales.items()), key=itemgetter(1)):
            self.cbScale.addItem(text, val)

        self.labelChannels = QtWidgets.QLabel("Channels", self.groupBox)
        self.cbChannelGroups = QtWidgets.QComboBox(self.groupBox)
        self.cbChannelGroups.setObjectName("cbChannelGroups")
        self.cbSelectedChannels = QtWidgets.QComboBox(self.groupBox)
        self.cbSelectedChannels.setObjectName("cbSelectedChannels")
        self.sbChannels = QtWidgets.QSpinBox(self.groupBox)
        self.sbChannels.setObjectName("sbChannels")
        self.sbChannels.setRange(1, 32)
        self.layoutChannels = QtWidgets.QHBoxLayout()
        self.layoutChannels.addWidget(self.cbSelectedChannels)
        self.layoutChannels.addWidget(self.sbChannels)

        self.checkBaseline = QtWidgets.QCheckBox("Baseline Correction", self.groupBox)
        self.checkBaseline.setObjectName("checkBaseline")
        self.buttonNow = QtWidgets.QPushButton("Now", self.groupBox)
        self.buttonNow.setObjectName("buttonNow")
        self.layoutBaseline = QtWidgets.QHBoxLayout()
        self.layoutBaseline.addWidget(self.checkBaseline)
        self.layoutBaseline.addWidget(self.buttonNow)

        # trigger settings
        self.cbTriggerPosition = QtWidgets.QComboBox(self.groupBox)
        self.cbTriggerPosition.setObjectName("cbTriggerPosition")
        self.labelTriggerPosition = QtWidgets.QLabel("Trigger position", self.groupBox)
        self.labelTriggerPositionU = QtWidgets.QLabel("Div", self.groupBox)
        self.cbTriggerPosition.addItem("off")
        for n in range(1,10):
            self.cbTriggerPosition.addItem(str(n))


        # give us a layout and add widgets
        self.gridLayoutGroup = QtWidgets.QGridLayout(self.groupBox)
        row = 0
        self.gridLayoutGroup.addWidget(self.labelTimebase, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.cbTimebase, row, 1, 1, 1)
        self.gridLayoutGroup.addWidget(self.unitTimebase, row, 2, 1, 1)
        row += 1
        self.gridLayoutGroup.addWidget(self.labelScale, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.cbScale, row, 1, 1, 1)
        self.gridLayoutGroup.addWidget(self.unitScale, row, 2, 1, 1)
        row += 1
        self.gridLayoutGroup.addWidget(self.labelChannels, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.cbChannelGroups, row, 1, 1, 1)
        #self.gridLayoutGroup.addWidget(self.cbSelectedChannels, row, 2, 1, 1)
        #self.gridLayoutGroup.addWidget(self.sbChannels, row, 3, 1, 1)
        self.gridLayoutGroup.addLayout(self.layoutChannels, row, 2, 1, 1)
        row += 1
        self.gridLayoutGroup.addWidget(self.labelTriggerPosition, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.cbTriggerPosition, row, 1, 1, 1)
        self.gridLayoutGroup.addWidget(self.labelTriggerPositionU, row, 2, 1, 1)
        row += 1
        self.gridLayoutGroup.addLayout(self.layoutBaseline, row, 0, 1, 3)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.groupBox, 0, 1, 1, 1)
       
        self.inUpdate = False

        # actions
        QtCore.QMetaObject.connectSlotsByName(self)


    def updateUI(self, settings):
        self.inUpdate = True
        self.checkBaseline.setChecked(settings.baseLineCorrection)
        
        idx = self.cbTimebase.findData(settings.timebase)
        self.cbTimebase.setCurrentIndex(idx)
        
        idx = self.cbScale.findData(settings.Scale)
        self.cbScale.setCurrentIndex(idx)
        
        self.cbChannelGroups.clear()
        for group in settings.groups:
            self.cbChannelGroups.addItem(ChannelGroup.Name[group], group)
        idx = self.cbChannelGroups.findData(settings.group)
        self.cbChannelGroups.setCurrentIndex(idx)

        self.sbChannels.setValue(settings.DisplayChannels)

        self.cbTriggerPosition.setCurrentIndex(settings.triggerPosition)

        self.settings = copy.deepcopy(settings)
        self.updateChannelSelection()
        self.inUpdate = False

    def updateChannelSelection(self):
        # create channel selection entries based on 
        # group size and number of display channels
        if self.settings.ChannelIndices is None:
            self.cbSelectedChannels.clear()
            return

        channels = self.settings.ChannelIndices.shape[0]
        step = self.settings.DisplayChannels
        entries = []
        for i in range(0, channels, step):
            if step == 1:
                e = ("%i"%(i+1), i)
            else:
                end = i + step
                if end > channels:
                    end = channels
                e = ("%i - %i"%(i+1, end), i)
            entries.append(e)

        currentOffset = self.settings.DisplayOffset
        self.cbSelectedChannels.clear()
        for e in entries:
            self.cbSelectedChannels.addItem(e[0], e[1])

        idx = max(0, self.cbSelectedChannels.findData(currentOffset))
        self.cbSelectedChannels.setCurrentIndex(idx)

    def emitSettingsChanged(self):
        if not self.inUpdate:
            self.settingsChanged.emit(self.settings)


    @QtCore.Slot(int)
    def on_cbTimebase_currentIndexChanged(self, index):
        if index < 0:
            return
        tb = self.cbTimebase.currentData()
        if tb != self.settings.timebase:
            self.settings.timebase = tb
            self.emitSettingsChanged()

    @QtCore.Slot(int)
    def on_cbScale_currentIndexChanged(self, index):
        if index < 0:
            return
        scale = self.cbScale.currentData()
        if scale != self.settings.Scale:
            self.settings.Scale = scale
            self.emitSettingsChanged()

    @QtCore.Slot(int)
    def on_cbChannelGroups_currentIndexChanged(self, index):
        if index < 0:
            return
        group = self.cbChannelGroups.currentData()
        if group != self.settings.group:
            self.settings.group = group
            idx = self.cbScale.findData(self.settings.Scale)
            self.cbScale.setCurrentIndex(idx)
            self.sbChannels.setValue(self.settings.DisplayChannels)
            self.updateChannelSelection()
            self.emitSettingsChanged()

    @QtCore.Slot(int)
    def on_cbSelectedChannels_currentIndexChanged(self, index):
        if index < 0:
            return
        offset = self.cbSelectedChannels.currentData()
        if offset != self.settings.DisplayOffset:
            self.settings.DisplayOffset = offset
            self.emitSettingsChanged()

    @QtCore.Slot(int)
    def on_sbChannels_valueChanged(self, value):
        if value != self.settings.DisplayChannels:
            self.settings.DisplayChannels = value
            self.updateChannelSelection()
            self.emitSettingsChanged()

    @QtCore.Slot(int)
    def on_checkBaseline_stateChanged(self, state):
        check = state == QtCore.Qt.Checked
        if check != self.settings.baseLineCorrection:
            self.settings.baseLineCorrection = check
            self.emitSettingsChanged()
        self.buttonNow.setEnabled(check)

    @QtCore.Slot(bool)
    def on_buttonNow_clicked(self, checked):
        self.baselineRequested.emit()

    @QtCore.Slot(int)
    def on_cbTriggerPosition_currentIndexChanged(self, index):
        if index < 0:
            return
        self.settings.triggerPosition = index
        if not self.inUpdate:
            self.triggerPositionChanged.emit(index)


