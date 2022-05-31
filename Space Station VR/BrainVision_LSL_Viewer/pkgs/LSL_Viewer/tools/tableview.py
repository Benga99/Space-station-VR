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
import types


class GenericTableWidget(QtWidgets.QTableView):
    ''' Generic model/view table widget
    Table view for a list of data objects:
    The view content is defined by a list of column dictionaries
        dictionary: {'variable':'variable name', 'header':'header text', 
                     'edit':False/True, 'editor':'default' or 'combobox' or 'plaintext'}
        optional entries: 'min': minum value, 'max': maximum value, 
                          'dec': number of decimal places, 'step': spin box incr/decr
                          'indexed' : True, use value as combobox index
                          'singleselection' : True, no extended selection mode for this column
    If a column is defined as combobox, the cb list text items can also be defined in a dictionary:
        dictionary: {'variable name':['Item 1', 'Item 2', ...]}

    e.g.:
    class data()
         def __init__(self, idx):
             self.intVar = 55
             self.floatVar = 1.25
             self.strVar = "the quick brown fox"
             self.boolVar = False
                    
    columns =  [
                {'variable':'intVar', 'header':'Index', 'edit':True, 'editor':'default', 'min':5, 'step':5},
                {'variable':'floatVar', 'header':'Float Variable', 'edit':True, 'editor':'combobox'},
                {'variable':'boolVar', 'header':'Bool Variable', 'edit':True, 'editor':'default'},
                {'variable':'strVar', 'header':'String Variable', 'edit':True, 'editor':'default'},
               ]

    cblist = {'floatVar':['0.1', '0.22', '1.23', '2', '4.5', '6.44']}
    
    datalist = []
    for r in range(5):
        datalist.append(data())

    setData(datalist, columns, cblist)
    '''
    dataChangedEvent = QtCore.Signal()
    selectedRowChangedEvent = QtCore.Signal(int)
    def __init__(self, *args, **kwargs):
        QtWidgets.QTableView.__init__(*(self,) + args)
        self.setAlternatingRowColors(True)
        #self.setObjectName("tableViewGeneric")
        #self.horizontalHeader().setCascadingSectionResizes(False)
        stretch = True
        if "Stretch" in kwargs:
            stretch = kwargs["Stretch"]
        self.horizontalHeader().setStretchLastSection(stretch)
        if stretch:
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        else:
            self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        if "RowNumbers" in kwargs:
            self.verticalHeader().setVisible(kwargs["RowNumbers"])
        else:
            self.verticalHeader().setVisible(False)
        self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        if "SelectionBehavior" in kwargs:
            self.setSelectionBehavior(kwargs["SelectionBehavior"])
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # table description and content
        self.fnColorSelect = lambda x: None
        self.fnCheckBox = lambda x: None
        self.fnValidate = lambda row, col, data: True
        self.description = []
        self.cblist = {}
        self.data = []
        
        # selection info
        self.selectedRow = 0

    def _fillTables(self):
        ''' Create and fill data tables
        '''
        self.data_model = _DataTableModel(self.data, self.description, self.cblist)
        self.setModel(self.data_model)
        self.dataItemDelegate = _DataItemDelegate(self)
        self.setItemDelegate(self.dataItemDelegate)
        self.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.data_model.fnColorSelect = self.fnColorSelect
        self.data_model.fnCheckBox = self.fnCheckBox
        self.data_model.fnValidate = self.fnValidate

        # actions
        self.connect(self.data_model, QtCore.SIGNAL("dataChanged(QModelIndex, QModelIndex)"), self._table_data_changed)
        self.connect(self.selectionModel(), QtCore.SIGNAL("selectionChanged(QItemSelection, QItemSelection)"), self._selectionChanged)
        
    def _table_data_changed(self, topLeft, bottomRight):
        ''' SIGNAL data in channel table has changed
        '''
        # look for multiple selected rows
        cr = self.currentIndex().row()
        cc = self.currentIndex().column()
        selectedRows = [i.row() for i in self.selectedIndexes() if i.column() == cc]
        # change column value in all selected rows
        if len(selectedRows) > 1:
            extended = True
            if 'singleselection' in self.description[cc] and self.description[cc]['singleselection']:
                extended = False
            if extended:
                val = self.data_model._getitem(cr, cc)
                for r in selectedRows:
                    self.data_model._setitem(r, cc, val)
                self.data_model.clearCache()

        # notify parent about changes
        self.dataChangedEvent.emit()



    def _selectionChanged(self, selected, deselected):
        if len(selected.indexes()) > 0:
            self.selectedRow = selected.indexes()[0].row()
            # notify parent about changes
            self.selectedRowChangedEvent.emit(self.selectedRow)

    
    def setData(self, data, description, cblist):
        ''' Initialize the table view
        @param data: list of data objects
        @param description: list of column description dictionaries
        @param cblist: dictionary of combo box list contents 
        '''
        self.data = data
        self.description = description
        self.cblist = cblist
        self._fillTables()
        
    def setfnColorSelect(self, lambdaColor):
        ''' Set the background color selection function
        @param lambdaColor: color selction function  
        '''
        self.fnColorSelect = lambdaColor
        
    def setfnCheckBox(self, lambdaCheckBox):
        ''' Set the checkbox display function
        @param lambdaCheckBox: function override  
        '''
        self.fnCheckBox = lambdaCheckBox
        
    def setfnValidate(self, lambdaValidate):
        ''' Set the row validation function
        @param lambdaValidate: function override  
        '''
        self.fnValidate = lambdaValidate
        
    def getSelectedRow(self):
        return self.selectedRow

    def setSelectedRow(self, row):
        idx = self.data_model.index(row, 0)
        self.selectionModel().setCurrentIndex(idx, QtCore.QItemSelectionModel.Select)





class _DataTableModel(QtCore.QAbstractTableModel):
    ''' EEG and AUX table data model for the configuration pane
    '''
    class DataItem():
        def __init__(self):
            value = None
            color = None
            check = None

    def __init__(self, data, description, cblist, parent=None, *args):
        ''' Constructor
        @param data: list of data objects
        @param description: list of column description dictionaries
        @param cblist: dictionary of combo box list contents 
        '''
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = data
        # list of column description dictionaries
        # dictionary: {'variable':'variable name', 'header':'header text', 'edit':False/True, 'editor':'default' or 'combobox'}
        # optional entries: 'min': minum value, 'max': maximum value, 'dec': number of decimal places, 
        #                   'step': spin box incr/decr
        #                   'indexed' : True, use value as combobox index  
        self.columns = description

        # dictionary of combo box list contents
        # dictionary: {'variable name':['Item 1', 'Item 2', ...]}
        self.cblist = cblist
        
        # color selection function
        self.fnColorSelect = lambda x: None
        # checkbox modification function
        self.fnCheckBox = lambda x: None
        # row validation function
        self.fnValidate = lambda row, col, data: True
        self.debugCounter = 0
        
        self.dataCache = {}
        self.modelReset.connect(self.clearCache)

    def _getitem(self, row, column):
        ''' Get data item based on table row and column
        @param row: row number
        @param column: column number
        @return:  data value
        ''' 
        if (row >= len(self.arraydata)) or (column >= len(self.columns)):
            return None
        
        # get data object
        data = self.arraydata[row]
        # get variable name from column description
        variable_name = self.columns[column]['variable']
        # get variable value
        #if hasattr(data, variable_name):
        try:
            d = getattr(data, variable_name)
            # get value from combobox list values?
            if 'indexed' in self.columns[column] and variable_name in self.cblist:
                idx = d
                if idx >=0 and idx < len(self.cblist[variable_name]):
                    d = self.cblist[variable_name][idx]
        except:
            d = None
        return d

    def _setitem(self, row, column, value):
        ''' Set data item based on table row and column
        @param row: row number
        @param column: column number
        @param value: value object
        @return: True if property value was set, False if not
        ''' 
        if (row >= len(self.arraydata)) or (column >= len(self.columns)):
            return False
        
        # get data object
        data = self.arraydata[row]

        # get variable name from column description
        variable_name = self.columns[column]['variable']

        # get index from combobox list values
        if 'indexed' in self.columns[column] and variable_name in self.cblist:
            if value in self.cblist[variable_name]:
                value = self.cblist[variable_name].index(value)
            else:
                return False
            
        # set variable value
        #if hasattr(data, variable_name):
        try:
            t = type(getattr(data, variable_name))
            if t is bool:
                setattr(data, variable_name, bool(value))
                return True
            elif t is float:
                #if type(value) is str:
                #    locale = QtCore.QLocale()
                #    value = locale.toDouble(value)[0]
                setattr(data, variable_name, float(value))
                return True
            elif t is int:
                setattr(data, variable_name, int(value))
                return True
            elif t in (str,):
                v = str(value)
                setattr(data, variable_name, v)
                return True
            else:
                return False
        except:
            return False

    def getPropertyInfo(self, row, column):
        ''' Get channel property infos, if available
        '''
        if (row >= len(self.arraydata)) or (column >= len(self.columns)):
            return None
        # get data object
        data = self.arraydata[row]
        if hasattr(data, 'PropertyInfo'):
            # get variable name from column description
            variable_name = self.columns[column]['variable']
            # lookup the range type
            if variable_name in data.PropertyInfo:
                return data.PropertyInfo[variable_name]
            else:
                return None
        else:
            return None

    def isReadOnly(self, row, column):
        ''' Check if the channel property is read-only
        @param row: table row number
        @param column: table column number
        @return: True if the property is read-only 
        '''
        # if the column definition has an read/write switch, take it
        if 'edit' in self.columns[column]:
            return not self.columns[column]['edit']

        # else lookup the range type
        PropertyInfo = self.getPropertyInfo(row, column)
        if PropertyInfo is None:
            return True
        return PropertyInfo.isReadOnly()

    def editorType(self, row, column):
        ''' Get the columns editor type from column description or data type
        @param column: table column number
        @return: editor type as string
        ''' 
        if column >= len(self.columns):
            return None

        PropertyInfo = self.getPropertyInfo(row, column)
        if not PropertyInfo is None:
            editor = "default"
            if PropertyInfo.isReadOnly() or not PropertyInfo.isDiscrete():
                editor = "default"
            else:
                editor = "combobox"
            return editor

        if not "editor" in self.columns[column] or "default" in self.columns[column]['editor']:
            editor = "default"
            v = self._getitem(0, column)
            if type(v) is int:
                editor = "spinbox"
            elif type(v) is float:
                editor = "doublespinbox"
        else:
            editor = self.columns[column]['editor']
        return editor
    
    def editorMinValue(self, row, column):
        ''' Get the columns editor minimum value from column description
        @param column: table column number
        @return: minimum value 
        ''' 
        if column >= len(self.columns):
            return None

        PropertyInfo = self.getPropertyInfo(row, column)
        if not PropertyInfo is None:
            if PropertyInfo.isMinMax():
                return PropertyInfo.minValue
            else:
                return None

        if 'min' in self.columns[column]:
            return self.columns[column]['min']
        else:
            return None
            
    def editorMaxValue(self, row, column):
        ''' Get the columns editor maximum value from column description
        @param column: table column number
        @return: minimum value
        ''' 
        if column >= len(self.columns):
            return None

        PropertyInfo = self.getPropertyInfo(row, column)
        if not PropertyInfo is None:
            if PropertyInfo.isMinMax():
                return PropertyInfo.minValue
            else:
                return None

        if 'max' in self.columns[column]:
            return self.columns[column]['max']
        else:
            return None

    def editorDecimals(self, column):
        ''' Get the columns editor decimal places from column description
        @param column: table column number
        @return: minimum value
        ''' 
        if column >= len(self.columns):
            return None
        if 'dec' in self.columns[column]:
            return int(self.columns[column]['dec'])
        else:
            return None

    def editorStep(self, column):
        ''' Get the columns editor single step value from column description
        @param column: table column number
        @return: minimum value
        ''' 
        if column >= len(self.columns):
            return None
        if 'step' in self.columns[column]:
            return self.columns[column]['step']
        else:
            return None

    
    def comboBoxList(self, row, column):
        ''' Get combo box item list for specified column
        @param column: table column number
        @return: combo box item list
        '''
        if column >= len(self.columns):
            return None

        PropertyInfo = self.getPropertyInfo(row, column)
        if not PropertyInfo is None:
            if PropertyInfo.isDiscrete():
                return PropertyInfo.stringList()
            else:
                return None
        
        # get variable name from column description
        variable_name = self.columns[column]['variable']
        # lookup list in dictionary
        if variable_name in self.cblist:
            return self.cblist[variable_name]
        else:
            return None
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        ''' Get the number of required table rows
        @return: number of rows
        '''
        if parent.isValid():
            return 0
        return len(self.arraydata)
    
    def columnCount(self, parent=QtCore.QModelIndex()):
        ''' Get the number of required table columns
        @return: number of columns
        '''
        if parent.isValid():
            return 0
        return len(self.columns)
        
    def data(self, index, role): 
        ''' Abstract method from QAbstactItemModel to get cell data based on role
        @param index: QModelIndex table cell reference
        @param role: given role for the item referred to by the index
        @return: the data stored under the given role for the item referred to by the index
        '''
        if not index.isValid(): 
            return None

        row = index.row()
        column = index.column()

        # cache, cache, cache ...
        key = row * 1000 + index.column()
        if key in self.dataCache:
            cache = self.dataCache[key]
            value = cache.value
            color = cache.color
            check = cache.check
        else:
            # get the underlying data
            value = self._getitem(row, column)
            data = self.arraydata[row]
            color = self.fnColorSelect(data)
            check = self.fnCheckBox((index.column(), data))
            if not self.fnValidate(row, column, self.arraydata):
                color = QtGui.QColor(255, 0, 0)
            cache = self.DataItem()
            cache.value = value
            cache.color = color
            cache.check = check
            self.dataCache[key] = cache

            #if row == 0 and column == 0:
            #    print("Data", self.debugCounter, "Role", role)
            #    self.debugCounter += 1

        if role == QtCore.Qt.CheckStateRole:
            # display function override?
            data = self.arraydata[row]
            if check is not None:
                if check:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
            # use data value
            if type(value) is bool:
                if value:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        
        elif (role == QtCore.Qt.DisplayRole) or (role == QtCore.Qt.EditRole):
            if not type(value) is bool:
                return value
        
        elif role == QtCore.Qt.BackgroundRole:
            # change background color for a specified row
            if color != None:
                return color
            
        return None
    
    def flags(self, index):
        ''' Abstract method from QAbstactItemModel
        @param index: QModelIndex table cell reference
        @return: the item flags for the given index
        '''
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
        if self.isReadOnly(index.row(), index.column()):
            return QtCore.Qt.ItemIsSelectable
        key = index.row() * 1000 + index.column()
        if key in self.dataCache:
            value = self.dataCache[key].value
        else:
            value = self._getitem(index.row(), index.column())
        if type(value) is bool:
            return QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsSelectable
        return QtCore.QAbstractTableModel.flags(self, index) | QtCore.Qt.ItemIsEditable
        
    def setData(self, index, value, role):
        ''' Abstract method from QAbstactItemModel to set cell data based on role
        @param index: QModelIndex table cell reference
        @param value: new cell data
        @param role: given role for the item referred to by the index
        @return: true if successful; otherwise returns false.
        '''
        if index.isValid(): 
            left = self.createIndex(index.row(), 0)
            right = self.createIndex(index.row(), self.columnCount())
            if role == QtCore.Qt.EditRole:
                if not self._setitem(index.row(), index.column(), value):
                    return False
                self.clearCache()
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), index, index)
                return True
            elif role == QtCore.Qt.CheckStateRole:
                if not self._setitem(index.row(), index.column(), value == QtCore.Qt.Checked):
                    return False
                self.clearCache()
                self.emit(QtCore.SIGNAL('dataChanged(QModelIndex, QModelIndex)'), left, right)
                return True
        return False

    def headerData(self, section, orientation, role):
        ''' Abstract method from QAbstactItemModel to get the column header
        @param section: column or row number
        @param orientation: Qt.Horizontal = column header, Qt.Vertical = row header
        @param role: given role for the item referred to by the index
        @return: header
        '''
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.columns[section]['header']
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(section+1)
        return None

    def clearCache(self):
        self.dataCache = {}

    def resetModel(self):
        self.beginResetModel()
        self.endResetModel()



class _DataItemDelegate(QtWidgets.QStyledItemDelegate):  
    ''' Combobox item editor
    '''
    def __init__(self, parent=None):
        super(_DataItemDelegate, self).__init__(parent)
        self.displayDecimals = None

    def createEditor(self, parent, option, index):
        editortype = index.model().editorType(index.row(), index.column())
        # combo box
        if editortype == 'combobox':
            combobox = QtWidgets.QComboBox(parent)
            locale = QtCore.QLocale()
            dec = index.model().editorDecimals(index.column())
            cblist = index.model().comboBoxList(index.row(), index.column())
            if not cblist is None:
                format = 'f'
                if dec == None:
                    if type(cblist[0]) is int:
                        dec = 0
                    else:
                        format = 'g'
                        dec = 6
                if not type(cblist[0]) is str:
                    for i in range(len(cblist)):
                        cblist[i] = locale.toString(float(cblist[i]), format, dec)
                combobox.addItems(cblist)
            combobox.setEditable(False)
            self.connect(combobox, QtCore.SIGNAL('activated(int)'), self.emitCommitData)
            return combobox
        
        # multi line editor (plain text)
        if editortype == 'plaintext':
            editor = QtWidgets.QPlainTextEdit(parent)
            editor.setMinimumHeight(100)
            return editor

        # spinbox for integer values
        if editortype == 'spinbox':
            editor = QtWidgets.QSpinBox(parent)
        # double spinbox for float values
        elif editortype == 'doublespinbox':
            editor = QtWidgets.QDoubleSpinBox(parent)
        # default editor
        else:
            editor = QtWidgets.QStyledItemDelegate.createEditor(self, parent, option, index)
        
        # set min/max values for integer values if available
        if isinstance(editor, QtWidgets.QSpinBox) or isinstance(editor, QtWidgets.QDoubleSpinBox):
            min = index.model().editorMinValue(index.row(), index.column())
            if min != None:
                editor.setMinimum(min)
            max = index.model().editorMaxValue(index.row(), index.column())
            if max != None:
                editor.setMaximum(max)
            step = index.model().editorStep(index.column())
            if step != None:
                editor.setSingleStep(step)
            
        # set decimal value for float values if available
        if isinstance(editor, QtWidgets.QDoubleSpinBox):
            dec = index.model().editorDecimals(index.column())
            if dec != None:
                editor.setDecimals(dec)

        return editor

    def setEditorData(self, editor, index):
        #if index.model().columns[index.column()]['editor'] == 'combobox':
        if isinstance(editor, QtWidgets.QComboBox):
            locale = QtCore.QLocale()
            idx = 0
            # get data
            d = index.model().data(index, QtCore.Qt.DisplayRole)
            if d != None:
                if type(d) is str:
                    # find matching list item text
                    idx = editor.findText(d)
                    if idx == -1:
                        idx = 0
                else:
                    # find the closest matching index
                    closest = lambda a,l:min(enumerate(l),key=lambda x:abs(x[1]-a))
                    # get item list
                    itemlist = []
                    for i in range(editor.count()):
                        txt = editor.itemText(i)
                        itemlist.append(float(txt))
                    # find index
                    idx = closest(float(d), itemlist)[0]
            
            editor.setCurrentIndex(idx)
            return
        QtWidgets.QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        #if model.columns[index.column()]['editor'] == 'combobox':
        if isinstance(editor, QtWidgets.QComboBox):
            model.setData(index, editor.currentText(), QtCore.Qt.EditRole)
            #model.reset()
            return
        QtWidgets.QStyledItemDelegate.setModelData(self, editor, model, index)

    def emitCommitData(self):
        self.emit(QtCore.SIGNAL('commitData(QWidget*)'), self.sender())

    def displayText(self, value, locale):
        if type(value) is float and self.displayDecimals != None:
            s = locale.toString(value, 'f', self.displayDecimals)
            return s
        return QtWidgets.QStyledItemDelegate.displayText(self, value, locale)
        
    def paint(self, painter, options, index):
        # keep the number of decimals to display
        dec = index.model().editorDecimals(index.column())
        if dec != None:
            self.displayDecimals = dec
        else:
            self.displayDecimals = None
        return QtWidgets.QStyledItemDelegate.paint(self, painter, options, index)
        
        