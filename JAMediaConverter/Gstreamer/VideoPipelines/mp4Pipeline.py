# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import Gst
from gi.repository import GstVideo

# streaming: https://gist.github.com/CreaRo/bb2103d296fd2c5c3b39d4b82250b68a


class mp4Pipeline(Gst.Pipeline):

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "mp4Pipeline")

        self.set_name("mp4Pipeline")

        self.__codec = "mp4"
        self.__origen = origen

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(self.__origen)
        if "." in location:
            extension = ".%s" % self.__origen.split(".")[-1]
            location = location.replace(extension, ".%s" % self.__codec)
        else:
            location = "%s.%s" % (location, self.__codec)

        self.__newpath = os.path.join(dirpath_destino, location)

        # ORIGEN (Siempre un archivo)
        filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        decodebin = Gst.ElementFactory.make("decodebin", "decodebin")

        # VIDEO
        videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        x264enc = Gst.ElementFactory.make("x264enc", "x264enc")
    
        # AUDIO
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        lamemp3enc = Gst.ElementFactory.make("lamemp3enc", "lamemp3enc")

        # SALIDA
        mp4mux = Gst.ElementFactory.make("mp4mux", "mp4mux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(filesrc)
        self.add(decodebin)

        self.add(videoconvert)
        self.add(x264enc)

        self.add(audioconvert)
        self.add(lamemp3enc)

        self.add(mp4mux)
        self.add(filesink)

        filesrc.link(decodebin)

        videoconvert.link(x264enc)
        x264enc.link(mp4mux)
        mp4mux.link(filesink)

        audioconvert.link(lamemp3enc)
        lamemp3enc.link(mp4mux)

        self.__videoSink = videoconvert.get_static_pad("sink")
        self.__audioSink = audioconvert.get_static_pad("sink")

        filesink.set_property("location", self.__newpath)
        filesrc.set_property("location", self.__origen)
        # FIXME: Agregar informe en
        decodebin.connect('pad-added', self.__on_pad_added)

        self._bus = self.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.busMessageCb)

    def getSinks(self):
        return self.get_by_name("decodebin"), self.__videoSink, self.__audioSink

    def __on_pad_added(self, uridecodebin, pad):
        # Agregar elementos en forma dinámica https://wiki.ubuntu.com/Novacut/GStreamer1.0
        string = pad.query_caps(None).to_string()
        if string.startswith('audio/'):
            #pad.link(self.__audioSink)
            print("AUDIO:\n", string)
        elif string.startswith('video/'):
            #pad.link(self.__videoSink)
            print("VIDEO:\n", string)

    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            #print("STATE_CHANGED:", old, new, pending)
        elif mensaje.type == Gst.MessageType.EOS:
            print("END")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, valor1 = self.query_duration(Gst.Format.TIME)
            bool2, valor2 = self.query_position(Gst.Format.TIME)
            print("DURATION_CHANGED:", valor1, valor2)
        elif mensaje.type == Gst.MessageType.ERROR:
            print("ERROR:", str(mensaje.parse_error()))
        
    def __del__(self):
        print("DESTROY OK")
