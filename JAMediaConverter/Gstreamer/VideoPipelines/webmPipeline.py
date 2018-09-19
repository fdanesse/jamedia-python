# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import Gst
from gi.repository import GstVideo


class webmPipeline(Gst.Pipeline):

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "webmPipeline")

        # FIXME: Suele suceder que no graba el video, solo una pantalla verde.
        # Encoder parameters: https://www.webmproject.org/docs/encoder-parameters/
        # vp8enc: https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good/html/gst-plugins-good-plugins-vp8enc.html

        # ejemplo de streaming en html: https://gist.github.com/vo/a0cc9313861888ad5180f442a4b7bf48
        # https://stackoverflow.com/questions/33306265/encode-decode-vp8-or-vp9-with-gstreamer
        # webmmux: https://developer.gnome.org/gst-plugins-libs/stable/gst-plugins-good-plugins-webmmux.html

        self.set_name("webmPipeline")

        self.__codec = "webm"
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
        # https://github.com/tamaggo/gstreamer-examples/blob/master/test_gst_appsrc_testvideo_mp4mux.py
        caps = Gst.Caps.from_string('video/x-raw,format=(string)I420')
        _filter = Gst.ElementFactory.make("capsfilter", "_filter")
        _filter.set_property("caps", caps)

        vp8enc = Gst.ElementFactory.make("vp8enc", "vp8enc")
        vp8enc.set_property("threads", 1)
        vp8enc.set_property("cq-level", 63)
        vp8enc.set_property("cpu-used", 0)
        videoqueue = Gst.ElementFactory.make("queue", "videoqueue")

        # AUDIO
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        vorbisenc = Gst.ElementFactory.make("vorbisenc", "vorbisenc")
        audioqueue = Gst.ElementFactory.make("queue", "audioqueue")

        # SALIDA
        webmmux = Gst.ElementFactory.make("webmmux", "webmmux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(filesrc)
        self.add(decodebin)

        self.add(videoconvert)
        self.add(_filter)
        self.add(vp8enc)
        self.add(videoqueue)

        self.add(audioconvert)
        self.add(vorbisenc)
        self.add(audioqueue)

        self.add(webmmux)
        self.add(filesink)

        filesrc.link(decodebin)

        videoconvert.link(_filter)
        _filter.link(vp8enc)
        vp8enc.link(videoqueue)
        videoqueue.link(webmmux)
        webmmux.link(filesink)

        audioconvert.link(vorbisenc)
        vorbisenc.link(audioqueue)
        audioqueue.link(webmmux)

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
        