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
from resources import resources_rc
import copy
import datetime, time
import numpy as np
from scipy import signal as scpsignal
from lxml import etree
from lxml import objectify 

from base.modbase import ModuleBase, ModuleEvent, EventType, ErrorSeverity, RecordingMode, ModuleError
from base.modbase import ChannelGroup, EEG_DataBlock, ImpedanceIndex
from base.modbase import EEG_Marker
from tools.tableview import GenericTableWidget

from amplifiers.lsl.lslcontrol import *

class AMP_LabStreamingLayer(ModuleBase):
    signalConnectionInfo = QtCore.Signal(object)

    def __init__(self, usethread = True, queuesize = 20, name = 'Stream', instance = 0):
        super().__init__(usethread, queuesize, name, instance)
        
        self.xmlVersion = 1

        self.setDefault()

        # create online configuration pane
        self.onlineConfiguration = OnlineConfigurationPane(self)
        self.onlineConfiguration.signalModeChanged.connect(self.onModeChanged)
        self.onlineConfiguration.signalConnect.connect(self.onConnect)

        # set default values
        self.recordingMode = RecordingMode.STOP
        self.samplingRate = 1000.0
        self.markersToSend = []

        # interval timers
        self.stateTimer = time.perf_counter()
        self.blockTimer = time.perf_counter()

        self.Controler = LSL_Controler()
        self.createChannelSelection()

    def setDefault(self):
        pass

    def onModeChanged(self, newMode):
        ''' SIGNAL from online configuration pane if recording mode changed
        '''
        #print("New recording mode %i"%newMode)
        if newMode == RecordingMode.STOP:
            self.stop()
        else:
            if self._running:
                if not self.stop():
                    self.onlineConfiguration.updateUI(self.recordingMode)
                    return
            self.recordingMode = newMode
            self.start()

    def onConfigurationChanged(self):
        ''' SIGNAL from configuration pane
        '''
        self.update_receivers()

    def onConnect(self, connect):
        ''' SIGNAL from online configuration pane if connect or disconnect requested
        '''
        autostart = False
        if connect:
            try:
                self.Controler.ConnectStreams()
            except Exception as e:
                self.send_exception(e)
            autostart = len(self.Controler.DeviceConnectionInfo) > 0
        else:
            if self.stop():
                self.Controler.DisconnectStreams()
        self.signalConnectionInfo.emit(self.Controler.DeviceConnectionInfo)
        self.update_receivers()
        if autostart:
            self.onModeChanged(RecordingMode.NORMAL)

    def stop(self, force=False):
        ''' Stop data acquisition
        @param force: force stop without query
        @return: True, if stop was accepted by attached modules
        '''
        # ask attached modules for acceptance
        if not force:
            if not self.query("Stop"):
                return False
        # stop it
        ModuleBase.stop(self)
        return True

    def get_online_configuration(self):
        ''' Get the online configuration pane
        '''
        return self.onlineConfiguration

    def get_configuration_pane(self):
        ''' Get the configuration pane
        @return: a QFrame object or None if you don't need a configuration pane
        '''
        cfgPane = ConfigurationPane(self)
        cfgPane.configurationChanged.connect(self.onConfigurationChanged)
        return cfgPane

    def process_start(self):
        # start acquisistion
        self.update_receivers()
        if len(self.dataBlock.channel_properties) == 0:
            raise ModuleError(self._object_name, "no input channels selected!")

        # set start time on first call
        self.start_time = datetime.datetime.now()
        self.sample_timer = time.perf_counter()
        self.stateTimer = time.perf_counter()
        self.markersToSend = []

        self.Controler.Start()

        # send status info
        info = "Start at %.0fHz with %d channels"%(self.dataBlock.sample_rate, len(self.dataBlock.channel_properties))
        self.send_event(ModuleEvent(self._object_name, EventType.LOGMESSAGE, info))
        # send recording mode
        self.send_event(ModuleEvent(self._object_name,
                                    EventType.STATUS,
                                    info = self.dataBlock.recording_mode,  
                                    status_field="Mode"))
        
        
        self.onlineConfiguration.updateUI(self.recordingMode)

    def process_stop(self):
        # stop acquisition
        self.recordingMode = RecordingMode.STOP
        self.Controler.Stop()
        # send status info
        info = "Stop"
        self.send_event(ModuleEvent(self._object_name, EventType.LOGMESSAGE, info))
        # send recording mode
        self.send_event(ModuleEvent(self._object_name,
                                    EventType.STATUS,
                                    info = self.recordingMode,   
                                    status_field="Mode"))
        self.onlineConfiguration.updateUI(self.recordingMode)

    def process_event(self, event):
        # Command events
        if event.type == EventType.COMMAND:
            # check for stop command
            if event.info == "Stop":
                if event.cmd_value == "force":
                    self.stop(force=True)
                else:
                    self.stop()

    def createChannelSelection(self):
        ''' Create index arrays of selected channels and prepare EEG_DataBlock.
        In impedance mode the reference channel is included. 
        '''
        # amplifier available?
        if not self.Controler.AmplifierDevices:
            self.refChannelName = ""
            self.channel_config = EEG_DataBlock.get_default_properties(0, 0)
            self.dataBlock = EEG_DataBlock(0, 0)
            self.dataBlock.channel_properties = copy.deepcopy(self.channel_config)
            return

        # get channel configuration from amplifier
        eegChannels = 0
        auxChannels = 0
        
        # get the number of channels
        self.refChannelName = "GND"
        for amp in self.Controler.AmplifierDevices:
            for c in amp.Channels:
                if c.Enable:
                    if c.Type == 'EEG' or c.Type == 'BIP':
                        eegChannels += 1
                    else:
                        auxChannels += 1
                    
        # create properties  based on channel selection
        self.channel_config = EEG_DataBlock.get_default_properties(eegChannels, auxChannels)
        # create a new data block based on channel selection
        self.dataBlock = EEG_DataBlock(eegChannels, auxChannels)
        
        # update properties
        digitalChannelDescription = []
        self.impedanceChannelSelection = []
        idx = 0
        eegInput = 1
        auxInput = 1
        subjectLabel = len(self.Controler.AmplifierDevices) > 1
        ampNumber = 1
        timestampChannels = 0
        for amp in self.Controler.AmplifierDevices:
            for c in amp.Channels:
                if c.Enable:
                    if c.Type == 'EEG' or c.Type == 'BIP':
                        self.channel_config[idx].inputgroup = ChannelGroup.EEG
                        self.channel_config[idx].group = ChannelGroup.EEG
                        self.channel_config[idx].input = eegInput
                        eegInput += 1
                    else:
                        self.channel_config[idx].inputgroup = ChannelGroup.AUX
                        self.channel_config[idx].group = ChannelGroup.AUX
                        self.channel_config[idx].input = auxInput
                        auxInput += 1
                    #set common properties
                    if subjectLabel:
                        sl = "S%i "%ampNumber
                    else:
                        sl = ""
                    self.channel_config[idx].name = u"%s%s"%(sl,c.Label)
                    self.channel_config[idx].unit = c.Unit
                    # add amplifier number (zero based)
                    self.channel_config[idx].amplifier = ampNumber - 1
                    idx += 1
            ampNumber += 1

        
        # update the timestamp channel array
        if timestampChannels > 0:
            self.dataBlock.timestamp_channel = np.zeros((timestampChannels, 10), np.double)
        else:
            self.dataBlock.timestamp_channel = None

        # update properties in the new data block
        self.dataBlock.channel_properties = copy.deepcopy(self.channel_config)
        # get sampling rate from amplifier
        self.dataBlock.sample_rate = self.Controler.SampleRate
        # set the recording modes
        self.dataBlock.recording_mode = self.recordingMode


    def process_update(self, params):
        self.createChannelSelection()

        self.send_event(ModuleEvent(self._object_name,
                                    EventType.STATUS,
                                    info = "%d ch"%(len(self.dataBlock.channel_properties)),
                                    status_field="Channels"))

        self.send_event(ModuleEvent(self._object_name, 
                                    EventType.STATUS,
                                    info = "%.0f Hz"%(self.dataBlock.sample_rate),
                                    status_field = "Rate"))

        return copy.copy(self.dataBlock)


    def process_output(self):
        t = time.perf_counter()
        self.dataBlock.performance_timer = 0
        self.dataBlock.performance_timer_max = 0
        self.recordtime = 0.0

        # check connection state and battery every 1s
        if (t - self.stateTimer) > 1.0 or self.stateTimer == 0:
            # read recording state and signal quality from device
            self.signalConnectionInfo.emit(self.Controler.DeviceConnectionInfo)
            self.stateTimer = t

        d, markers = self.Controler.Read()
        if d is None:
            return None

        dtBlock = (t - self.blockTimer) * 1000.0
        #print("%.0f ms"%dtBlock)
        self.blockTimer = t

        self.dataBlock.eeg_channels = d[0]
        self.dataBlock.trigger_channel = d[1]
        self.dataBlock.sample_channel = d[2]
        self.dataBlock.timestamp_channel = d[3]
        self.dataBlock.sample_counter += self.dataBlock.sample_channel.shape[1]

        # put it into the receiver queues
        eeg = copy.copy(self.dataBlock)

        # read and append markers
        self.markersToSend.extend(markers)
        for marker in self.markersToSend[:]:
            if marker[0] <= self.dataBlock.sample_channel[0,-1]:
                eeg.markers.append(EEG_Marker(type="Marker",
                                              description=marker[1],
                                              position=marker[0],
                                              channel=0))
                self.markersToSend.remove(marker)
        self.recordtime = time.perf_counter() - t

        return eeg

    
    def process_idle(self):
        # adjust idle time to record time
        idletime = max(0.03-self.recordtime, 0.01)
        time.sleep(idletime)    # suspend the worker thread


    def getXML(self):
        ''' Get module properties for XML configuration file
        @return: objectify XML element
        '''
        return None
        
    def setXML(self, xml):
        ''' Set module properties from XML configuration file
        @param xml: complete objectify XML configuration tree, 
        module will search for matching values
        '''
        pass

    def get_module_info(self):
        ''' Get information about this module for the about dialog
        @return: information string or None if info is not available
        '''
        return self.Controler.DeviceInfoString

'''
------------------------------------------------------------
ONLINE GUI
------------------------------------------------------------
'''

class OnlineConfigurationPane(QtWidgets.QFrame):
    signalModeChanged = QtCore.Signal(RecordingMode)
    signalConnect = QtCore.Signal(int)

    def __init__(self, amp, *args):
        super().__init__()
        self.amp = amp
       
        # make it nice ;-)
        self.setFrameShape(QtWidgets.QFrame.Panel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)

        # instantiate GUI elements
        self.groupBoxMode = QtWidgets.QGroupBox(self)
        self.groupBoxMode.setFlat(False)
        self.groupBoxMode.setCheckable(False)
        self.groupBoxMode.setObjectName("groupBoxMode")
        self.groupBoxMode.setTitle("LSL Amplifier")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/icons/play_green.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        
        self.pushButtonStartDefault = QtWidgets.QPushButton("Start", self.groupBoxMode)
        self.pushButtonStartDefault.setMinimumSize(QtCore.QSize(120, 40))
        self.pushButtonStartDefault.setStyleSheet("text-align: left; padding-left: 10px;")
        self.pushButtonStartDefault.setIcon(icon)
        self.pushButtonStartDefault.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStartDefault.setCheckable(True)
        self.pushButtonStartDefault.setAutoExclusive(True)
        self.pushButtonStartDefault.setAutoDefault(False)
        self.pushButtonStartDefault.setObjectName("pushButtonStartDefault")


        self.pushButtonStop = QtWidgets.QPushButton("Stop", self.groupBoxMode)
        self.pushButtonStop.setMinimumSize(QtCore.QSize(120, 40))
        self.pushButtonStop.setStyleSheet("text-align: left; padding-left: 10px;")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icons/stop_green.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButtonStop.setIcon(icon1)
        self.pushButtonStop.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStop.setCheckable(True)
        self.pushButtonStop.setAutoExclusive(True)
        self.pushButtonStop.setAutoDefault(False)
        self.pushButtonStop.setObjectName("pushButtonStop")

        self.lineEditConnectionState = QtWidgets.QLineEdit("Connection", self.groupBoxMode)
        self.lineEditConnectionState.setReadOnly(True)
        self.lineEditConnectionState.setAlignment(QtCore.Qt.AlignHCenter)

        self.pushButtonConnect = QtWidgets.QPushButton("Connect", self.groupBoxMode)
        self.pushButtonConnect.setObjectName("pushButtonConnect")
        self.pushButtonDisconnect = QtWidgets.QPushButton("Disconnect", self.groupBoxMode)
        self.pushButtonDisconnect.setObjectName("pushButtonDisconnect")


        # give us a layout and add widgets
        self.gridLayoutGroup = QtWidgets.QGridLayout(self.groupBoxMode)
        row = 0
        self.gridLayoutGroup.addWidget(self.pushButtonStartDefault, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.pushButtonStop, row, 1, 1, 1)
        row += 1
        self.gridLayoutGroup.addWidget(self.lineEditConnectionState, row, 0, 1, 2)
        row += 1
        self.gridLayoutGroup.addWidget(self.pushButtonConnect, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.pushButtonDisconnect, row, 1, 1, 1)
        row += 1

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.groupBoxMode, 0, 1, 1, 1)
       
        # set default values
        self.pushButtonStop.setChecked(True)
            
        # actions
        QtCore.QMetaObject.connectSlotsByName(self)
        self.amp.signalConnectionInfo.connect(self.setState)

        # set default values
        self.updateUI(RecordingMode.STOP)
        self.setState([(0, 0)])

            
    @QtCore.Slot()
    def on_pushButtonStop_clicked(self):
        mode = RecordingMode.STOP
        self.signalModeChanged.emit(mode)
    
    @QtCore.Slot()
    def on_pushButtonStartDefault_clicked(self):
        mode = RecordingMode.NORMAL
        self.signalModeChanged.emit(mode)
    
    @QtCore.Slot()
    def on_pushButtonConnect_clicked(self):
        self.setState([(-1, 0)])
        self.lineEditConnectionState.repaint()
        self.signalConnect.emit(1)
    
    @QtCore.Slot()
    def on_pushButtonDisconnect_clicked(self):
        self.signalConnect.emit(0)
   
    def setState(self, state_quality):
        if len(state_quality) > 0:
            state, quality = state_quality[0]
        else:
            state, quality = (0, 0)
        displayDevice = -1

        info =""
        palette = self.lineEditConnectionState.palette()
        if state == -1:
            info = "searching amplifiers ..."
            palette.setColor(QtGui.QPalette.Base, QtCore.Qt.cyan)
        elif state == ConnectionState.CS_DISCONNECTED:
            info = "amplifier disconnected"
            palette.setColor(QtGui.QPalette.Base, QtCore.Qt.gray)
        elif state == ConnectionState.CS_CONNECTED:
            info = "amplifier connected"
            if quality == SignalQuality.SQ_NOINFO:
                palette.setColor(QtGui.QPalette.Base, QtCore.Qt.gray)
            elif quality == SignalQuality.SQ_GOOD:
                palette.setColor(QtGui.QPalette.Base, QtCore.Qt.green)
            elif quality == SignalQuality.SQ_MEDIUM:
                palette.setColor(QtGui.QPalette.Base, QtCore.Qt.yellow)
            elif quality == SignalQuality.SQ_BAD:
                info = "amplifier out of range"
                palette.setColor(QtGui.QPalette.Base, QtCore.Qt.red)
            else:
                palette.setColor(QtGui.QPalette.Base, QtCore.Qt.gray)
        elif state == ConnectionState.CS_RECONNECT:
            info = "reconnect amplifier ..."
            palette.setColor(QtGui.QPalette.Base, QtCore.Qt.blue)
        else:
            palette.setColor(QtGui.QPalette.Base, QtCore.Qt.gray)
                
        if displayDevice >= 0:
            info = "%i - %s"%(displayDevice+1, info)                
        self.lineEditConnectionState.setText(info)
        self.lineEditConnectionState.setPalette(palette)
        self.enableAmplifierControls(state)
    
    def updateUI(self, mode):
        ''' Update user interface according to recording mode
        '''
        self.pushButtonStartDefault.setChecked(mode == RecordingMode.NORMAL)
        self.pushButtonStop.setChecked(mode == RecordingMode.STOP)

    def enableAmplifierControls(self, state):
        ''' enable or disable all amplifier control buttons, depending on the connection state
        '''
        enable = state != ConnectionState.CS_DISCONNECTED

        self.pushButtonConnect.setEnabled(not enable)
        self.pushButtonDisconnect.setEnabled(enable)
             
        self.pushButtonStartDefault.setEnabled(enable)
        self.pushButtonStop.setEnabled(enable)



'''
------------------------------------------------------------
CONFIGURATION GUI
------------------------------------------------------------
'''

class ConfigurationPane(QtWidgets.QFrame):
    configurationChanged = QtCore.Signal()
    def __init__(self, module, *args):
        super().__init__(*args)
        
        # reference to our parent module
        self.module = module
        
        # Set tab name
        self.setWindowTitle("LSL Amplifier")
        
        # make it nice
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        
        # base layout
        self.gridLayout = QtWidgets.QGridLayout(self)

        # signals
        self.signalTable = GenericTableWidget(Stretch=True)
        self.signalTable.setObjectName("signalTable")
        columns =  [
                    {'variable':'Type', 'header':'Channel Type'},
                    {'variable':'Unit', 'header':'Unit'},
                    {'variable':'Enable', 'header':'Enable', 'edit':True},
                    {'variable':'Label', 'header':'Label'},
                   ]

        cblist = {
                 }
    
        if len(self.module.Controler.AmplifierDevices) > 0:
            data = self.module.Controler.AmplifierDevices[0].Channels
        else:
            data = []
        self.signalTable.setData(data, columns, cblist)
        self.signalTable.resizeColumnsToContents()

        # use spacer items to align label and combox top-left
        vSpacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hSpacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hSpacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        # add all items to the layout
        row = 0
        self.gridLayout.addWidget(self.signalTable, row, 0, 1, 1)
        row += 1
        #self.gridLayout.addItem(vSpacerItem1, row, 0, 1, 1)

        # actions
        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.Slot()        
    def on_signalTable_dataChangedEvent(self):
        self.configurationChanged.emit()

