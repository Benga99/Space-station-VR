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

import time
from PySide2 import QtCore, QtGui, QtWidgets
from pylsl import StreamInlet, ContinuousResolver, IRREGULAR_RATE
from amplifiers.lsl.lsldevice import *

class LSL_Controler:
    def __init__(self, *args, **kwargs):
        #self.Resolver = ContinuousResolver(forget_after=5.0)
        self.AmplifierDevices = []
        self.MarkerDevices = []


    def ConnectStreams(self):
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        self.Resolver = ContinuousResolver(forget_after=5.0)
        QtWidgets.QApplication.restoreOverrideCursor()
        dlg = StreamSelectionDialog(self.Resolver)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
            self.DisconnectStreams()
            try:
                for streamInfo in dlg.GetSelection():
                    # TODO: support more than one regular stream
                    if streamInfo.nominal_srate() != IRREGULAR_RATE and len(self.AmplifierDevices) == 0:
                        d = LSL_Device()
                        if d.Create(streamInfo):
                            self.AmplifierDevices.append(d)
                    elif streamInfo.nominal_srate() == IRREGULAR_RATE:
                        d = LSL_Device(isMarkerDevice=True)
                        if d.Create(streamInfo):
                            self.MarkerDevices.append(d)
            except Exception as e:
                QtWidgets.QApplication.restoreOverrideCursor()
                self.Resolver = None
                raise(e)

            QtWidgets.QApplication.restoreOverrideCursor()
        self.Resolver = None

    def DisconnectStreams(self):
        for stream in self.AmplifierDevices:
            stream.Stop()
        for stream in self.MarkerDevices:
            stream.Stop()
        self.AmplifierDevices = []
        self.MarkerDevices = []

    def Start(self):
        for d in self.AmplifierDevices:
            d.Start()
        for d in self.MarkerDevices:
            d.Start()

    def Stop(self):
        for d in self.AmplifierDevices:
            d.Stop()
        for d in self.MarkerDevices:
            d.Stop()

    def Read(self):
        markers = []
        d = self.AmplifierDevices[0].ReadData()
        if d is None:
            return d, markers

        # TODO: merge data streams

        # get all markers
        for md in self.MarkerDevices:
            m = md.ReadMarkers()
            if m:
                markers.extend(m)

        # translate marker time stamps into sample counter values
        scBase = d[2][0][0]
        tsBase = d[3][0]
        sr = self.SampleRate
        for m in range(len(markers)):
            ts, label = markers[m]
            sc = int(scBase + (ts - tsBase) * sr + 0.5)
            markers[m] = (sc, label)

        return d, markers

    @property
    def DeviceConnectionInfo(self):
        ''' Get connection state and signal quality
        '''
        ci = []
        for device in self.AmplifierDevices:
            try:
                ci.append((device.ConnectionState, device.SignalQuality))
            except:
                ci.append((ConnectionState.CS_DISCONNECTED, SignalQuality.SQ_NOINFO))
        return ci

    @property
    def SampleRate(self):
        if len(self.AmplifierDevices) > 0:
            sr = self.AmplifierDevices[0].SampleRate
        else:
            sr = 1000.0
        return sr

    @property
    def DeviceInfoString(self):
        info = []
        for device in self.AmplifierDevices:
            info.append(device.DeviceInfoString)
        for device in self.MarkerDevices:
            info.append(device.DeviceInfoString)
        if info:
            s = "\n".join(info)
        else:
            s = None
        return s


class StreamSelectionDialog(QtWidgets.QDialog):
    ''' Device selection
    '''
    def __init__(self, resolver, *args):
        super().__init__(*args)
        
        self.resize(500, 200)
        self.resolver = resolver
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        self.label_regular = QtWidgets.QLabel("Regular")
        self.SelectionListRegular = QtWidgets.QListWidget()
        self.SelectionListRegular.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.label_irregular = QtWidgets.QLabel("Irregular")
        self.SelectionListIrregular = QtWidgets.QListWidget()
        self.SelectionListIrregular.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label_regular)
        layout.addWidget(self.SelectionListRegular)

        layout.addWidget(self.label_irregular)
        layout.addWidget(self.SelectionListIrregular)

        vlayout = QtWidgets.QVBoxLayout()
        vlayout.addLayout(layout)
        vlayout.addWidget(self.buttonBox)
        
        self.setLayout(vlayout)
        self.setWindowTitle("Select LSL streams")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.UpdateStreamList()
        self.startTimer(1000)

    def StreamID(self, stream):
        id = "%s (%s)"%(stream.name(), stream.source_id())
        return id


    def UpdateStreamList(self):
        streams = self.resolver.results()
        regularStreamIDs = []
        irregularStreamIDs = []
        for stream in streams:
            if stream.nominal_srate() == IRREGULAR_RATE:
                irregularStreamIDs.append(self.StreamID(stream))
            else:
                regularStreamIDs.append(self.StreamID(stream))

        # remove not existing items from regular list
        itemsToRemove=[]
        for row in range(self.SelectionListRegular.count()):
            item = self.SelectionListRegular.item(row)
            if item.text() not in regularStreamIDs:
                itemsToRemove.append(row)
        for item in itemsToRemove:
            self.SelectionListRegular.takeItem(item)
        
        # remove not existing items from irregular list
        itemsToRemove=[]
        for row in range(self.SelectionListIrregular.count()):
            item = self.SelectionListIrregular.item(row)
            if item.text() not in irregularStreamIDs:
                itemsToRemove.append(row)
        for item in itemsToRemove:
            self.SelectionListIrregular.takeItem(item)
            
        # add new items to the regular list
        present = []
        for row in range(self.SelectionListRegular.count()):
            item = self.SelectionListRegular.item(row)
            present.append(item.text())
        for id in regularStreamIDs:
            if id not in present:
                self.SelectionListRegular.addItem(id)

        # add new items to the irregular list
        present = []
        for row in range(self.SelectionListIrregular.count()):
            item = self.SelectionListIrregular.item(row)
            present.append(item.text())
        for id in irregularStreamIDs:
            if id not in present:
                self.SelectionListIrregular.addItem(id)

        # auto select the first regular stream
        if len(self.SelectionListRegular.selectedItems()) == 0 and self.SelectionListRegular.count() > 0:
            self.SelectionListRegular.item(0).setSelected(True)

        # disable the irregular selection list if no regular item is selected
        if len(self.SelectionListRegular.selectedItems()) == 0:
            self.SelectionListIrregular.setEnabled(False)
        else:
            self.SelectionListIrregular.setEnabled(True)

        numRegularStreams = "%i regular stream(s) available"%len(regularStreamIDs)
        self.label_regular.setText(numRegularStreams)

        numIrregularStreams = "%i irregular stream(s) available"%len(irregularStreamIDs)
        self.label_irregular.setText(numIrregularStreams)
        
    def GetSelection(self):
        selection = []
        for item in self.SelectionListRegular.selectedItems():
            for stream in self.resolver.results():
                if item.text() == self.StreamID(stream):
                    selection.append(stream)
        for item in self.SelectionListIrregular.selectedItems():
            for stream in self.resolver.results():
                if item.text() == self.StreamID(stream):
                    selection.append(stream)
        return selection
    
    def timerEvent(self, e):
        self.UpdateStreamList()



'''
------------------------------------------------------------
UNIT TESTS
------------------------------------------------------------
'''


def UnitTestSelection():
    app = QtWidgets.QApplication([])
    selector = LSL_Controler()
    selector.ConnectStreams()




if __name__ == '__main__':
    UnitTestSelection()



