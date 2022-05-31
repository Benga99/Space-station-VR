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

from scipy import signal
from base.modbase import *
from operator import itemgetter


#from res import self
#from PyQt4 import QtGui

class FLT_Eeg(ModuleBase):
    ''' Low, high pass and notch filter
    '''

    def __init__(self, *args, **keys):
        ''' Constructor
        '''
        ModuleBase.__init__(self, name="EEG Filter", **keys)

        # XML parameter version
        # 1: initial version
        self.xmlVersion = 1
        
        self.data = None
        self.dataavailable = False
        self.params = None
        
        self.notchFilter = []           # notch filter array
        self.lpFilter = []              # lowpass filter array
        self.hpFilter = []              # highpass filter array
       
        # set default process values
        self.samplefreq = 50000.0
        self.filterorder = 2
        self.notchFrequency = 50.0      # notch filter frequency in Hz
        
        # set default properties
        self.setDefault()

    def setDefault(self):
        ''' Set all module parameters to default values
        '''
        # global filter values (for EEG-channels)
        self.lpGlobal = 0.0
        self.hpGlobal = 0.0
        self.notchGlobal = False
        # filter values for other channel types
        self.lpOther = 0.0
        self.hpOther = 0.0
        self.notchOther = False

    def get_configuration_pane(self):
        ''' Get the configuration pane if available.
        Qt widgets are not reusable, so we have to create it new every time
        '''
        return _ConfigurationPane(self)
       
    def _design_filter(self, frequency, type, slice):
        ''' Create filter settings for channel groups with equal filter parameters
        @param frequency: filter frequeny in Hz
        @param type: filter type, "low", "high" or "bandstop"
        @param slice: channel group indices
        @return: filter parameters and state vector
        '''
        if (frequency == 0.0) or (frequency > self.samplefreq/2.0):
            return None
        if type == "bandstop":
            # single notch
            cut1 = (frequency-1.0) / self.samplefreq * 2.0
            cut2 = (frequency+1.0) / self.samplefreq * 2.0
            b,a = signal.filter_design.iirfilter(2, [cut1, cut2], btype=type, ftype='butter') 
        else:
            cut = frequency / self.samplefreq * 2.0
            b,a = signal.filter_design.butter(self.filterorder, cut, btype=type) 
        zi = signal.lfiltic(b, a, (0.0,))
        czi = np.resize(zi, (slice.stop - slice.start, len(zi)))
        return {'slice':slice, 'a':a, 'b':b, 'zi':czi, 'frequency':frequency}

    def process_update(self, params):
        ''' Calculate filter parameters for updated channels
        '''
        # update the local reference
        if self.params == None:
            self.params = params
        else:
            # apply filter settings
            for ch in params.channel_properties:
                if ch.group == ChannelGroup.EEG:
                    ch.lowpass = self.lpGlobal
                    ch.highpass = self.hpGlobal
                    ch.notchfilter = self.notchGlobal
                else:
                    ch.lowpass = self.lpOther
                    ch.highpass = self.hpOther
                    ch.notchfilter = self.notchOther
            self.params = params
            

        # reset filter
        self.samplefreq = params.sample_rate
        self.lpFilter = []
        self.hpFilter = []
        self.notchFilter = []

        # nothing to filter
        if len(params.channel_properties) == 0:
            return params

        # create channel slices and filter for continuous notch filters
        notch = params.channel_properties[0].notchfilter
        slc = slice(0,1,1)
        for property in params.channel_properties[1::]:
            if property.notchfilter == notch:
                slc = slice(slc.start, slc.stop+1, 1)
            else:
                # design filter
                if notch: freq = self.notchFrequency 
                else: freq = 0.0
                filter = self._design_filter(freq, 'bandstop', slc)
                if filter != None:
                    self.notchFilter.append(filter)
                slc = slice(slc.stop, slc.stop+1, 1)
                notch = property.notchfilter
        if notch: freq = self.notchFrequency 
        else: freq = 0.0
        filter = self._design_filter(freq, 'bandstop', slc)
        if filter != None:
            self.notchFilter.append(filter)
            
        # create channel slices and filter for continuous unique lowpass filter frequencies
        freq = params.channel_properties[0].lowpass
        slc = slice(0,1,1)
        for property in params.channel_properties[1::]:
            if property.lowpass == freq:
                slc = slice(slc.start, slc.stop+1, 1)
            else:
                # design filter
                filter = self._design_filter(freq, 'low', slc)
                if filter != None:
                    self.lpFilter.append(filter)
                slc = slice(slc.stop, slc.stop+1, 1)
                freq = property.lowpass
        filter = self._design_filter(freq, 'low', slc)
        if filter != None:
            self.lpFilter.append(filter)
            
        # create channel slices and filter for continuous unique highpass filter frequencies
        freq = params.channel_properties[0].highpass
        slc = slice(0,1,1)
        for property in params.channel_properties[1::]:
            if property.highpass == freq:
                slc = slice(slc.start, slc.stop+1, 1)
            else:
                # design filter
                filter = self._design_filter(freq, 'high', slc)
                if filter != None:
                    self.hpFilter.append(filter)
                slc = slice(slc.stop, slc.stop+1, 1)
                freq = property.highpass
        filter = self._design_filter(freq, 'high', slc)
        if filter != None:
            self.hpFilter.append(filter)

        # propagate down
        return params
        
    def process_input(self, datablock):
        ''' Filter all channel groups
        '''
        self.dataavailable = True
        self.data = datablock

        # don't filter impedance values 
        if self.data.recording_mode == RecordingMode.IMPEDANCE:
            return

        # replace channel filter configuration within the data block with our modified configuration
        for channel in range(len(self.data.channel_properties)):
            self.data.channel_properties[channel].lowpass = self.params.channel_properties[channel].lowpass
            self.data.channel_properties[channel].highpass = self.params.channel_properties[channel].highpass
            self.data.channel_properties[channel].notchfilter = self.params.channel_properties[channel].notchfilter
        
        # highpass filter
        for flt in self.hpFilter:
            self.data.eeg_channels[flt['slice']],flt['zi'] = \
                signal.lfilter(flt['b'], flt['a'], 
                               self.data.eeg_channels[flt['slice']], zi=flt['zi'])
            
        # lowpass filter
        for flt in self.lpFilter:
            self.data.eeg_channels[flt['slice']],flt['zi'] = \
                signal.lfilter(flt['b'], flt['a'], 
                               self.data.eeg_channels[flt['slice']], zi=flt['zi'])
       
        # notch filter
        for flt in self.notchFilter:
            self.data.eeg_channels[flt['slice']],flt['zi'] = \
                signal.lfilter(flt['b'], flt['a'], 
                               self.data.eeg_channels[flt['slice']], zi=flt['zi'])
            
            
    
    def process_output(self):
        if not self.dataavailable:
            return None
        self.dataavailable = False
        return self.data

    def getXML(self):
        ''' Get module properties for XML configuration file
        @return: objectify XML element::
            e.g.
            <EegFilter instance="0" version="1">
                <notch_frequency>50.0</path>
                ...
            </EegFilter>
        '''
        E = objectify.E
        cfg = E.EegFilter(E.notch_frequency(self.notchFrequency),
                          E.lp_global(self.lpGlobal),
                          E.hp_global(self.hpGlobal),
                          E.notch_global(self.notchGlobal),
                          E.lp_other(self.lpGlobal),
                          E.hp_other(self.hpGlobal),
                          E.notch_other(self.notchGlobal),
                          version=str(self.xmlVersion),
                          instance=str(self._instance),
                          module="filter")
        return cfg
        
        
    def setXML(self, xml):
        ''' Set module properties from XML configuration file
        @param xml: complete objectify XML configuration tree, 
        module will search for matching values
        '''
        # search my configuration data
        storages = xml.xpath("//EegFilter[@module='filter' and @instance='%i']"%(self._instance) )
        if len(storages) == 0:
            # configuration data not found, set default values
            self.notchFrequency = 50.0
            return      
        
        # we should have only one instance from this type
        cfg = storages[0]   
        
        # check version, has to be lower or equal than current version
        version = cfg.get("version")
        if (version == None) or (int(version) > self.xmlVersion):
            self.send_event(ModuleEvent(self._object_name, EventType.ERROR, "XML Configuration: wrong version"))
            return
        version = int(version)
        
        # get the values
        try:
            self.notchFrequency = cfg.notch_frequency.pyval
            if version > 1:
                # get global filter values
                self.notchGlobal = cfg.notch_global.pyval
                self.lpGlobal = cfg.lp_global.pyval
                self.hpGlobal = cfg.hp_global.pyval
                # get other channel filter values
                self.notchOther = cfg.notch_other.pyval
                self.lpOther = cfg.lp_other.pyval
                self.hpOther = cfg.hp_other.pyval
            
        except Exception as e:
            self.send_exception(e, severity=ErrorSeverity.NOTIFY)


'''
------------------------------------------------------------
FILTER MODULE CONFIGURATION PANE
------------------------------------------------------------
'''

class _ConfigurationPane(QtWidgets.QFrame):
    ''' Module configuration pane
    '''
    def __init__(self, filter, *args):
        ''' Constructor
        '''
        super().__init__(*args)
        self.inInit = True
        self.setupUi()

        # setup content
        self.filter = filter

        # notch frequency
        self.notchlist = ['50', '60']
        self.comboBox_Notch.addItems(self.notchlist)
        idx = self._get_cb_index(self.comboBox_Notch, self.filter.notchFrequency)
        if idx >= 0:
            self.comboBox_Notch.setCurrentIndex(idx)

        # EEG lowpass filter
        self.lowpasslist = ['off', '10', '20', '30', '50', '100', '200', '500', '1000', '2000']
        self.comboBoxEegLowpass.addItems(self.lowpasslist)
        idx = self._get_cb_index(self.comboBoxEegLowpass, self.filter.lpGlobal)
        if idx >= 0:
            self.comboBoxEegLowpass.setCurrentIndex(idx)

        # AUX lowpass filter
        self.comboBoxAuxLowpass.addItems(self.lowpasslist)
        idx = self._get_cb_index(self.comboBoxAuxLowpass, self.filter.lpOther)
        if idx >= 0:
            self.comboBoxAuxLowpass.setCurrentIndex(idx)
        
        # EEG highpass filter
        self.highpasslist = ['off','0.01', '0.02', '0.05', '0.1', '0.2', '0.5', '1', '2', '5', '10']
        self.comboBoxEegHighpass.addItems(self.highpasslist)
        idx = self._get_cb_index(self.comboBoxEegHighpass, self.filter.hpGlobal)
        if idx >= 0:
            self.comboBoxEegHighpass.setCurrentIndex(idx)

        # AUX highpass filter
        self.comboBoxAuxHighpass.addItems(self.highpasslist)
        idx = self._get_cb_index(self.comboBoxAuxHighpass, self.filter.hpOther)
        if idx >= 0:
            self.comboBoxAuxHighpass.setCurrentIndex(idx)

        # EEG notch filter
        self.checkBoxEegNotch.setChecked(self.filter.notchGlobal)

        # AUX notch filter
        self.checkBoxAuxNotch.setChecked(self.filter.notchOther)

        self.inInit = False


    def setupUi(self):
        self.setObjectName("frmFilterConfig")
        self.resize(690, 423)
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Raised)
        self.setWindowTitle("Filter")

        self.gridLayout_main = QtWidgets.QGridLayout(self)
        self.gridLayout_main.setVerticalSpacing(10)
        self.gridLayout_main.setObjectName("gridLayout_main")

        self.gridLayout_filters = QtWidgets.QGridLayout()
        self.gridLayout_filters.setSpacing(15)
        self.gridLayout_filters.setObjectName("gridLayout_filters")

        # Header
        self.label_Channels = QtWidgets.QLabel("Channels", self)
        self.gridLayout_filters.addWidget(self.label_Channels, 0, 0, 1, 1)

        self.label_Lowpass = QtWidgets.QLabel("High Cutoff [Hz]", self)
        self.gridLayout_filters.addWidget(self.label_Lowpass, 0, 1, 1, 1)

        self.label_Highpass = QtWidgets.QLabel("Low Cutoff [Hz]", self)
        self.gridLayout_filters.addWidget(self.label_Highpass, 0, 2, 1, 1)

        self.label_Notch = QtWidgets.QLabel("Notchfilter", self)
        self.gridLayout_filters.addWidget(self.label_Notch, 0, 3, 1, 1)

        # EEG channels
        self.label_EegChannels = QtWidgets.QLabel("EEG", self)
        self.gridLayout_filters.addWidget(self.label_EegChannels, 1, 0, 1, 1)

        self.comboBoxEegLowpass = QtWidgets.QComboBox(self)
        self.comboBoxEegLowpass.setObjectName("comboBoxEegLowpass")
        self.gridLayout_filters.addWidget(self.comboBoxEegLowpass, 1, 1, 1, 1)

        self.comboBoxEegHighpass = QtWidgets.QComboBox(self)
        self.comboBoxEegHighpass.setObjectName("comboBoxEegHighpass")
        self.gridLayout_filters.addWidget(self.comboBoxEegHighpass, 1, 2, 1, 1)

        self.checkBoxEegNotch = QtWidgets.QCheckBox(self)
        self.checkBoxEegNotch.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBoxEegNotch.setObjectName("checkBoxEegNotch")
        self.checkBoxEegNotch.setText("on")
        self.gridLayout_filters.addWidget(self.checkBoxEegNotch, 1, 3, 1, 1)

        # AUX channels
        self.label_AuxChannels = QtWidgets.QLabel("AUX", self)
        self.gridLayout_filters.addWidget(self.label_AuxChannels, 2, 0, 1, 1)

        self.comboBoxAuxLowpass = QtWidgets.QComboBox(self)
        self.comboBoxAuxLowpass.setObjectName("comboBoxAuxLowpass")
        self.gridLayout_filters.addWidget(self.comboBoxAuxLowpass, 2, 1, 1, 1)

        self.comboBoxAuxHighpass = QtWidgets.QComboBox(self)
        self.comboBoxAuxHighpass.setObjectName("comboBoxAuxHighpass")
        self.gridLayout_filters.addWidget(self.comboBoxAuxHighpass, 2, 2, 1, 1)

        self.checkBoxAuxNotch = QtWidgets.QCheckBox(self)
        self.checkBoxAuxNotch.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkBoxAuxNotch.setObjectName("checkBoxAuxNotch")
        self.checkBoxAuxNotch.setText("on")
        self.gridLayout_filters.addWidget(self.checkBoxAuxNotch, 2, 3, 1, 1)

        vSpacerItem3 = QtWidgets.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_filters.addItem(vSpacerItem3, 3, 0, 1, 4)

        self.gridLayout_main.addLayout(self.gridLayout_filters, 0, 0, 1, 1)

        hSpacerItem = QtWidgets.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_main.addItem(hSpacerItem, 0, 1, 1, 1)

        vSpacerItem = QtWidgets.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_main.addItem(vSpacerItem, 1, 0, 1, 3)

        # Notch frequency
        self.gridLayout_notch = QtWidgets.QGridLayout()
        self.gridLayout_notch.setHorizontalSpacing(10)
        self.gridLayout_notch.setVerticalSpacing(6)
        self.gridLayout_notch.setObjectName("gridLayout_notch")

        self.label_notchgrp = QtGui.QLabel("Notchfilter", self)
        self.gridLayout_notch.addWidget(self.label_notchgrp, 0, 0, 1, 1)

        self.label_notchfrq = QtWidgets.QLabel("Frequency", self)
        self.gridLayout_notch.addWidget(self.label_notchfrq, 1, 0, 1, 1)

        self.label_notchfrq_unit = QtWidgets.QLabel("[Hz]", self)
        self.gridLayout_notch.addWidget(self.label_notchfrq_unit, 1, 2, 1, 1)

        self.comboBox_Notch = QtWidgets.QComboBox(self)
        self.comboBox_Notch.setMaxVisibleItems(2)
        self.comboBox_Notch.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.comboBox_Notch.setObjectName("comboBoxNotchFrequency")
        self.gridLayout_notch.addWidget(self.comboBox_Notch, 1, 1, 1, 1)

        vSpacerItem2 = QtWidgets.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_notch.addItem(vSpacerItem2, 2, 0, 1, 1)

        self.gridLayout_main.addLayout(self.gridLayout_notch, 0, 2, 1, 1)

        QtCore.QMetaObject.connectSlotsByName(self)

    def _get_cb_index(self, cb, value):
        ''' Get closest matching combobox index
        @param cb: combobox object 
        @param value: float lookup value 
        '''
        itemlist = []
        for i in range(cb.count()):
            try:
                val = float(cb.itemText(i))
            except:
                val = 0
            itemlist.append( (i, val) )
        idx = itemlist[-1][0]
        for item in sorted(itemlist, key=itemgetter(1)):
            if item[1] >= value - 0.0001:
                idx = item[0]
                break
        return idx
    
    @QtCore.Slot(str)
    def on_comboBoxNotchFrequency_currentIndexChanged(self, value):
        if self.inInit: return
        try:
            self.filter.notchFrequency = float(value)
        except:
            self.filter.notchFrequency = 0

    @QtCore.Slot(int)
    def on_checkBoxEegNotch_stateChanged(self, value):
        if self.inInit: return
        self.filter.notchGlobal = (value == QtCore.Qt.Checked)

    @QtCore.Slot(str)
    def on_comboBoxEegLowpass_currentIndexChanged(self, value):
        if self.inInit: return
        try:
            self.filter.lpGlobal = float(value)
        except:
            self.filter.lpGlobal = 0


    @QtCore.Slot(str)
    def on_comboBoxEegHighpass_currentIndexChanged(self, value):
        if self.inInit: return
        try:
            self.filter.hpGlobal = float(value)
        except:
            self.filter.hpGlobal = 0


    @QtCore.Slot(int)
    def on_checkBoxAuxNotch_stateChanged(self, value):
        if self.inInit: return
        self.filter.notchOther = (value == QtCore.Qt.Checked)

    @QtCore.Slot(str)
    def on_comboBoxAuxLowpass_currentIndexChanged(self, value):
        if self.inInit: return
        try:
            self.filter.lpOther = float(value)
        except:
            self.filter.lpOther = 0


    @QtCore.Slot(str)
    def on_comboBoxAuxHighpass_currentIndexChanged(self, value):
        if self.inInit: return
        try:
            self.filter.hpOther = float(value)
        except:
            self.filter.hpOther = 0


