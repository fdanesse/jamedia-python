# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html

import os

import gi
gi.require_version('Gst', '1.0')

from gi.repository import GObject
from gi.repository import Gst


class VideoOutput(Gst.Bin):

    def __init__(self, sink):

        Gst.Bin.__init__(self)
        # "VideoOutput"
        self.__gtkSink = sink
        #self.__gtkSink.set_property("pixel-aspect-ratio", Gst.Fraction(1, 1))
        self.__videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')
        self.__videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        caps = Gst.Caps.from_string('video/x-raw,pixel-aspect-ratio=1/1')  # Corrige un BUG: http://gstreamer-devel.966125.n4.nabble.com/master-vs-1-5-1-changing-video-size-on-compositor-input-td4673354.html
        self.__capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        self.__capsfilter.set_property("caps", caps)
        self.__videorate = Gst.ElementFactory.make('videorate', 'videorate')
        self.__videorate.set_property('skip-to-first', True)
        self.__videorate.set_property('drop-only', True)
        self.__videorate.set_property('max-rate', 30)
        self.videobalance = Gst.ElementFactory.make('videobalance', "videobalance")
        self.gamma = Gst.ElementFactory.make('gamma', "gamma")
        self.videoflip = Gst.ElementFactory.make('videoflip',"videoflip")

        self.add(self.__videoqueue)
        self.add(self.__videoconvert)
        self.add(self.__videorate)
        self.add(self.videobalance)
        self.add(self.gamma)
        self.add(self.videoflip)
        self.add(self.__capsfilter)
        self.add(self.__gtkSink)

        self.__videoqueue.link(self.__videoconvert)
        self.__videoconvert.link(self.__capsfilter)
        self.__capsfilter.link(self.__videorate)
        self.__videorate.link(self.videobalance)
        self.videobalance.link(self.gamma)
        self.gamma.link(self.videoflip)
        self.videoflip.link(self.__gtkSink)

        pad = self.__videoqueue.get_static_pad("sink")
        self.add_pad(Gst.GhostPad.new("sink", pad))
