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
import collections
from .modbase import ModuleEvent, EventType, ErrorSeverity
        
class StatusBarWidget(QtWidgets.QWidget):
    ''' Main Window status bar
    '''
    showLogEvent = QtCore.Signal()
    saveLogEvent = QtCore.Signal()
    
    def __init__(self, initialText=""):
        super().__init__()
        self.setupUi()
        self.initialText = initialText

        # info label color and click 
        self.labelInfo.setAutoFillBackground(True)
        self.labelInfo.mouseReleaseEvent = self.labelInfoClicked
        self.defaultBkColor = self.labelInfo.palette().color(self.labelInfo.backgroundRole())
        self.labelInfo.setText(initialText)
        self.labelStatus_4.setAutoFillBackground(True)
        
        # log entries
        self.logFifo = collections.deque(maxlen=10000)
        self.lockError = False
        self.moduleinfo = ""
        
        # number of channels and reference channel names
        self.status_channels = ""
        self.status_reference = ""
        
        # utilization progressbar fifo
        self.resetUtilization()
        
    def setupUi(self):
        self.setObjectName("frmStatusBar")
        self.resize(903, 43)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelInfo = QtWidgets.QLabel(self)
        self.labelInfo.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelInfo.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelInfo.setObjectName("labelInfo")
        self.horizontalLayout.addWidget(self.labelInfo)
        self.labelStatus_1 = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelStatus_1.sizePolicy().hasHeightForWidth())
        self.labelStatus_1.setSizePolicy(sizePolicy)
        self.labelStatus_1.setMinimumSize(QtCore.QSize(50, 0))
        self.labelStatus_1.setMaximumSize(QtCore.QSize(100, 16777215))
        self.labelStatus_1.setBaseSize(QtCore.QSize(0, 0))
        self.labelStatus_1.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelStatus_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelStatus_1.setText("")
        self.labelStatus_1.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus_1.setObjectName("labelStatus_1")
        self.horizontalLayout.addWidget(self.labelStatus_1)
        self.labelStatus_2 = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelStatus_2.sizePolicy().hasHeightForWidth())
        self.labelStatus_2.setSizePolicy(sizePolicy)
        self.labelStatus_2.setMaximumSize(QtCore.QSize(180, 16777215))
        self.labelStatus_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelStatus_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelStatus_2.setText("")
        self.labelStatus_2.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus_2.setWordWrap(True)
        self.labelStatus_2.setObjectName("labelStatus_2")
        self.horizontalLayout.addWidget(self.labelStatus_2)
        self.labelStatus_3 = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelStatus_3.sizePolicy().hasHeightForWidth())
        self.labelStatus_3.setSizePolicy(sizePolicy)
        self.labelStatus_3.setMaximumSize(QtCore.QSize(150, 16777215))
        self.labelStatus_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelStatus_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelStatus_3.setText("")
        self.labelStatus_3.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus_3.setObjectName("labelStatus_3")
        self.horizontalLayout.addWidget(self.labelStatus_3)
        self.labelStatus_4 = QtWidgets.QLabel(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelStatus_4.sizePolicy().hasHeightForWidth())
        self.labelStatus_4.setSizePolicy(sizePolicy)
        self.labelStatus_4.setMinimumSize(QtCore.QSize(60, 0))
        self.labelStatus_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.labelStatus_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.labelStatus_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.labelStatus_4.setText("")
        self.labelStatus_4.setAlignment(QtCore.Qt.AlignCenter)
        self.labelStatus_4.setObjectName("labelStatus_4")
        self.horizontalLayout.addWidget(self.labelStatus_4)
        self.progressBarUtilization = QtWidgets.QProgressBar(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.progressBarUtilization.sizePolicy().hasHeightForWidth())
        self.progressBarUtilization.setSizePolicy(sizePolicy)
        self.progressBarUtilization.setMaximumSize(QtCore.QSize(150, 16777215))
        self.progressBarUtilization.setMaximum(100)
        self.progressBarUtilization.setProperty("value", 20)
        self.progressBarUtilization.setInvertedAppearance(False)
        self.progressBarUtilization.setObjectName("progressBarUtilization")
        self.horizontalLayout.addWidget(self.progressBarUtilization)

        self.setWindowTitle("Form")
        self.labelInfo.setToolTip("Click here to get the message history")
        self.labelInfo.setText("Brain Products GmbH")
        self.labelStatus_1.setToolTip("Sampling Rate")
        self.labelStatus_2.setToolTip("Total number of channels and reference channels")
        self.labelStatus_3.setToolTip("Configuration")
        self.labelStatus_4.setToolTip("Battery Voltage")
        self.progressBarUtilization.setFormat("%v% Utilization")

        QtCore.QMetaObject.connectSlotsByName(self)


    def resetUtilization(self):
        ''' Reset utilization parameters
        '''
        self.utilizationFifo = collections.deque()
        self.utilizationUpdateCounter = 0
        self.utilizationMaxValue = 0
        self.updateUtilization(0)
        
    def updateUtilization(self, utilization):
        ''' Update the utilization progressbar
        @param utilization: percentage of utilization 
        '''
        # average utilization value
        self.utilizationFifo.append(utilization)
        if len(self.utilizationFifo) > 5:
            self.utilizationFifo.popleft()
        utilization = sum(self.utilizationFifo) / len(self.utilizationFifo)
        self.utilizationMaxValue = max(self.utilizationMaxValue, utilization)
        
        # slow down utilization display
        if self.utilizationUpdateCounter > 0:
            self.utilizationUpdateCounter -= 1
            return
        self.utilizationUpdateCounter = 5
        utilization = self.utilizationMaxValue
        self.utilizationMaxValue = 0
        
        # update progress bar
        if utilization < 100:
            self.progressBarUtilization.setValue(utilization)
        else:
            self.progressBarUtilization.setValue(100)
        self.progressBarUtilization.setFormat("%d%% Utilization"%(utilization))
        
        # modify progress bar color (<80% -> green, >=80% -> red) 
        if utilization < 80:
            self.progressBarUtilization.setStyleSheet("QProgressBar {padding: 1px; text-align: right; margin-right: 35ex;} "\
                                                      "QProgressBar::chunk {background: "\
                                                      "qlineargradient(x1: 1, y1: 0, x2: 1, y2: 0.5, stop: 1 green, stop: 0 white);"\
                                                      "margin: 0.5px}")
        else:
            self.progressBarUtilization.setStyleSheet("QProgressBar {padding: 1px; text-align: right; margin-right: 35ex;} "\
                                                      "QProgressBar::chunk {background: "\
                                                      "qlineargradient(x1: 1, y1: 0, x2: 1, y2: 0.5, stop: 1 red, stop: 0 white);"\
                                                      "margin: 0.5px}")
        
    def updateEventStatus(self, event):
        ''' Update status info field and put events into the log fifo
        @param event: ModuleEvent object
        '''
        # display dedicated status info values
        if event.type == EventType.STATUS:
            if event.status_field == "Rate":
                self.labelStatus_1.setText(event.info)
            elif event.status_field == "Channels":
                self.status_channels = event.info
                self.labelStatus_2.setText(self.status_channels + ", " + self.status_reference)
            elif event.status_field == "Reference":
                refnames = event.info
                # limit the number of displayed channel names
                if len(refnames) > 70:
                    refnames = refnames[:70].rsplit('+',1)[0] + "+ ..."
                self.status_reference = refnames
                self.labelStatus_2.setText(self.status_channels + ", " + self.status_reference)
            elif event.status_field == "Workspace":
                self.labelStatus_3.setText(event.info)
            elif event.status_field == "Battery":
                # set voltage
                self.labelStatus_4.setText(event.info)
                # severity indicates normal, critical or bad
                palette = self.labelStatus_4.palette()
                if event.severity == ErrorSeverity.NOTIFY:
                    palette.setColor(self.labelStatus_4.backgroundRole(), QtCore.Qt.yellow)
                elif event.severity == ErrorSeverity.STOP:
                    palette.setColor(self.labelStatus_4.backgroundRole(), QtCore.Qt.red)
                else:
                    palette.setColor(self.labelStatus_4.backgroundRole(), self.defaultBkColor)
                self.labelStatus_4.setPalette(palette)
            elif event.status_field == "Utilization":
                self.updateUtilization(event.info)
            return
        
        # lock an error display until LogView is shown
        if ((self.lockError == False) or (event.severity > 0)) and event.type != EventType.LOG:
            # update label
            self.labelInfo.setText(str(event))
            palette = self.labelInfo.palette()
            if event.type == EventType.ERROR:
                palette.setColor(self.labelInfo.backgroundRole(), QtCore.Qt.red)
                if event.severity > 0:
                    self.lockError = True
                    palette.setColor(self.labelInfo.backgroundRole(), QtCore.Qt.red)
                else:
                    palette.setColor(self.labelInfo.backgroundRole(), QtCore.Qt.yellow)
            else:
                palette.setColor(self.labelInfo.backgroundRole(), self.defaultBkColor)
            self.labelInfo.setPalette(palette)
        # put events into log fifo
        if event.type != EventType.MESSAGE:
            self.logFifo.append(event)
        
    def showLogEntries(self):
        ''' Show the event log content
        ''' 
        dlg = DlgLogView()
        dlg.setLogEntry(self.getLogText())
        save = dlg.exec_()
        if save:
            self.saveLogEvent.emit()
        self.resetErrorState()
    
    def getLogText(self):
        ''' Get the log entries as plain text
        '''
        txt = self.initialText + " Event Log\n\n"
        txt += self.moduleinfo
        for event in reversed(self.logFifo):
            txt += "%s\t %s\n"%(event.event_time.strftime("%Y-%m-%d %H:%M:%S.%f"), str(event))
        return txt
        
        
    def labelInfoClicked(self, mouse_event):
        ''' Mouse click into info label
        Show the event log content
        ''' 
        self.showLogEvent.emit()
        
        
    def resetErrorState(self):
        ''' Reset error lock and info display
        '''
        self.lockError = False
        self.labelInfo.setText("")
        palette = self.labelInfo.palette()
        palette.setColor(self.labelInfo.backgroundRole(), self.defaultBkColor)
        self.labelInfo.setPalette(palette)
        

'''
------------------------------------------------------------
LOG ENTRY DIALOG
------------------------------------------------------------
'''

class DlgLogView(QtWidgets.QDialog):
    ''' Show all log entries as plain text
    '''
    def __init__(self, *args):
        super().__init__(*args)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("frmLogView")
        self.resize(880, 400)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.labelView = QtWidgets.QPlainTextEdit(self)
        self.labelView.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.labelView.setReadOnly(True)
        self.labelView.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.labelView.setBackgroundVisible(False)
        self.labelView.setObjectName("labelView")
        self.gridLayout.addWidget(self.labelView, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonSave = QtWidgets.QPushButton(self)
        self.pushButtonSave.setAutoDefault(False)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.horizontalLayout.addWidget(self.pushButtonSave)
        self.pushButtonClose = QtWidgets.QPushButton(self)
        self.pushButtonClose.setDefault(True)
        self.pushButtonClose.setObjectName("pushButtonClose")
        self.horizontalLayout.addWidget(self.pushButtonClose)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 1)

        self.setWindowTitle("Log History")
        self.pushButtonSave.setText("Save")
        self.pushButtonClose.setText("Close")

        QtCore.QObject.connect(self.pushButtonClose, QtCore.SIGNAL("clicked()"), self.reject)
        QtCore.QObject.connect(self.pushButtonSave, QtCore.SIGNAL("clicked()"), self.accept)
        QtCore.QMetaObject.connectSlotsByName(self)

    def setLogEntry(self, entry):
        self.labelView.setPlainText(entry)

