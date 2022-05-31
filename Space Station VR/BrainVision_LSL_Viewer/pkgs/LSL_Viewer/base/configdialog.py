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


class ConfigurationDialog(QtWidgets.QDialog):
    ''' Module main configuration dialog
    All module configuration panes will go here
    '''
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.panes = []
        
    def setupUi(self):
        self.setObjectName("frmConfiguration")
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(1024, 750)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/process.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab1 = QtWidgets.QWidget()
        self.tab1.setObjectName("tab1")
        self.gridLayout1 = QtWidgets.QGridLayout(self.tab1)
        self.gridLayout1.setObjectName("gridLayout1")
        self.tabWidget.addTab(self.tab1, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.setWindowTitle("Configuration")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab1), "Tab 1")

        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QMetaObject.connectSlotsByName(self)


    def addPane(self, pane):
        ''' Insert new tab and add module configuration pane
        @param pane: module configuration pane (QFrame object)
        '''
        if pane == None:
            return
        currenttabs = len(self.panes) 
        if currenttabs > 0:
            # add new tab
            tab = QtWidgets.QWidget()
            tab.setObjectName("tab%d"%(currenttabs+1))
            gridLayout = QtWidgets.QGridLayout(tab)
            gridLayout.setObjectName("gridLayout%d"%(currenttabs+1))
            self.tabWidget.addTab(tab, "")
        else:
            gridLayout = self.gridLayout1
            tab = self.tab1
            
        self.panes.append(pane)
        gridLayout.addWidget(pane)
        self.tabWidget.setTabText(self.tabWidget.indexOf(tab), pane.windowTitle())
        


