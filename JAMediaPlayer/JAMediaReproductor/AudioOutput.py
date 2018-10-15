# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GstVideo

GObject.threads_init()
Gst.init("--opengl-hwdec-interop=vaapi-glx")

# Equalizer: https://gstreamer.freedesktop.org/documentation/tutorials/playback/custom-playbin-sinks.html#page-description


class AudioOutput(Gst.Pipeline):

    def __init__(self, config):

        Gst.Pipeline.__init__(self, "AudioOutput")
        
        self.__config = config

        self.__audioqueue = Gst.ElementFactory.make('queue', 'audioqueue')
        #self.__audioqueue.set_property("min-threshold-buffers", 500)
        self.__audioresample = Gst.ElementFactory.make('audioresample', "audioresample")
        self.__audioresample.set_property("quality", 10)
        self.__equalizer = Gst.ElementFactory.make('equalizer-10bands', 'equalizer')
        self.__audiosink = Gst.ElementFactory.make('autoaudiosink', 'audiosink')
        
        self.add(self.__audioqueue)
        self.add(self.__audioresample)
        self.add(self.__equalizer)
        self.add(self.__audiosink)

        self.__audioqueue.link(self.__audioresample)
        self.__audioresample.link(self.__equalizer)
        self.__equalizer.link(self.__audiosink)

        pad = self.__audioqueue.get_static_pad("sink")
        self.add_pad(Gst.GhostPad.new("sink", pad))

    def setting(self, config):
        for key in config.keys():
            if self.__config[key] != config[key]:
                self.__config[key] = config[key]
                self.__equalizer.set_property(key, self.__config[key])

'''
band0               : gain for the frequency band 29 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band1               : gain for the frequency band 59 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band2               : gain for the frequency band 119 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band3               : gain for the frequency band 237 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band4               : gain for the frequency band 474 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band5               : gain for the frequency band 947 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band6               : gain for the frequency band 1889 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band7               : gain for the frequency band 3770 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band8               : gain for the frequency band 7523 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
band9               : gain for the frequency band 15011 Hz, ranging from -24 dB to +12 dB
                    flags: legible, escribible, controlable
                    Double. Range:             -24 -              12 Default:               0 
'''