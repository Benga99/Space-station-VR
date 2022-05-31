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

class SignalGenerator(ModuleBase):
    ''' Simple signal generator
    '''
    def __init__(self, usethread = True, queuesize = 20, name = 'SignalGenerator', instance = 0):
        super().__init__(usethread, queuesize, name, instance)
        
        #self.xmlVersion = 1
        #self.xmlVersion = 2     # noise added
        self.xmlVersion = 3      # unit added

        self.setDefault()

        # create online configuration pane
        self.onlineConfiguration = OnlineConfigurationPane(self)
        self.onlineConfiguration.modeChanged.connect(self.recordingModeChanged)
        self.recordingMode = RecordingMode.STOP

        # impedance interval timer
        self.impedanceTimer = time.perf_counter()

    def setDefault(self):
        self.samplingRate = 10000
        self.signals = [
                         SignalConfiguration(ChannelGroup.EEG, 32),
                         SignalConfiguration(ChannelGroup.BIP, 0),
                         SignalConfiguration(ChannelGroup.AUX, 2)
                       ]

    def recordingModeChanged(self, newMode):
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

    def configurationChanged(self):
        self.update_receivers()

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
        cfgPane.configurationChanged.connect(self.configurationChanged)
        return cfgPane

    def process_start(self):
        # start acquisistion
        self.update_receivers()
        if len(self.dataBlock.channel_properties) == 0:
            raise ModuleError(self._object_name, "no input channels selected!")

        # set start time on first call
        self.start_time = datetime.datetime.now()
        self.sample_timer = time.perf_counter()

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


    def process_update(self, params):
        eegChannels = 0
        auxChannels = 0
        groups = []
        units = []
        self.impedanceChannelSelection = []
        for signal in self.signals:
            if signal.channelGroup == ChannelGroup.EEG or signal.channelGroup == ChannelGroup.BIP:
                eegChannels += signal.numberOfChannels
            else:
                auxChannels += signal.numberOfChannels
            groups.extend([signal.channelGroup]*signal.numberOfChannels)
            units.extend([signal.signalUnit]*signal.numberOfChannels)
        self.dataBlock = EEG_DataBlock(eeg=eegChannels, aux=auxChannels)
        for c in range(len(self.dataBlock.channel_properties)):
            ch = self.dataBlock.channel_properties[c]
            group = groups[c]
            if group == ChannelGroup.EEG or group == ChannelGroup.BIP:
                ch.inputgroup = ChannelGroup.EEG
                # define which channels contains which impedance values
                self.impedanceChannelSelection.append(c)
                self.dataBlock.eeg_channels[c, ImpedanceIndex.DATA] = 1
                self.dataBlock.eeg_channels[c,ImpedanceIndex.GND] = 1
                self.dataBlock.eeg_channels[c,ImpedanceIndex.REF] = 1
                self.dataBlock.eeg_channels[c,ImpedanceIndex.MODULE] = 0
            else:
                ch.inputgroup = ChannelGroup.AUX
            ch.group = group
            ch.unit = units[c]
            ch.name = "%s-%d"%(ChannelGroup.Name[group], c+1)
            ch.input = c + 1
            ch.modulechannel = c + 1

        self.dataBlock.sample_rate = self.samplingRate
        self.dataBlock.recording_mode = self.recordingMode
        self.dataBlock.sample_counter = 0

        # create a trigger channel
        self.dataBlock.digitalChannelDescription = []
        description = {'Type':'TRG', 'Function':'Trigger IN', 'Amplifier':0, 'Module':0,
                        'WriteMask':0, 'ReadMask':0xFF}
        self.dataBlock.digitalChannelDescription.append(description)



        self.send_event(ModuleEvent(self._object_name,
                                    EventType.STATUS,
                                    info = "%d ch"%(len(self.dataBlock.channel_properties)),
                                    status_field="Channels"))

        self.send_event(ModuleEvent(self._object_name, 
                                    EventType.STATUS,
                                    info = "%.0f Hz"%(self.dataBlock.sample_rate),
                                    status_field = "Rate"))

        return copy.copy(self.dataBlock)


    def process_impedance(self):
        ''' Get the impedance values from amplifier
        and return the eeg data block
        '''
        # send values only once per second
        t = time.perf_counter()
        if (t - self.impedanceTimer) < 1.0:
            return None
        self.impedanceTimer = t
        
        # invalidate the old impedance data list
        self.dataBlock.impedances = []
        
        # copy impedance values to data array
        self.dataBlock.eeg_channels = np.zeros((len(self.dataBlock.channel_properties), 10), 'd')
        self.dataBlock.eeg_channels[self.impedanceChannelSelection, ImpedanceIndex.GND] = 3300
        self.dataBlock.eeg_channels[self.impedanceChannelSelection, ImpedanceIndex.REF] = np.array(self.impedanceChannelSelection) * 2000 + 1000
        self.dataBlock.eeg_channels[self.impedanceChannelSelection, ImpedanceIndex.DATA] = np.array(self.impedanceChannelSelection) * 1000 + 1000
        self.dataBlock.eeg_channels[self.impedanceChannelSelection, ImpedanceIndex.MODULE] = 0
        
        # dummy values for trigger and sample counter
        self.dataBlock.trigger_channel = np.zeros((1, 10), np.uint32)
        self.dataBlock.sample_channel = np.zeros((1, 10), np.uint32)

        # set recording time
        self.dataBlock.block_time = datetime.datetime.now()
                    
        # put it into the receiver queues
        eeg = copy.copy(self.dataBlock)
        return eeg





    def process_output(self):
        t = time.perf_counter()
        self.dataBlock.performance_timer = 0
        self.dataBlock.performance_timer_max = 0
        self.recordtime = 0.0

        # get impedance values
        if self.recordingMode == RecordingMode.IMPEDANCE:
            return self.process_impedance()


        # calculate the number of samples to read
        numsamples = int((t - self.sample_timer) * self.dataBlock.sample_rate)
        self.sample_timer = t

        if numsamples <= 0:
            return None

        # get the signals
        lastSC = self.dataBlock.sample_counter
        self.dataBlock.sample_channel = np.array([np.linspace(lastSC, lastSC+numsamples, num=numsamples, endpoint=False, dtype=np.integer)])
        self.dataBlock.sample_counter += numsamples
        self.dataBlock.eeg_channels = np.zeros((len(self.dataBlock.channel_properties), numsamples), 'd')
        self.dataBlock.trigger_channel = np.zeros((1, numsamples), np.uint32)
        self.dataBlock.markers = []

        ts = self.dataBlock.sample_channel[0] / self.dataBlock.sample_rate
        dt = 1.0 / self.dataBlock.sample_rate
        group = None
        idx = 0
        
        # create the signals, trigger and noise
        channelGroups = [p.group for p in self.dataBlock.channel_properties]
        groups, groupIndices = np.unique(channelGroups, return_inverse=True)
        signals = np.array([self.getSignal(ts, group, dt) for group in groups])
        # add the signals
        s = np.stack(signals[groupIndices][:,0])
        self.dataBlock.eeg_channels = s
        # add trigger channel
        for g in range(len(groups)):
            self.dataBlock.trigger_channel[0] |= signals[g,1]
        # add noise
        sigma = np.stack(signals[groupIndices][:,2])
        noise = np.random.normal(0.0, sigma, (s.shape[1], s.shape[0]))
        self.dataBlock.eeg_channels += noise.transpose()

        # calculate date and time for the first sample of this block in s
        sampletime = self.dataBlock.sample_channel[0][0] / self.dataBlock.sample_rate
        self.dataBlock.block_time = self.start_time + datetime.timedelta(seconds=sampletime)

        # put it into the receiver queues
        eeg = copy.copy(self.dataBlock)
        self.recordtime = time.perf_counter() - t
        #print(self.recordtime)
        return eeg

    
    def process_idle(self):
        # adjust idle time to record time
        idletime = max(0.06-self.recordtime, 0.02)
        time.sleep(idletime)    # suspend the worker thread for 60ms


    def getSignal(self, t, channelGroup, dt):
        s = np.zeros_like(t)
        trg = np.zeros(len(t), np.uint32)
        noise = 0.0
        for signal in self.signals:
            if signal.channelGroup == channelGroup:
                amplitude = signal.signalAmplitude_mV * 1e3
                offset = signal.signalOffset_mV * 1e3
                if signal.signalShape == "Sine":
                    s = np.sin(t * 2.0 * np.pi * signal.signalFrequency) * amplitude + offset
                    #break
                if signal.signalShape == "Rectangle":
                    s = scpsignal.square(t * 2.0 * np.pi * signal.signalFrequency) * amplitude + offset
                    #break
                noise = signal.signalNoise_mV * 1e3
                #if noise > 0.0:
                #    mu = 0.0
                #    sigma = noise
                #    s += np.random.normal(mu, sigma, len(t))
                T = 1.0 / signal.signalFrequency
                ti = np.nonzero((t % T) <= T/2)
                trg[ti] = 1 << channelGroup
        return s, trg, noise


    def getXML(self):
        ''' Get module properties for XML configuration file
        @return: objectify XML element
        '''
        E = objectify.E
        signals = E.Signals()
        for s in self.signals:
            signals.append(s.getXML())

        cfg = E.SignalGenerator(
                            E.rate(self.samplingRate),
                            signals,
                            version=str(self.xmlVersion),
                            instance=str(self._instance),
                            module="source"
                            )
        return cfg
        
    def setXML(self, xml):
        ''' Set module properties from XML configuration file
        @param xml: complete objectify XML configuration tree, 
        module will search for matching values
        '''
        # search my configuration data
        root = xml.xpath("//SignalGenerator[@module='source' and @instance='%i']"%(self._instance))
        if len(root) == 0:
            # configuration data not found, leave everything unchanged
            return      
        
        # we should have only one display instance from this type
        cfg = root[0]   
        
        # check version, has to be lower or equal than current version
        version = cfg.get("version")
        if (version == None) or (int(version) > self.xmlVersion):
            self.send_event(ModuleEvent(self._object_name, EventType.ERROR, "XML Configuration: wrong version"))
            return
        version = int(version)
        
        # get the values
        try:
            self.samplingRate = cfg.rate.pyval
            sl = []
            for signal in cfg.Signals.iterchildren():
                s = SignalConfiguration(0,1)
                s.setXML(signal, version)
                sl.append(s)
            self.signals = sl
        except Exception as e:
            self.send_exception(e, severity=ErrorSeverity.NOTIFY)


class SignalConfiguration():
    def __init__(self, channelGroup, numberOfChannels):
        self.channelGroup = channelGroup
        self.numberOfChannels = numberOfChannels
        self.signalShape = "Sine"
        self.signalFrequency = 10.0
        self.signalAmplitude_mV = 0.1
        self.signalOffset_mV = 0.0
        self.signalNoise_mV = 0.0
        self.signalUnit = "microvolts"

    def getXML(self):
        E = objectify.E
        s = E.Signal(
                E.group(self.channelGroup),
                E.channels(self.numberOfChannels),
                E.shape(self.signalShape),
                E.frequency(self.signalFrequency),
                E.amplitude(self.signalAmplitude_mV),
                E.offset(self.signalOffset_mV),
                E.noise(self.signalNoise_mV),
                E.unit(self.signalUnit)
                )
        return s

    def setXML(self, cfg, version):
        self.channelGroup = cfg.group.pyval
        self.numberOfChannels = cfg.channels.pyval
        self.signalShape = cfg.shape.pyval
        self.signalFrequency = cfg.frequency.pyval
        self.signalAmplitude_mV = cfg.amplitude.pyval
        self.signalOffset_mV = cfg.offset.pyval
        if version >= 2:
            self.signalNoise_mV = cfg.noise.pyval
        if version >= 3:
            self.signalUnit = cfg.unit.pyval



'''
------------------------------------------------------------
ONLINE GUI
------------------------------------------------------------
'''

class OnlineConfigurationPane(QtWidgets.QFrame):
    modeChanged = QtCore.Signal(RecordingMode)

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
        self.groupBoxMode.setTitle("Signal Generator")

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon.addPixmap(QtGui.QPixmap(":/icons/play_green.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        
        self.pushButtonStartDefault = QtWidgets.QPushButton("Default\nMode", self.groupBoxMode)
        self.pushButtonStartDefault.setMinimumSize(QtCore.QSize(120, 40))
        self.pushButtonStartDefault.setStyleSheet("text-align: left; padding-left: 10px;")
        self.pushButtonStartDefault.setIcon(icon)
        self.pushButtonStartDefault.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStartDefault.setCheckable(True)
        self.pushButtonStartDefault.setAutoExclusive(True)
        self.pushButtonStartDefault.setAutoDefault(False)
        self.pushButtonStartDefault.setObjectName("pushButtonStartDefault")

        self.pushButtonStartImpedance = QtWidgets.QPushButton("Impedance\nMode", self.groupBoxMode)
        self.pushButtonStartImpedance.setMinimumSize(QtCore.QSize(120, 40))
        self.pushButtonStartImpedance.setStyleSheet("text-align: left; padding-left: 10px;")
        self.pushButtonStartImpedance.setIcon(icon)
        self.pushButtonStartImpedance.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStartImpedance.setCheckable(True)
        self.pushButtonStartImpedance.setAutoExclusive(True)
        self.pushButtonStartImpedance.setAutoDefault(False)
        self.pushButtonStartImpedance.setObjectName("pushButtonStartImpedance")

        self.pushButtonStartTest = QtWidgets.QPushButton("Test\nMode", self.groupBoxMode)
        self.pushButtonStartTest.setMinimumSize(QtCore.QSize(120, 40))
        self.pushButtonStartTest.setStyleSheet("text-align: left; padding-left: 10px;")
        self.pushButtonStartTest.setIcon(icon)
        self.pushButtonStartTest.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStartTest.setCheckable(True)
        self.pushButtonStartTest.setAutoExclusive(True)
        self.pushButtonStartTest.setAutoDefault(False)
        self.pushButtonStartTest.setObjectName("pushButtonStartTest")

        self.pushButtonStop = QtWidgets.QPushButton("Stop", self.groupBoxMode)
        self.pushButtonStop.setMinimumSize(QtCore.QSize(120, 40))
        #self.pushButtonStop.setStyleSheet("text-align: left; padding-left: 10px;")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/icons/stop_green.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.pushButtonStop.setIcon(icon1)
        self.pushButtonStop.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonStop.setCheckable(True)
        self.pushButtonStop.setAutoExclusive(True)
        self.pushButtonStop.setAutoDefault(False)
        self.pushButtonStop.setObjectName("pushButtonStop")


        # give us a layout and add widgets
        row = 0
        self.gridLayoutGroup = QtWidgets.QGridLayout(self.groupBoxMode)
        self.gridLayoutGroup.addWidget(self.pushButtonStartDefault, row, 0, 1, 2)
        row += 1
        self.gridLayoutGroup.addWidget(self.pushButtonStartTest, row, 0, 1, 1)
        self.gridLayoutGroup.addWidget(self.pushButtonStartImpedance, row, 1, 1, 1)
        row += 1
        self.gridLayoutGroup.addWidget(self.pushButtonStop, row, 0, 1, 2)
        row += 1

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.addWidget(self.groupBoxMode, 0, 1, 1, 1)
       
        # set default values
        self.pushButtonStop.setChecked(True)
            
        # actions
        QtCore.QMetaObject.connectSlotsByName(self)

        # set default values
        self.updateUI(RecordingMode.STOP)
            
    @QtCore.Slot()
    def on_pushButtonStop_clicked(self):
        mode = RecordingMode.STOP
        self.modeChanged.emit(mode)
    
    @QtCore.Slot()
    def on_pushButtonStartDefault_clicked(self):
        mode = RecordingMode.NORMAL
        self.modeChanged.emit(mode)
    
    @QtCore.Slot()
    def on_pushButtonStartImpedance_clicked(self):
        mode = RecordingMode.IMPEDANCE
        self.modeChanged.emit(mode)
    
    @QtCore.Slot()
    def on_pushButtonStartTest_clicked(self):
        mode = RecordingMode.TEST
        self.modeChanged.emit(mode)
    
    
    def updateUI(self, mode):
        ''' Update user interface according to recording mode
        '''
        self.pushButtonStartDefault.setChecked(mode == RecordingMode.NORMAL)
        self.pushButtonStartTest.setChecked(mode == RecordingMode.TEST)
        self.pushButtonStartImpedance.setChecked(mode == RecordingMode.IMPEDANCE)
        self.pushButtonStop.setChecked(mode == RecordingMode.STOP)

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
        self.setWindowTitle("Signal Generator")
        
        # make it nice
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        
        # base layout
        self.gridLayout = QtWidgets.QGridLayout(self)

        # sampling rate
        self.labelSamplingRate = QtWidgets.QLabel("Sampling rate", self)

        self.cbSamplingRate = QtWidgets.QComboBox(self)
        self.cbSamplingRate.setObjectName("cbSamplingRate")
        self.cbSamplingRate.addItem("100 Hz", 100)
        self.cbSamplingRate.addItem("200 Hz", 200)
        self.cbSamplingRate.addItem("250 Hz", 250)
        self.cbSamplingRate.addItem("500 Hz", 500)
        self.cbSamplingRate.addItem("1000 Hz", 1000)
        self.cbSamplingRate.addItem("2000 Hz", 2000)
        self.cbSamplingRate.addItem("5000 Hz", 5000)
        self.cbSamplingRate.addItem("10 kHz", 10000)
        self.cbSamplingRate.addItem("20 kHz", 20000)

        # signals
        self.signalTable = GenericTableWidget(Stretch=False)
        self.signalTable.setObjectName("signalTable")
        columns =  [
                    {'variable':'channelGroup', 'header':'Group', 'edit':True, 'editor':'combobox', 'indexed':True},
                    {'variable':'numberOfChannels', 'header':'Channels', 'edit':True, 'editor':'default', 'min':0, 'max':128},
                    {'variable':'signalShape', 'header':'Shape', 'edit':True, 'editor':'combobox'},
                    {'variable':'signalFrequency', 'header':'Frequency\n[Hz]', 'edit':True, 'editor':'default', 'min':0.5, 'max':1000.0},
                    {'variable':'signalAmplitude_mV', 'header':'Amplitude\n[mV]', 'edit':True, 'editor':'default', 'min':0.0, 'max':1000.0, 'step':0.1},
                    {'variable':'signalOffset_mV', 'header':'Offset\n[mV]', 'edit':True, 'editor':'default', 'min':-1000.0, 'max':1000.0, 'step':0.1},
                    {'variable':'signalNoise_mV', 'header':'Noise\n[mV]', 'edit':True, 'editor':'default', 'min':0.0, 'max':1000.0, 'step':0.1},
                    {'variable':'signalUnit', 'header':'Unit', 'edit':True, 'editor':'default'},
                   ]

        cblist = {
                  'channelGroup':ChannelGroup.Name,
                  'signalShape':["Sine","Rectangle"],
                 }
    
        self.signalTable.setData(self.module.signals, columns, cblist)
        self.signalTable.resizeColumnsToContents()

        # use spacer items to align label and combox top-left
        vSpacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        hSpacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        hSpacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        
        # add all items to the layout
        row = 0
        self.gridLayout.addWidget(self.labelSamplingRate, row, 0)
        self.gridLayout.addWidget(self.cbSamplingRate, row, 1)
        self.gridLayout.addItem(hSpacerItem1, row, 2, 1, 1)
        row += 1
        self.gridLayout.addWidget(self.signalTable, row, 0, 1, 3)
        self.gridLayout.addItem(hSpacerItem2, row, 3, 1, 1)
        row += 1
        self.gridLayout.addItem(vSpacerItem1, row, 0, 1, 1)

        # set initial values from parent module
        idx = self.cbSamplingRate.findData(self.module.samplingRate)
        self.cbSamplingRate.setCurrentIndex(idx)


        # actions
        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.Slot(int)        
    def on_cbSamplingRate_currentIndexChanged(self, index):
        self.module.samplingRate = self.cbSamplingRate.currentData()
        self.configurationChanged.emit()
        
    @QtCore.Slot()        
    def on_signalTable_dataChangedEvent(self):
        self.configurationChanged.emit()
