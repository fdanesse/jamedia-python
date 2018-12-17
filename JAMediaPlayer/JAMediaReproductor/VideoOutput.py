# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GstVideo

Gst.init([])


class VideoOutput(Gst.Pipeline):

    def __init__(self, sink):

        Gst.Pipeline.__init__(self, "VideoOutput")
        
        self.__gtkSink = sink
        
        # self.__subparse = Gst.ElementFactory.make('subparse', 'subparse')
        # FIXME: Subtítulos no funcionan
        # self.__subtitleoverlay = Gst.ElementFactory.make('subtitleoverlay', 'subtitleoverlay')

        self.__videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        self.videobalance = Gst.ElementFactory.make('videobalance', "videobalance")
        self.gamma = Gst.ElementFactory.make('gamma', "gamma")
        self.videoflip = Gst.ElementFactory.make('videoflip',"videoflip")
        caps = Gst.Caps.from_string('video/x-raw,pixel-aspect-ratio=1/1')  # Corrige un BUG: http://gstreamer-devel.966125.n4.nabble.com/master-vs-1-5-1-changing-video-size-on-compositor-input-td4673354.html
        self.__capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        self.__capsfilter.set_property("caps", caps)

        # FIXME: Subtítulos no funcionan self.add(self.__subtitleoverlay)
        self.add(self.__videoconvert)
        self.add(self.videobalance)
        self.add(self.gamma)
        self.add(self.videoflip)
        self.add(self.__capsfilter)
        self.add(self.__gtkSink)

        # FIXME: Subtítulos no funcionan self.__videoqueue.link(self.__subtitleoverlay)
        # FIXME: Subtítulos no funcionan self.__subtitleoverlay.link(self.__videoconvert)
        self.__videoconvert.link(self.videobalance)
        self.videobalance.link(self.gamma)
        self.gamma.link(self.videoflip)
        self.videoflip.link(self.__capsfilter)
        self.__capsfilter.link(self.__gtkSink)

        pad = self.__videoconvert.get_static_pad("sink")
        self.add_pad(Gst.GhostPad.new("sink", pad))
