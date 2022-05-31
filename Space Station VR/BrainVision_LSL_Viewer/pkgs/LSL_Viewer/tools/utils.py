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

import os, sys, traceback
import re

def GetExceptionTraceBack():
    ''' Get last trace back info as tuple
    @return: tuple(string representation, filename, line number, module)
    '''
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    tb = traceback.extract_tb(exceptionTraceback)[-1]
    fn = os.path.split(tb[0])[1]
    txt = "%s, %d, %s"%(fn, tb[1], tb[2])
    return tuple([txt, fn, tb[1], tb[2]])

def Flatten(lst):
    ''' Flatten a list containing lists or tuples
    '''
    for elem in lst:
        if type(elem) in (tuple, list):
            for i in Flatten(elem):
                yield i
        else:
            yield elem

def cmp(a, b):
    ''' Python 3 replacement for cmp function '''
    return (a > b) - (a < b) 

def CompareVersion(a, b, n=3):
    ''' Compare two version numbers
    @param a: version number 1
    @param b: version number 2
    @param n: number of categories to compare
    @return:  -1 if a<b, 0 if a=b, 1 if a>b
    '''
    def fixup(i):
        try:
            return int(i)
        except ValueError:
            return i
    a = list(map(fixup, re.findall("\d+|\w+", a)))
    b = list(map(fixup, re.findall("\d+|\w+", b)))
    return cmp(a[:n], b[:n])


