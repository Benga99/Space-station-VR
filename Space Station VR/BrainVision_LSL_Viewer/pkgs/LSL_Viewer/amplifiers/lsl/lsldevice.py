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

from pylsl import StreamInlet
from pylsl import proc_ALL, proc_clocksync, proc_threadsafe, proc_monotonize, proc_none

from lxml import etree
from lxml import objectify 
import time
import numpy as np
import collections
import threading

# Connection state
class ConnectionState(object):
    CS_DISCONNECTED = 0                         # Device is disconnected
    CS_RECONNECT = 1                            # Device is currently disconnected and the library tries to reconnect the device
    CS_CONNECTED = 2                            # Device is connected


# Signal quality
class SignalQuality(object):
    SQ_NOINFO = 0
    SQ_GOOD = 1
    SQ_MEDIUM = 2
    SQ_BAD = 3

class Channel(object):
    def __init__(self, label, type, unit, enable):
        self.Label = label
        self.Type = type
        self.Unit = unit
        self.Enable = enable

class AmpError(Exception):
    ''' Generic amplifier exception
    '''
    def __init__(self, value, errornr = 0):
        errortext = ""
        errortext = errortext + " : %i"%(errornr)
        if errornr != 0:
            self.value = "LSL: " + str(value) + " -> " + errortext
        else:
            self.value = "LSL: " + str(value)
    def __str__(self):
        return self.value



class LSL_Device:
    def __init__(self, isMarkerDevice=False):
        self.inlet = None
        self.Channels = []
        self.running = False
        self.channelSlice = []
        self.isMarkerDevice = isMarkerDevice
        self.lastSampleTime = 0
        self.sampleTime = 0
        self.Markers = collections.deque()
        self.worker = None
        self.watchDog = time.clock()

    def Create(self, streaminfo):
        self.StreamInfo = streaminfo
        #print(streaminfo.as_xml())
        try:
            if self.isMarkerDevice:
                proc = proc_clocksync
                chunk = 0
                #proc = proc_clocksync | proc_threadsafe
            else:
                proc = proc_clocksync
                chunk = int(streaminfo.nominal_srate() * 0.03) # 30 ms chunk size
            #proc = proc_none
            self.inlet = StreamInlet(streaminfo, max_chunklen=chunk, processing_flags=proc, max_buflen=100)
            self.getChannelInfo(self.inlet.info(timeout=2.0))
            #print(self.inlet.info().as_xml())
        except Exception as e:
            self.inlet = None
            raise AmpError("failed to open LSL stream: %s"%str(e))
        return self.inlet is not None

    def Start(self):
        if self.inlet is None:
            raise AmpError("failed to start, no EEG stream available")
        self.currentSampleCounter = 0
        self.currentSampleTime = 0.0
        self.running = True
        self.errorCounter = -1
        self.watchDog = time.clock()
        if self.SampleRate > 0:
            self.sampleTime = 1.0 / self.SampleRate
        else:
            self.sampleTime = 1.0

        # create the slice for enabled channels
        self.channelSlice = []
        for c in range(len(self.Channels)):
            if self.Channels[c].Enable:
                self.channelSlice.append(c)

        # create the worker thread for marker streams
        if self.isMarkerDevice:
            self.Markers.clear()
            self.worker = threading.Thread(target=self.workerThread)  
            self.worker.start()
        else:
            self.worker = None


    def Stop(self):
        self.running = False
        if not self.worker is None:
            self.worker.join(2.0)
            self.worker = None

    def workerThread(self):
        while self.running:
            try:
                samples, timestamps = self.inlet.pull_chunk(timeout=0.005, max_samples=100)
                if samples:
                    for n in range(len(samples)):
                        sample = samples[n]
                        timestamp = timestamps[n]
                        if sample and timestamp:
                            marker = (timestamp, str(sample[0]))
                            self.Markers.append(marker)
            except:
                pass


    def getChannelInfo(self, streaminfo):
        defaultType = 'unknown'
        defaultUnits = 'unknown'
        if streaminfo.type() == "EEG":
            defaultType = 'EEG'
            defaultUnits = 'microvolts'

        xml = streaminfo.as_xml()
        root = objectify.fromstring(xml)
        #print(objectify.dump(root))
        self.Channels = []
        numchannels = root.channel_count.pyval
        try:
            channels = root.xpath("//info/desc/channels")[0]
            for idx, channel in enumerate(channels.iterchildren()):
                # set default values
                label = 'C%i'%(idx+1)
                ctype = defaultType
                unit = defaultUnits
                # get the values from xml
                try:
                    label = channel.label.pyval
                except:
                    pass
                try:
                    ctype = channel.type.pyval
                except:
                    pass
                try:
                    unit = channel.unit.pyval
                except:
                    pass
                c = Channel(label, ctype, unit, True)
                if idx < numchannels:
                    self.Channels.append(c)
        except :
            pass
        # fill in missing channels 
        for n in range(len(self.Channels), numchannels):
            label = 'C%i'%(n+1)
            ctype = defaultType
            unit = defaultUnits
            c = Channel(label, ctype, unit, True)
            self.Channels.append(c)

    def ReadData(self):
        ''' Read data from device
        @return: list of np arrays for channel data, trigger channel, sample counter and time stamps
        '''
        if self.inlet is None or not self.running or self.isMarkerDevice:
            return None

        channels = len(self.Channels)

        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=8000)
        if not samples:
            return None
        x = np.array(samples)
        y = x.reshape(-1, channels).transpose()

        # select and format the data
        eeg = np.array(y[self.channelSlice], np.float)
        ts = np.array(timestamps, np.float)

        # check for lost samples
        dts = np.diff(ts, prepend=self.lastSampleTime)
        dtsabs = np.abs(dts)
        scadd = np.floor(dts / self.sampleTime)
        scadd[np.nonzero(dtsabs < self.sampleTime * 2.0)] = 0.0
        #lost = int(np.sum(scadd))
        #if lost > 0:
            #print("Samples lost: ", lost)
            #print(scadd)
            #print(dts)
        self.lastSampleTime = ts[-1]


        # TODO: Remove this: replace first channel data with jitter values [ms] for testing only. 
        # 
        #eeg[0] = dts * 1000.0
        
        # dummy trigger
        trg = np.zeros((1, eeg.shape[1]), np.uint32)
        
        # dummy sample counter
        sct = np.arange(self.currentSampleCounter, self.currentSampleCounter + eeg.shape[1], 1, np.int64)
        #sct += np.cumsum(scadd).astype(np.int64)
        self.currentSampleCounter = sct[-1] + 1
        sct = sct.reshape((1,-1))
        
        # feed the dog
        self.watchDog = time.clock()
        
        d = []
        d.append(eeg)
        d.append(trg)
        d.append(sct)
        d.append(ts)
        return d

    def ReadMarkers(self):
        markers = []
        for n in range(len(self.Markers)):
            markers.append(self.Markers.pop())
        return markers

        '''
        if self.inlet is None or not self.running or not self.isMarkerDevice:
            return markers
        t = time.clock()
        samples, timestamps = self.inlet.pull_chunk(timeout=0.0, max_samples=5000)
        #print("%.1f ms"%((time.clock()-t) * 1000))
        if not samples:
            return markers
        for n in range(len(samples)):
            sample = samples[n]
            timestamp = timestamps[n]
            #if sample and len(sample[0]) > 0 and timestamp:
            if sample and timestamp:
                markers.append((timestamp, str(sample[0])))
        return markers
        '''


    @property
    def ConnectionState(self):
        if self.inlet is None:
            state = ConnectionState.CS_DISCONNECTED
        else:
            if self.running and time.clock() > self.watchDog + 4:
                state = ConnectionState.CS_RECONNECT
            else:
                state = ConnectionState.CS_CONNECTED
        return state

    @property
    def SignalQuality(self):
        if self.inlet is None:
            quality = SignalQuality.SQ_NOINFO
        else:
            quality = SignalQuality.SQ_GOOD
        return quality

    @property
    def SampleRate(self):
        sr = self.StreamInfo.nominal_srate()
        return sr

    @property
    def DeviceInfoString(self):
        return "- %s %s %s"%(self.StreamInfo.name(), self.StreamInfo.type(), self.StreamInfo.source_id())



