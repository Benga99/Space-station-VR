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

from ctypes import windll,c_bool,c_uint,byref
from os import getpid

GetPriorityClass    = windll.kernel32.GetPriorityClass
SetPriorityClass    = windll.kernel32.SetPriorityClass
OpenProcess         = windll.kernel32.OpenProcess
CloseHandle         = windll.kernel32.CloseHandle
GetProcessAffinityMask = windll.kernel32.GetProcessAffinityMask
SetProcessAffinityMask = windll.kernel32.SetProcessAffinityMask

class Priorities():
    ABOVE_NORMAL_PRIORITY_CLASS     = 0x8000
    BELOW_NORMAL_PRIORITY_CLASS     = 0x4000
    HIGH_PRIORITY_CLASS             = 0x0080
    IDLE_PRIORITY_CLASS             = 0x0040
    NORMAL_PRIORITY_CLASS           = 0x0020
    REALTIME_PRIORITY_CLASS         = 0x0100
    order = [0x0040,0x4000,0x0020,0x8000,0x0080,0x0100]
    reverseOrder = {'0x40':0,'0x4000':1,'0x20':2,'0x8000':3,'0x80':4,'0x100':5}

__shouldClose = [False]

def getProcessHandle( process, inherit = False ):
    __shouldClose[ 0 ] = True
    if not process:
        process = getpid()
    return OpenProcess( c_uint( 0x0200 | 0x0400 ), c_bool( inherit ), c_uint( process ) )

def SetPriorityById( priority, process = None, inherit = False ):
    return SetPriority( priority, getProcessHandle( process, inherit ) )

def SetPriority( priority, process = None, inherit = False ):
    if not process:
        process = getProcessHandle( None, inherit )
    result = SetPriorityClass( process, c_uint( priority ) ) != 0
    if __shouldClose:
        CloseHandle(process)
        __shouldClose[ 0 ] = False
    return result

def IncreasePriorityById( process = None, inherit = False, times = 1 ):
    return IncreasePriority( getProcessHandle( process, inherit, times ) )

def IncreasePriority( process = None, inherit = False, times = 1 ):
    if times <1:
        raise ValueError("Wrong value for the number of increments")
    if not process:
        process = getProcessHandle( None, inherit )
    currentPriority = Priorities.reverseOrder[ hex( GetPriorityClass (process) ) ]
    if currentPriority < ( len( Priorities.order ) - 1 ):
        return SetPriority( Priorities.order[ min( currentPriority + times, len( Priorities.order ) - 1) ], process )
    return False

def DecreasePriorityById( process = None, inherit = False, times = 1 ):
    return DecreasePriority( getProcessHandle( process, inherit, times ) )

def DecreasePriority( process = None, inherit = False, times = 1 ):
    if times <1:
        raise ValueError("Wrong value for the number of decrements")
    if not process:
        process = getProcessHandle( None, inherit )
    currentPriority = Priorities.reverseOrder[ hex( GetPriorityClass( process ) ) ]
    if currentPriority > 0:
        return SetPriority( Priorities.order[ max(0,currentPriority - times) ], process )
    return False

def LimitProcessors(process = None, inherit = False):
    # limit the process to the first two available processors
    if not process:
        process = getProcessHandle( None, inherit )

    pmask = c_uint()
    smask = c_uint()
    GetProcessAffinityMask(process, byref(pmask), byref(smask))
    smask = smask.value
    pmask = 0
    mask = 1
    cpu = 0
    while mask < 0x8000 and cpu < 2:
        if smask & mask:
            pmask |= mask
            cpu += 1
        mask = mask << 1

    #result = SetPriorityClass( process, c_uint( priority ) ) != 0
    result = SetProcessAffinityMask(process, c_uint(pmask))

    if __shouldClose:
        CloseHandle(process)
        __shouldClose[ 0 ] = False
    return result

    #kernel32.SetProcessAffinityMask(p, pmask)
    #print("INFO: Available CPUs (bit mask) 0x%04X, Python process limited to 0x%04X"%(smask, pmask))
