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


import sys, os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

from optparse import OptionParser
from lxml import etree
from lxml import objectify 

from tools.utils import GetExceptionTraceBack, Flatten, CompareVersion
from .modbase import ModuleBase, ModuleEvent, EventType, ErrorSeverity, RecordingMode
from resources import resources_rc
from .configdialog import ConfigurationDialog
from .statusbar import StatusBarWidget

from .siggen import SignalGenerator

__application__ = "BrainVision LSL Viewer"
__version__ = "0.9.5"
'''Application Version'''



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi()
        self.firstShown = False

        # create and add the status bar
        self.statusWidget = StatusBarWidget(initialText="Brain Products GmbH, " + __application__ +" " + __version__)
        self.statusBar().addPermanentWidget(self.statusWidget, 1)
        self.statusWidget.showLogEvent.connect(self.showLogEntries)
        self.statusWidget.saveLogEvent.connect(self.saveLogEntries)

        # remote control server
        self.RC = None

        # set preferences
        self.applicationName = __application__
        self.configurationFile = ""
        self.configurationDir = ""
        self.logDir = ""
        self.appVersion = QtCore.QVersionNumber.fromString(__version__)
        self.loadPreferences()
        self.recordingMode = -1

        # build the application
        self.parseCommandLine()
        self.defineModuleChain()

        # initial module chain update (top module)
        self.topmodule.update_receivers()

        # update log text module info
        self.updateModuleInfo()
        
        # update button states
        self.updateUI()

        # performance boost ;-)
        self.startTimer(1)

        # load configuration file
        if self.cmd_options.ConfigurationFile == None:
            # try to load the last configuration file
            try:
                if len(self.configurationFile) > 0:
                    cfg = os.path.normpath(self.configurationDir + '/' + self.configurationFile)
                    self.loadConfiguration(cfg)
                else:
                    self.resetConfiguration()
            except:
                pass
        else:
            # try to load configuration from command line file
            try:
                self.loadConfiguration(os.path.normpath(self.cmd_options.ConfigurationFile))
            except Exception as e:
                raise Exception("Failed to load configuration from file: " +
                                self.cmd_options.ConfigurationFile + "\n" + repr(e))


    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(862, 604)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/bv.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)

        self.centralwidget = QtWidgets.QWidget(self)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        # signal pane
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_SignalPane = QtWidgets.QHBoxLayout()
        self.horizontalLayout_SignalPane.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout_SignalPane.setObjectName("horizontalLayout_SignalPane")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_SignalPane.addItem(spacerItem)
        self.horizontalLayout.addLayout(self.horizontalLayout_SignalPane)
        # control pane with vertical scroll bar
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollArea.sizePolicy().hasHeightForWidth())
        self.scrollArea.setSizePolicy(sizePolicy)
        self.scrollArea.setMinimumSize(QtCore.QSize(300, 0))
        self.scrollArea.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrollArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.scrollArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 300, 533))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.scrollAreaWidgetContents.sizePolicy().hasHeightForWidth())
        # online parameters 
        self.scrollAreaWidgetContents.setSizePolicy(sizePolicy)
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(300, 0))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.verticalLayout_OnlinePane = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout_OnlinePane.setObjectName("verticalLayout_OnlinePane")
        # configuration button
        self.pushButtonConfiguration = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
        self.pushButtonConfiguration.setStyleSheet("text-align: left; padding-left: 10px; padding-top: 5px; padding-bottom: 5px")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/process.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonConfiguration.setIcon(icon1)
        self.pushButtonConfiguration.setIconSize(QtCore.QSize(32, 32))
        self.pushButtonConfiguration.setObjectName("pushButtonConfiguration")
        self.verticalLayout_OnlinePane.addWidget(self.pushButtonConfiguration)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_OnlinePane.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.setCentralWidget(self.centralwidget)
        # main menu and status bar
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 862, 27))
        self.menubar.setObjectName("menubar")
        self.menuApplication = QtWidgets.QMenu(self.menubar)
        self.menuApplication.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.menuApplication.setTearOffEnabled(False)
        self.menuApplication.setObjectName("menuApplication")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.setObjectName("actionQuit")
        self.actionShowLog = QtWidgets.QAction(self)
        self.actionShowLog.setObjectName("actionShowLog")
        self.actionLoadConfiguration = QtWidgets.QAction(self)
        self.actionLoadConfiguration.setObjectName("actionLoadConfiguration")
        self.actionSaveConfiguration = QtWidgets.QAction(self)
        self.actionSaveConfiguration.setObjectName("actionSaveConfiguration")
        self.actionDefaultConfiguration = QtWidgets.QAction(self)
        self.actionDefaultConfiguration.setObjectName("actionDefaultConfiguration")
        if not self.isLSL:
            self.menuApplication.addAction(self.actionLoadConfiguration)
            self.menuApplication.addAction(self.actionSaveConfiguration)
            self.menuApplication.addAction(self.actionDefaultConfiguration)
            self.menuApplication.addSeparator()
        self.menuApplication.addAction(self.actionShowLog)
        self.menuApplication.addSeparator()
        self.menuApplication.addAction(self.actionQuit)
        self.menubar.addAction(self.menuApplication.menuAction())
        # set item text
        self.setWindowTitle(__application__)
        self.pushButtonConfiguration.setText("Configuration ...")
        self.menuApplication.setTitle("File")
        self.actionQuit.setText("Quit")
        self.actionShowLog.setText("Show Log")
        self.actionLoadConfiguration.setText("Load Configuration ...")
        self.actionSaveConfiguration.setText("Save Configuration ...")
        self.actionDefaultConfiguration.setText("Reset Configuration")

        QtCore.QMetaObject.connectSlotsByName(self)

    def showEvent(self, event):
        if not self.firstShown:
            self.windowHandle().screenChanged.connect(self.screen_changed)
            self.screen_changed(self.windowHandle().screen())
            self.firstShown = True

    def screen_changed(self, new_screen):
        dpi = new_screen.logicalDotsPerInch()
        if dpi == 96.0:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, True)
        else:
            QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi, False)

    def closeEvent(self, event):
        ''' Application wants to close, prevent closing if recording to file is still active
        '''
        if not self.topmodule.query("Stop"):
            event.ignore()
        else:
            self.topmodule.stop(force=True)
            self.savePreferences()
            # clean up modules
            for module in Flatten(self.modules):
                module.terminate()
            # terminate remote control server
            if self.RC != None:
                self.RC.terminate()
            event.accept()


    def messageReceived(self, event):
        print("Main: %s"%event)

    @QtCore.Slot()        
    def on_pushButtonConfiguration_clicked(self):
        """ Configuration button clicked
        - Open configuration dialog and add configuration panes for each module in the
        module chain, if available
        """
        dlg = ConfigurationDialog()
        for module in Flatten(self.modules):
            pane = module.get_configuration_pane()
            if pane != None:
                dlg.addPane(pane)
        ok = dlg.exec_()
        if ok and not self.isLSL:
            self.on_actionSaveConfiguration_triggered()

    @QtCore.Slot()        
    def on_actionLoadConfiguration_triggered(self):
        """ Load configuration from XML file """
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        dlg.setNameFilter("Configuration files (*.xml)")
        dlg.setDefaultSuffix("xml")
        if len(self.configurationDir) > 0:
            dlg.setDirectory(self.configurationDir)
        dlg.selectFile(self.configurationFile)
        if dlg.exec_() == True:
            try:
                files = dlg.selectedFiles()
                fileName = files[0]
                # load configuration from XML file
                self.loadConfiguration(fileName)
                # set preferences
                dir, fn = os.path.split(fileName)            
                self.configurationFile = fn
                self.configurationDir = dir
            except Exception as e:
                tb = GetExceptionTraceBack()[0]
                self.processEvent(ModuleEvent("Load Configuration", EventType.ERROR,\
                                              tb + " -> %s "%(fileName) + str(e), 
                                              severity=ErrorSeverity.NOTIFY))

    @QtCore.Slot()        
    def on_actionSaveConfiguration_triggered(self):
        """ Save configuration to file """
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setNameFilter("Configuration files (*.xml)")
        dlg.setDefaultSuffix("xml")
        if len(self.configurationDir) > 0:
            dlg.setDirectory(self.configurationDir)
        dlg.selectFile(self.configurationFile)
        if dlg.exec_() == True:
            try:
                files = dlg.selectedFiles()
                fileName = files[0]
                # save configuration to XML
                self.saveConfiguration(fileName)
                # set preferences
                dir, fn = os.path.split(fileName)            
                self.configurationFile = fn
                self.configurationDir = dir
                # update status line
                fn, ext = os.path.splitext(os.path.split(fileName)[1])            
                self.processEvent(ModuleEvent("Application",
                                              EventType.STATUS,
                                              info = fn,
                                              status_field = "Workspace"))
            except Exception as e:
                tb = GetExceptionTraceBack()[0]
                self.processEvent(ModuleEvent("Save Configuration", EventType.ERROR,\
                                              tb + " -> %s "%(fileName) + str(e), 
                                              severity=ErrorSeverity.NOTIFY))

    @QtCore.Slot()        
    def on_actionDefaultConfiguration_triggered(self):
        """ Reset configuration to default values """
        self.resetConfiguration()

    @QtCore.Slot()
    def on_actionShowLog_triggered(self):
        self.showLogEntries()

    @QtCore.Slot()
    def on_actionQuit_triggered(self):
        self.close()

    def parseCommandLine(self):
        ''' Parse command line options    
        '''
    
        # get command line options    
        parser = OptionParser()
        parser.add_option("-m", "--modules", dest="ModuleFile",
                          help="Instantiate modules from separate module definition file MODULEFILE. "
                               "InstantiateModules() from this file will be called." )
        parser.add_option("-c", "--configfile", dest="ConfigurationFile",
                          help="Load CONFIGURATIONFILE instead of last configuration.")
        parser.add_option("-r", "--runas", dest="RunAs", default="",
                          help="Specify the module configuration that should be used.")
        parser.add_option("-o", "--options", dest="Options", default="",
                          help="General options: R - start the remote server")
        try:
            self.cmd_options, args = parser.parse_args()
        except: 
            raise Exception("Command line parser error !")
        # set remote client as default run configuration
        if self.cmd_options.RunAs == "":
            self.cmd_options.RunAs = "RC"
    
    @property
    def isLSL(self):
        return 'LSL' in __application__


    def defineModuleChain(self):
        ''' Instantiate and arrange module objects 
        - Modules will be connected top -> down, starting with array index 0 
        - Additional modules can be connected left -> right with tuples as list objects 
        '''
        # check the command line option
        if self.cmd_options.ModuleFile == None:
            if self.isLSL:
                self.cmd_options.ModuleFile = "amplifiers.lsl.modulesL"
            else:
                self.cmd_options.ModuleFile = "base.moduletree"
        # get module configuration from external file
        try:
            #exec("from " + self.cmd_options.ModuleFile + " import InstantiateModules as im")
            #self.modules = InstantiateModules(self.cmd_options.RunAs)
            import importlib
            mod = importlib.import_module(self.cmd_options.ModuleFile)
            self.modules = mod.InstantiateModules(self.cmd_options.RunAs)
        except Exception as e:
            raise Exception("Failed to instantiate modules from external file: " +
                            self.cmd_options.ModuleFile + "\n" + str(e))
        # append a data sink for performance calculation
        self.modules.append(DataSink())

        # connect modules
        for idx_vertical in range(len(self.modules)-1):
            if type(self.modules[idx_vertical]) in (tuple, list):
                # connect top/down
                if type(self.modules[idx_vertical+1]) in (tuple, list):
                    self.modules[idx_vertical][0].add_receiver(self.modules[idx_vertical+1][0])
                else:
                    self.modules[idx_vertical][0].add_receiver(self.modules[idx_vertical+1])
                # connect left/right
                for idx_horizontal in range(len(self.modules[idx_vertical])-1):
                    self.modules[idx_vertical][idx_horizontal].add_receiver(self.modules[idx_vertical][idx_horizontal+1])
            else:
                # connect top/down
                if type(self.modules[idx_vertical+1]) in (tuple, list):
                    self.modules[idx_vertical].add_receiver(self.modules[idx_vertical+1][0])
                else:
                    self.modules[idx_vertical].add_receiver(self.modules[idx_vertical+1])

        # get the top module
        if type(self.modules[0]) in (tuple, list):
            self.topmodule = self.modules[0][0]
        else:
            self.topmodule = self.modules[0]
        
        # get the bottom module
        if type(self.modules[-1]) in (tuple, list):
            self.bottommodule = self.modules[-1][-1]
        else:
            self.bottommodule = self.modules[-1]

        # get events from module chain top module
        self.topmodule.eventToParent.connect(self.processEvent, QtCore.Qt.QueuedConnection)

        # get signal panes for plot area
        self.horizontalLayout_SignalPane.removeItem(self.horizontalLayout_SignalPane.itemAt(0))
        for module in Flatten(self.modules):
            pane = module.get_display_pane()
            if pane != None:
                self.horizontalLayout_SignalPane.addWidget(pane)

        # insert online configuration panes
        position = 0
        for module in Flatten(self.modules):
            module.main_object = self
            pane = module.get_online_configuration()
            if pane != None:
                #self.verticalLayout_OnlinePane.insertWidget(self.verticalLayout_OnlinePane.count()-2, pane)
                self.verticalLayout_OnlinePane.insertWidget(position, pane)
                position += 1



    def processEvent(self, event):
        ''' Process events from module chain
        @param event: ModuleEvent object
        Stop acquisition on errors with a severity > 1
        '''
       
        # process commands
        if event.type == EventType.COMMAND:
            # don't log commands
            return

        # recording mode changed?
        if event.type == EventType.STATUS:
            if event.status_field == "Mode":
                self.recording_mode = event.info
                self.updateUI(isRunning=(event.info != RecordingMode.STOP))
                self.updateModuleInfo()
                
        # log events and update status line
        self.statusWidget.updateEventStatus(event)

        # look for errors
        if (event.type == EventType.ERROR) and (event.severity > 1):
            self.topmodule.stop(force=True)


    def sendEvent(self, event):
        ''' Send an event to the top module event chain
        '''
        self.topmodule.send_event(event)
            

    def savePreferences(self):
        ''' Save preferences to XML file
        '''
        E = objectify.E
        preferences = E.preferences(E.configDir(self.configurationDir),
                                    E.configFile(self.configurationFile),
                                    E.logDir(self.logDir))
        root = E.BVViewer(preferences, version=self.appVersion.toString())
        
        # preferences will be stored to user home directory
        try:
            homedir = QtCore.QDir.home()
            appdir = "." + self.applicationName
            if not homedir.cd(appdir):
                homedir.mkdir(appdir)
                homedir.cd(appdir)
            filename = str(homedir.absoluteFilePath("preferences.xml"))
            etree.ElementTree(root).write(filename, pretty_print=True, encoding="UTF-8")
        except:
            pass
        
    def loadPreferences(self):
        ''' Load preferences from XML file
        '''
        try:
            # preferences will be stored to user home directory
            homedir = QtCore.QDir.home()
            appdir = "." + self.applicationName
            if not homedir.cd(appdir):
                return
            filename = str(homedir.absoluteFilePath("preferences.xml"))
    
            # read XML file
            cfg = objectify.parse(filename)
            # check application and version
            app = cfg.xpath("//BVViewer")
            if (len(app) == 0) or (app[0].get("version") == None):
                # configuration data not found
                return          
            # check version
            v = app[0].get("version")
            version = QtCore.QVersionNumber.fromString(v)
            common = QtCore.QVersionNumber.commonPrefix(version, self.appVersion)
            if common.segmentCount() < 2:
                # wrong version
                return          
    
            # update preferences
            preferences = app[0].preferences
            self.configurationDir = preferences.configDir.pyval
            self.configurationFile = preferences.configFile.pyval
            self.logDir = preferences.logDir.pyval
        except:
            pass


    def saveConfiguration(self, filename):
        ''' Save module configuration to XML file
        @param filename: Full qualified XML file name 
        '''
        E = objectify.E
        modules = E.modules()
        # get configuration from each connected module
        for module in Flatten(self.modules):
            cfg = module.getXML()
            if cfg != None:
                modules.append(cfg)
        # build complete configuration tree
        root = E.BVViewer(modules, version=__version__)
        # write it to file
        etree.ElementTree(root).write(filename, pretty_print=True, encoding="UTF-8")

    def loadConfiguration(self, filename):
        ''' Load module configuration from XML file
        @param filename: Full qualified XML file name 
        '''
        ok = True
        cfg = objectify.parse(filename)
        # check application and version
        app = cfg.xpath("//BVViewer")
        if (len(app) == 0) or (app[0].get("version") == None):
            # configuration data not found
            self.processEvent(ModuleEvent("Load Configuration", EventType.ERROR,\
                                          "%s is not a valid BVViewer configuration file"%(filename),\
                                          severity=1) )
            ok = False          

        if ok:
            version = app[0].get("version")
            if CompareVersion(version, __version__, 2) > 0:
                # wrong version
                self.processEvent(ModuleEvent("Load Configuration", EventType.ERROR,\
                                              "%s wrong version %s > %s"%(filename, version, __version__),\
                                              severity=ErrorSeverity.NOTIFY) )
                ok = False          
        
        # setup modules from configuration file
        if ok:
            for module in Flatten(self.modules):
                module.setXML(cfg)

            # update module chain, starting from top module
            self.topmodule.update_receivers()

            # update status line
            file_name, ext = os.path.splitext(os.path.split(filename)[1])            
            self.processEvent(ModuleEvent("Application",
                                          EventType.STATUS,
                                          info = file_name,
                                          status_field = "Workspace"))
        

    def resetConfiguration(self):
        ''' Menu "Reset Configuration": 
        Set default values for all modules
        '''
        # reset all modules
        for module in Flatten(self.modules):
            module.setDefault()

        # update module chain, starting from top module
        self.topmodule.update_receivers()

        # update status line
        self.processEvent(ModuleEvent("Application",
                                      EventType.STATUS,
                                      info = "default",
                                      status_field = "Workspace"))


    def updateUI(self, isRunning=False):
        ''' Update user interface to reflect the recording state
        '''
        if isRunning:
            self.pushButtonConfiguration.setEnabled(False)
            self.actionLoadConfiguration.setEnabled(False)
            self.actionSaveConfiguration.setEnabled(False)
            self.actionQuit.setEnabled(False)
            self.actionDefaultConfiguration.setEnabled(False)
        else:
            self.pushButtonConfiguration.setEnabled(True)
            self.actionLoadConfiguration.setEnabled(True)
            self.actionSaveConfiguration.setEnabled(True)
            self.actionQuit.setEnabled(True)
            self.actionDefaultConfiguration.setEnabled(True)
            self.statusWidget.resetUtilization()

    def updateModuleInfo(self):
        ''' Update the module information in the log text
        and propagate it to all connected modules as status information   
        '''
        # get module information
        self.statusWidget.moduleinfo = ""
        for module in Flatten(self.modules):
            info = module.get_module_info()
            if info != None:
                self.statusWidget.moduleinfo += module._object_name + "\n"
                self.statusWidget.moduleinfo += info
        if len(self.statusWidget.moduleinfo) > 0:
            self.statusWidget.moduleinfo += "\n\n"
        
        # propagate status info to all connected modules
        moduleinfo = __application__ + " " + __version__ + "\n\n"
        moduleinfo += self.statusWidget.moduleinfo
        msg = ModuleEvent(__application__,
                          EventType.STATUS,
                          info = moduleinfo,
                          status_field="ModuleInfo")
        self.sendEvent(msg)

    def showLogEntries(self):
        ''' Show log entries
        '''
        self.updateModuleInfo()
        self.statusWidget.showLogEntries()

    def saveLogEntries(self):
        ''' Write log entries to file
        '''
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        dlg.setNameFilter("Log files (*.log)")
        dlg.setDefaultSuffix("log")
        if len(self.logDir) > 0:
            dlg.setDirectory(self.logDir)
        if dlg.exec_() == True:
            try:
                files = dlg.selectedFiles()
                file_name = files[0]
                # set preferences
                dir, fn = os.path.split(file_name)            
                self.logDir = dir
                # write log entries to file
                f = open(file_name, "w", encoding="utf-8")
                f.write(self.statusWidget.getLogText())
                f.close()
            except Exception as e:
                tb = GetExceptionTraceBack()[0]
                QtWidgets.QMessageBox.critical(None, __application__, 
                                        "Failed to write log file (%s)\n"%(file_name) +
                                        tb + " -> " + str(e))


class DataSink(ModuleBase):
    ''' Last module in the chain
    '''
    def __init__(self, usethread = True, queuesize = 20, name = 'DataSink', instance = 0):
        super().__init__(usethread, queuesize, name, instance)
        self.data = None                
        self.dataavailable = False
        
    def process_input(self, datablock):
        self.dataavailable = True       
        self.data = datablock           
        
    
    def process_output(self):
        if not self.dataavailable:
            return None
        # send performance / utilization event
        totaltime = 1000.0 * self.data.performance_timer_max
        sampletime = 1000.0 * totaltime / self.data.sample_channel.shape[1]
        utilization = sampletime * self.data.sample_rate / 1e6 * 100.0
        self.send_event(ModuleEvent(self._object_name,
                                    EventType.STATUS,
                                    info = utilization,
                                    status_field = "Utilization"))
        self.dataavailable = False
        return self.data
    

def main(args=sys.argv):
    ''' Create and start up main application
    '''
    print("Starting application, please wait ...\n")

    app = QtWidgets.QApplication(args)
    try:
        win = None
        win = MainWindow()
        win.showMaximized()
        app.exec_()
    except Exception as e:
        tb = GetExceptionTraceBack()[0]
        QtWidgets.QMessageBox.critical(None, "Application", tb + " -> " + str(e))
        if win != None:
            win.close()
   
    print("Application terminated\n")
        
        
if __name__ == '__main__':
    main()
