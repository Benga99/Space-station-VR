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

from base.modbase import *
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2.QtCharts import QtCharts
import collections
import shiboken2 as sip
import ctypes
import scipy as sc
from math import ceil, log, floor
import sys


class FFT_RMS(ModuleBase):
    ''' FFT, RMS and Peak measurement module
    
    Calculate and display a FFT, RMS and peak values for selected channels. 
    Channel selection will be send from display module as command events.
     
    '''

    def __init__(self, *args, **keys):
        ''' Constructor. 
        Initialize instance variables and instantiate GUI objects 
        '''
        # initialize the base class, give a descriptive name
        ModuleBase.__init__(self, name="FFT RMS", **keys)    

        # XML parameter version
        # 1: initial version
        self.xmlVersion = 1
        
        # initialize module variables
        self.data = None                #: hold the data block we got from previous module
        self.dataavailable = False      #: data available for output to next module 
        self.channelFifo = collections.deque() #: channel selection FiFo
        self.params = EEG_DataBlock(0,0)    #: default channel configuration

        # Plot configuration data
        self.chunk = 1024               #: FFT chunk size
        self.frequency_range = 200      #: Display frequency range [Hz]
        self.plot_items = 4             #: Maximum number of plot items

        # instantiate online configuration pane
        self.onlinePane = _OnlineCfgPane()
        # connect the event handler for changes in chunk size
        self.onlinePane.comboBoxChunk.currentIndexChanged.connect(self.onlineValueChanged)
        # connect the event handler for changes in frequency
        self.onlinePane.comboBoxFrequency.currentIndexChanged.connect(self.onlineValueChanged)

        # instantiate signal pane
        self.signalPane = _SignalPane()

        # set default values
        self.setDefault()

    def setDefault(self):
        ''' Set all module parameters to default values
        '''
        self.chunk = 1024               
        self.frequency_range = 200      
        self.plot_items = 4      
        self.onlinePane.setCurrentValues(self.frequency_range, self.chunk)       
        
    def process_input(self, datablock):
        ''' Get data from previous module.
        Because we need to exchange data between different threads we will use 
        a queue object to send data to the display thread to be thread-safe.  
        @param datablock: EEG_DataBlock object 
        '''
        self.dataavailable = True       # signal data availability
        self.data = datablock           # get a local reference
        
        # anything to do ? check channel selection and recording mode.
        # If we are in impedance mode, it makes no sense to calculate the FFT
        if (self.channel_index[0].size == 0) or (self.data.recording_mode == RecordingMode.IMPEDANCE):
            return
        
        # because we need a predefined data chunk size, we have to collect data until
        # at least one data block of data with chunk size is available
        # so first we append data from selected channels to a local buffer
        append = self.data.eeg_channels[self.channel_index]
        self.eeg_channels = np.append(self.eeg_channels, append, 1) # append to axis 1 of local buffer 

        # slice the local buffer into chunks
        while self.eeg_channels.shape[1] > self.chunk:
            # copy data of chunk size from all selected channels
            bufcopy = self.eeg_channels[:,:self.chunk]
            self.eeg_channels = self.eeg_channels[:,self.chunk:]
            # send channel data to the signal pane queue
            if self.signalPane.data_queue.empty():
                self.signalPane.data_queue.put(bufcopy, False) 
            #print bufcopy.shape[1]
            
        # set different color for selected channels
        selected = self.data.channel_properties[self.channel_index]
        for ch in selected:
            ch.color = QtCore.Qt.darkYellow
    
    
    def process_output(self):
        ''' Send data out to next module
        '''
        if not self.dataavailable:
            return None
        self.dataavailable = False
        return self.data
    
    
    def process_update(self, params):
        ''' Evaluate and maybe modify the channel configuration.
        @param params: EEG_DataBlock object.
        @return: EEG_DataBlock object
        '''
        # keep a reference of the channel configuration
        self.params = copy.copy(params)
        # Create a new channel selection array and setup the signal pane
        self.updateSignalPane()
        # set different color for selected channels
        selected = params.channel_properties[self.channel_index]
        for ch in selected:
            ch.color = QtCore.Qt.darkYellow
        return params
    
    
    def process_event(self, event):
        ''' Handle events from attached receivers. 
        @param event: ModuleEvent
        '''
        # Search for ModuleEvents from display module and update channel selection
        if (event.type == EventType.COMMAND) and (event.info == "ChannelSelected"):
            channel = event.cmd_value
            # if channel is already in selection, remove it
            if channel in self.channelFifo:
                self.channelFifo.remove(channel)
            else:
                self.channelFifo.appendleft(channel)
            # limit selection to max. entries
            while len(self.channelFifo) > self.plot_items:
                self.channelFifo.pop()
            # notify other receivers
            if not self._running:
                self.update_receivers(params=self.params, propagate_only=False)
            else:
                # Create a new channel selection array and setup the signal pane
                self.updateSignalPane()
    
    
    def updateSignalPane(self):
        ''' Create a channel selection array and setup the signal pane
        '''
        # acquire ModuleBase thread lock
        self._thLock.acquire()
        
        # get values from online configuration pane
        self.frequency_range, self.chunk = self.onlinePane.getCurrentValues()
        
        # if channel FiFo contains more than maximum configured items, remove odd
        while len(self.channelFifo) > self.plot_items:
            self.channelFifo.pop()
        
        # create channel selection indices from channel FiFo
        mask = lambda x: (x.name in self.channelFifo)
        channel_ref = np.array([mask(p) for p in self.params.channel_properties])
        self.channel_index = np.nonzero(channel_ref)
        
        # create empty calculation buffers
        if self.params.eeg_channels.shape[0] > 0:
            self.eeg_channels = np.delete(np.zeros_like(self.params.eeg_channels[self.channel_index]),
                                          np.s_[:], 
                                          1)
        
        # create FFT plot for each selected channel
        self.signalPane.setupDisplay(self.params.channel_properties[self.channel_index],
                                     self.params.sample_rate, 
                                     self.chunk, 
                                     self.frequency_range)
        # release ModuleBase thread lock
        self._thLock.release()
    
        
    def get_display_pane(self):
        ''' Get the signal display pane
        @return: a QFrame object or None if you don't need a display pane
        '''
        return self.signalPane

    def get_online_configuration(self):
        ''' Get the online configuration pane
        @return: a QFrame object or None if you don't need a online configuration pane
        '''
        return self.onlinePane
    
    def get_configuration_pane(self):
        ''' Get the configuration pane
        @return: a QFrame object or None if you don't need a configuration pane
        '''
        cfgPane = _ConfigurationPane(self)
        return cfgPane

    def onlineValueChanged(self, int):
        ''' Event handler for changes in frequency and chunk size 
        '''
        # Create a new channel selection array and setup the signal pane
        self.updateSignalPane()
    
    
    def getXML(self):
        ''' Get module properties for XML configuration file
        @return: objectify XML element::
            e.g.
            <FFT_RMS version="1" module="FFT" instance="0">
                <frequency_range>200.0</frequency_range>
                <chunk_size>2048</chunk_size>
                <plot_items>4</plot_items>
            </Tut_FFT>
        '''
        E = objectify.E
        cfg = E.FFT_RMS(E.frequency_range(self.frequency_range),
                        E.chunk_size(self.chunk),
                        E.plot_items(self.plot_items),
                        version=str(self.xmlVersion),
                        module="FFT",
                        instance=str(self._instance))
        return cfg
        
        
    def setXML(self, xml):
        ''' Set module properties from XML configuration file
        @param xml: complete objectify XML configuration tree, 
        module will search for matching values
        '''
        # search module configuration data
        storages = xml.xpath("//FFT_RMS[@module='FFT' and @instance='%i']"%(self._instance) )
        if len(storages) == 0:
            # configuration data not found, set default values
            self.setDefault()
            return      
        
        # we should have only one instance from this type
        cfg = storages[0]   
        
        # check version, has to be lower or equal than current version
        version = cfg.get("version")
        if (version == None) or (int(version) > self.xmlVersion):
            self.send_event(ModuleEvent(self._object_name, 
                                        EventType.ERROR, 
                                        "XML Configuration: wrong version"))
            return
        version = int(version)
        
        # get the values
        try:
            self.frequency_range = cfg.frequency_range.pyval
            self.chunk = cfg.chunk_size.pyval
            self.plot_items = cfg.plot_items.pyval
            self.onlinePane.setCurrentValues(self.frequency_range, self.chunk)       
        except Exception as e:
            self.send_exception(e, severity=ErrorSeverity.NOTIFY)





################################################################
# Online Configuration Pane

class _OnlineCfgPane(QtWidgets.QFrame):
    ''' Online configuration pane
    '''
    def __init__(self , *args):
        super().__init__(*args)

        # make it nice ;-)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        # give us a layout and group box
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.groupBox.setTitle("FFT")
        
        # group box layout
        self.gridLayoutGroup = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayoutGroup.setHorizontalSpacing(10)
        self.gridLayoutGroup.setContentsMargins(20, -1, 20, -1)
        
        # add the chunk size combobox
        self.comboBoxChunk = QtWidgets.QComboBox(self.groupBox)
        self.comboBoxChunk.setObjectName("comboBoxChunk")
        self.comboBoxChunk.addItem("128")
        self.comboBoxChunk.addItem("256")
        self.comboBoxChunk.addItem("512")
        self.comboBoxChunk.addItem("1024")
        self.comboBoxChunk.addItem("2048")
        self.comboBoxChunk.addItem("4096")
        self.comboBoxChunk.addItem("8129")
        self.comboBoxChunk.addItem("16384")
        self.comboBoxChunk.addItem("32768")
        
        # add the frequency range combobox
        self.comboBoxFrequency = QtWidgets.QComboBox(self.groupBox)
        self.comboBoxFrequency.setObjectName("comboBoxChunk")
        self.comboBoxFrequency.addItem("20")
        self.comboBoxFrequency.addItem("50")
        self.comboBoxFrequency.addItem("100")
        self.comboBoxFrequency.addItem("200")
        self.comboBoxFrequency.addItem("500")
        self.comboBoxFrequency.addItem("1000")
        self.comboBoxFrequency.addItem("2000")
        self.comboBoxFrequency.addItem("5000")
        self.comboBoxFrequency.addItem("10000")
        self.comboBoxFrequency.addItem("20000")
        self.comboBoxFrequency.addItem("50000")

        # create unit labels
        self.labelChunk = QtWidgets.QLabel(self.groupBox)
        self.labelChunk.setText("[n]")
        self.labelFrequency = QtWidgets.QLabel(self.groupBox)
        self.labelFrequency.setText("[Hz]")
        
        # add widgets to layouts
        self.gridLayoutGroup.addWidget(self.comboBoxFrequency, 0, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.labelFrequency, 0, 1, 1, 1)
        self.gridLayoutGroup.addWidget(self.comboBoxChunk, 0, 2, 1, 1)
        self.gridLayoutGroup.addWidget(self.labelChunk, 0, 3, 1, 1)
        
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)

        # set default values
        self.comboBoxFrequency.setCurrentIndex(2)
        self.comboBoxChunk.setCurrentIndex(4)
        
    def getCurrentValues(self):
        ''' Get current selected values for frequency and chunk size
        @return: frequency and chunk size as tuple
        '''
        chunk = int(self.comboBoxChunk.currentText())
        frequency = float(self.comboBoxFrequency.currentText())
        return frequency, chunk

    def setCurrentValues(self, frequency, chunk):
        ''' Set the current values for frequency and chunk size
        @param frequency: new frequency value
        @param chunk: new chunk size
        '''
        # find chunk size index
        idx = -1
        for i in range(self.comboBoxChunk.count()):
            if chunk == int(self.comboBoxChunk.itemText(i)):
                idx = i
        # set new combobox index
        if idx >= 0:
            self.comboBoxChunk.setCurrentIndex(idx)
        
        # find frequency index
        idx = -1
        for i in range(self.comboBoxFrequency.count()):
            if frequency == float(self.comboBoxFrequency.itemText(i)):
                idx = i
        # set new combobox index
        if idx >= 0:
            self.comboBoxFrequency.setCurrentIndex(idx)
            
            

################################################################
# Signal Pane

class _SignalPane(QtWidgets.QFrame):
    ''' FFT display pane
    '''
    def __init__(self , *args):
        super().__init__(*args)

        # Initialize local variables
        self.data_queue = Queue.Queue(10)       # data exchange queue

        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.setAutoFillBackground(True)
        
        # Layout display items
        self.setMinimumSize(QtCore.QSize(0, 0))     # hide signal pane if there are no plot items
        self.verticalLayout = QtWidgets.QVBoxLayout(self) # arrange plot items vertically

        # list of current plot widgets
        self.plot = []

        # start 50ms display timer 
        self.startTimer(50)

        self.hide()

    def setupDisplay(self, channels, samplerate, datapoints, frequency_range):
        ''' Rearrange and setup plot widgets
        @param channels: list of selected channels as EEG_ChannelProperties 
        @param samplerate:  sampling rate in Hz
        @param datapoints:  chunk size in samples
        @param frequency_range: show frequencies up to this value [Hz]
        ''' 
        # show the signal pane only if channels selected
        if len(channels) > 0:
            if self.isHidden():
                self.show()
        else:
            if not self.isHidden():
                self.hide()

        # flush input data queue
        while not self.data_queue.empty():
            self.data_queue.get_nowait()

        # remove previous plot widgets
        for plot in self.plot[:]:
            self.verticalLayout.removeWidget(plot)
            plot.setParent(None)
            self.plot.remove(plot)
            #del plot
            plot.deleteLater()

        # create and setup requested display widgets
        pos = 0
        for channel in channels:
            plot = _FFT_Plot(self)
            self.plot.append(plot)
            unit = TranslateUnits(channel.unit)
            plot.setupDisplay(unit, channel.name, samplerate, datapoints, frequency_range)
            #self.verticalLayout.insertWidget(pos, plot)
            self.verticalLayout.addWidget(plot)
            pos += 1


    def timerEvent(self,e):
        ''' Display timer callback.
        Get data from input queue and distribute it to the plot widgets
        '''
        if not self.data_queue.empty():
            # get data from queue
            channel_data = self.data_queue.get_nowait()
            # distribute data to plot widgets
            for index, plot in enumerate(self.plot):
                plot.calculate(channel_data[index])
        #else:
        #    for index, plot in enumerate(self.plot):
        #        plot.repaint()



class _FFT_Plot(QtCharts.QChartView):
    ''' FFT plot widget
    '''
    def __init__(self, *args):
        super().__init__(*args)

        self.setMinimumSize(QtCore.QSize(200, 100))
        #self.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)

        self.chart = QtCharts.QChart()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setMargins(QtCore.QMargins(0, 0, 5, 5))
        self.chart.setLocalizeNumbers(False)

        self.setChart(self.chart)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        
        axisfont = QtGui.QFont("arial", 8)

        self.axisX = QtCharts.QValueAxis()
        self.axisX.setRange(0, 10.0)
        self.axisX.setTickCount(6)
        self.axisX.setMinorTickCount(4)
        self.axisX.setLabelFormat('%g')
        self.axisX.setTitleText('Frequency [Hz]')

        self.axisY = QtCharts.QValueAxis()
        self.axisY.setRange(0, 10.0)
        self.axisY.setTickCount(6)
        self.axisY.setMinorTickCount(1)
        self.axisY.setLabelFormat('%.0f')
        self.axisY.setTitleText('Amplitude')
        self.axisY.setTitleVisible(True)
        self.axisY.setLabelsVisible(True)
        #self.axisY.setLabelsFont(axisfont)

        legend = self.chart.legend()
        legend.setVisible(False)

        self.trace = QtCharts.QLineSeries()
        pen = self.trace.pen()
        pen.setColor(QtCore.Qt.black)
        #pen.setWidthF(2)
        self.trace.setPen(pen)
        self.trace.setName('FFT')
        self.trace.setUseOpenGL(False)
        self.chart.addSeries(self.trace)
        self.chart.setAxisX(self.axisX, self.trace)
        self.chart.setAxisY(self.axisY, self.trace)

        #r = QtCore.QRectF(100,100,200,200)
        #self.chart.setPlotArea(QtCore.QRectF())

        self.autoScale = True

        # set initial display values
        self.setupDisplay("?", "channel<br>values", 500, 1024, 200) 
        

    def setupDisplay(self, unit, channelname, samplerate, datapoints, frequency_range):
        ''' Initialize all display parameters
        @param unit: channel unit as string 
        @param channelname: channel name as string 
        @param samplerate:  sampling rate in Hz
        @param datapoints:  chunk size in samples
        @param frequency_range: show frequencies up to this value [Hz]
        '''
        self.samplerate = samplerate
        self.datapoints = datapoints
        self.frequency_range = frequency_range
        self.unit = unit
        
        self.dt = 1.0 / samplerate
        self.df = 1.0 / (datapoints * self.dt)
        self.xValues = np.arange(0.0, samplerate, self.df)
        self.yValues = 0.0 * self.xValues
        self.axisX.setRange(0, self.frequency_range)
        self.axisY.setRange(0, 10000)
        self.trace.setName(channelname)
        self.chart.setTitle('%s<br>'%channelname)

        polygon = QtGui.QPolygonF(len(self.xValues))
        self.setPolylineValues(polygon, self.xValues, self.yValues)
        self.trace.replace(polygon)


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


    def _VS(self, uVolt):
        ''' Format voltage string
        '''
        if self.unit == "µV":
            if abs(uVolt) < 1000.0:
                vString = "%4.1f µV"%(uVolt)
            else:
                vString = "%4.2f mV"%(uVolt/1000.0)
        else:
            if abs(uVolt) < 1000.0:
                vString = "%4.1f %s"%(uVolt, self.unit)
            else:
                vString = "%4.2fe3 %s"%(uVolt/1000.0, self.unit)
        return vString
        
    def calculate(self, channel_data):
        ''' Do the FFT
        @param channel_data: raw data array of chunk size
        '''
        lenX = channel_data.shape[0]
        window = np.hanning(lenX)
        window = window / sum(window) * 2.0

        # FFT zero padded for higher resolution
        width = 100 * 1024        
        A = np.fft.fft(channel_data*window, width)
        fsize = len(A)//2
        B = np.abs(A)[:fsize] 
        X = np.fft.fftfreq(fsize*2, self.dt)[:fsize]
        
        # Plot FFT
        # find the last display index and the decimation factor
        lastindex = len(X)
        decimation = 2
        ii = np.nonzero(X > self.frequency_range)
        if len(ii) > 0 and len(ii[0]) > 0:
            lastindex = ii[0][0]
        if lastindex > 4000:
            decimation = 4
        # extract the display data
        yd = B[:lastindex:decimation]
        xd = X[:lastindex:decimation]
        # plot the result
        #print(len(xd),len(yd))
        polygon = QtGui.QPolygonF(len(xd))
        self.setPolylineValues(polygon, xd, yd)
        self.trace.replace(polygon)
        
        # search the maximum peak value
        peaks,_ = sc.signal.find_peaks(B)
        ppIndex = np.argmax(B[peaks])
        pIndex = peaks[ppIndex]
        pf = X[pIndex] 
        pv = B[pIndex]

        # auto scale
        if self.autoScale:
            self.axisY.setRange(0, pv*1.2)
            self.axisX.setRange(0, self.frequency_range)
            self.setLabelFormat()

        rms = np.sqrt(np.mean(channel_data*channel_data))          # calculate RMS
        ptp = np.ptp(channel_data)                                 # calculate peak to peak value 
        #offset = (np.amax(channel_data) + np.amin(channel_data))/2 # mean value
        offset = B[0] / 2                                          # value at 0 Hz

        title = '<b>%s</b>'%self.trace.name() +\
                "   RMS = %s  Vpp = %s  DC = %s <br>fpeak = %.1f Hz Vpeak = %s"\
                %(  self._VS(rms),
                    self._VS(ptp),
                    self._VS(offset),
                    pf, self._VS(pv) )
        self.chart.setTitle(title)

    def setLabelFormat(self):
        ym = self.axisY.max()
        if ym > 10:
            self.axisY.setLabelFormat('%.0f')
        elif ym > 1:
            self.axisY.setLabelFormat('%.1f')
        elif ym > 0.1:
            self.axisY.setLabelFormat('%.2f')
        else:
            self.axisY.setLabelFormat('%.3f')


    def wheelEvent(self, event):
        scroll = event.angleDelta().y()
        delta = 2.0
        if scroll != 0:
            if scroll > 0:
                factor = delta
                dir = 1
            else:
                factor = 1 / delta
                dir = -1
            
            ym = self.axisY.max()
            p = floor(log(ym,10)  + sys.float_info.epsilon)
            c = floor(ym / 10**(p)) + dir
            if c >= 1:
                ym = c * 10**p
            else:
                ym = 9 * 10**(p-1)

            ym = max(0.01, min(1e6, ym))
            self.axisY.setMax(ym)
            self.setLabelFormat()
        self.autoScale = False

        event.accept()
 

################################################################
# Configuration Pane
        
class _ConfigurationPane(QtWidgets.QFrame):
    ''' FFT Module configuration pane.
    
    Tab for global configuration dialog, contains only one item: "Max. number of plot items"
    '''
    def __init__(self, module, *args):
        super().__init__(*args)
        
        # reference to our parent module
        self.module = module
        
        # Set tab name
        self.setWindowTitle("FFT")
        
        # make it nice
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        
        # base layout
        self.gridLayout = QtWidgets.QGridLayout(self)

        # item label
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Max. number of plot items")

        # plot item combobox
        self.comboBoxItems = QtWidgets.QComboBox(self)
        self.comboBoxItems.setObjectName("comboBoxItems")
        # add combobox list items (1-4)
        for n in range(1,5):
            self.comboBoxItems.addItem(str(n))

        # use spacer items to align label and combox top-left
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        # add all items to the layout
        self.gridLayout.addWidget(self.label, 0, 0)
        self.gridLayout.addWidget(self.comboBoxItems, 0, 1)
        self.gridLayout.addItem(spacerItem1, 1, 0, 1, 1)
        self.gridLayout.addItem(spacerItem2, 0, 2, 1, 1)

        # set initial value from parent module
        self.comboBoxItems.setCurrentIndex(self.module.plot_items-1)

        # actions
        self.comboBoxItems.currentIndexChanged.connect(self._ItemsChanged)

    def _ItemsChanged(self, index):
        ''' Event handler for changes in "number of plot items"
        '''
        self.module.plot_items = index + 1  # update the module parameter
        

