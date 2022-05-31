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

from displays.scope2 import ScopeDisplay
from amplifiers.lsl.lslamp import AMP_LabStreamingLayer
from displays.fft import FFT_RMS
from filter.filter import FLT_Eeg

def InstantiateModules(run_as):
    ''' Instantiate and arrange module objects. 
    Modules will be connected top -> down, starting with array index 0. 
    Additional modules can be connected left -> right with tuples as list objects.
    @param run_as: command line option (-r, --runas) for different module configurations 
    @return: list with instantiated module objects 
    '''
    modules = [
                AMP_LabStreamingLayer(),
                FLT_Eeg(),
                FFT_RMS(),
                ScopeDisplay()
                ]
    return modules



