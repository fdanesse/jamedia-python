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


class VideoOutput(Gst.Pipeline):

    def __init__(self, sink, config):

        Gst.Pipeline.__init__(self, "VideoOutput")
        
        self.__config = config
        self.__gtkSink = sink
        
        self.__videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')

        # self.__subparse = Gst.ElementFactory.make('subparse', 'subparse')
        # FIXME: Subtítulos no funcionan
        # self.__subtitleoverlay = Gst.ElementFactory.make('subtitleoverlay', 'subtitleoverlay')

        self.__videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        caps = Gst.Caps.from_string('video/x-raw,pixel-aspect-ratio=1/1')
        self.__capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        self.__capsfilter.set_property("caps", caps)
        self.__videorate = Gst.ElementFactory.make('videorate', 'videorate')
        self.__videorate.set_property('skip-to-first', True)  # No pruce datos hasta el primer frame recibido
        self.__videorate.set_property('drop-only', True)  # No pasa imagenes duplicadas
        self.__videorate.set_property('max-rate', 30)
        self.__videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
        self.videobalance = Gst.ElementFactory.make('videobalance', "videobalance")
        self.gamma = Gst.ElementFactory.make('gamma', "gamma")
        self.videoflip = Gst.ElementFactory.make('videoflip',"videoflip")

        self.add(self.__videoqueue)
        # FIXME: Subtítulos no funcionan self.add(self.__subtitleoverlay)
        self.add(self.__videoconvert)
        self.add(self.__capsfilter)
        self.add(self.__videorate)
        self.add(self.__videoscale)
        self.add(self.videobalance)
        self.add(self.gamma)
        self.add(self.videoflip)
        self.add(self.__gtkSink)

        # FIXME: Subtítulos no funcionan self.__videoqueue.link(self.__subtitleoverlay)
        # FIXME: Subtítulos no funcionan self.__subtitleoverlay.link(self.__videoconvert)
        self.__videoqueue.link(self.__videoconvert)
        self.__videoconvert.link(self.__capsfilter)
        self.__capsfilter.link(self.__videorate)
        self.__videorate.link(self.__videoscale)
        self.__videoscale.link(self.videobalance)
        self.videobalance.link(self.gamma)
        self.gamma.link(self.videoflip)
        self.videoflip.link(self.__gtkSink)

        pad = self.__videoqueue.get_static_pad("sink")
        self.add_pad(Gst.GhostPad.new("sink", pad))
