# -*- coding: utf-8 -*-

import os
import datetime

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GstVideo
from gi.repository import GLib
from JAMediaPlayer.Globales import MAGIC
from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
from JAMediaConverter.Gstreamer.Globales import format_ns, getSize

GObject.threads_init()
Gst.init("--opengl-hwdec-interop=vaapi-glx")


class audioBin1(Gst.Bin):
    def __init__(self, path, codec):
        Gst.Bin.__init__(self, "audioBin1")

        audioresample = Gst.ElementFactory.make('audioresample', "audioresample")
        audioresample.set_property("quality", 10)
        audiorate = Gst.ElementFactory.make('audiorate', "audiorate")

        enc = None
        if codec == "wav":
            enc = Gst.ElementFactory.make('wavenc', 'wavenc')
        elif codec == "mp3":
            enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')

        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        self.add(audioresample)
        self.add(audiorate)
        self.add(enc)
        self.add(filesink)

        audioresample.link(audiorate)
        audiorate.link(enc)
        enc.link(filesink)

        self.add_pad(Gst.GhostPad.new("sink", audioresample.get_static_pad("sink")))

        filesink.set_property("location", path)


class audioBin2(Gst.Bin):
    def __init__(self, path):
        Gst.Bin.__init__(self, "audioBin2")

        audioresample = Gst.ElementFactory.make('audioresample', "audioresample")
        audioresample.set_property("quality", 10)
        audiorate = Gst.ElementFactory.make('audiorate', "audiorate")
        enc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')
        mux = Gst.ElementFactory.make('oggmux', 'oggmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        self.add(audioresample)
        self.add(audiorate)
        self.add(enc)
        self.add(mux)
        self.add(filesink)

        audioresample.link(audiorate)
        audiorate.link(enc)
        enc.link(mux)
        mux.link(filesink)

        self.add_pad(Gst.GhostPad.new("sink", audioresample.get_static_pad("sink")))

        filesink.set_property("location", path)


class audioBin(Gst.Pipeline):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, dirpath_destino, codec):
        Gst.Pipeline.__init__(self, "audioBin")

        self.__controller = None
        self.__codec = codec
        self.__origen = origen
        self.__dirpath_destino = dirpath_destino
        self.__duration = 0
        self.__position = 0

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(self.__origen)
        informeName = location
        if "." in location:
            extension = ".%s" % self.__origen.split(".")[-1]
            informeName = location.replace(extension, "")
            location = location.replace(extension, ".%s" % self.__codec)
        else:
            location = "%s.%s" % (location, self.__codec)

        self.__tipo = MAGIC.file(origen)
        self.__status = Gst.State.NULL
        self.__t1 = None
        self.__t2 = None
        self.__timeProcess = None
        self.__informeModel = InformeTranscoderModel(self.__codec + "-" + informeName)
        self.__informeModel.connect("info", self.__emit_info)
        self.__newpath = os.path.join(dirpath_destino, location)

        self.__videoSink = Gst.ElementFactory.make('fakesink', 'fakesink')

        self.__audioSink = None
        if codec == "wav" or codec == "mp3":
            self.__audioSink = audioBin1(self.__newpath, codec)
        elif codec == "ogg":
            self.__audioSink = audioBin2(self.__newpath)

        self.__pipe = Gst.ElementFactory.make('playbin', 'playbin')
        self.add(self.__pipe)
        self.__pipe.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
        self.__pipe.set_property('audio-sink', self.__audioSink)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.busMessageCb)

        self.__pipe.set_property("uri", Gst.filename_to_uri(self.__origen))
        #uridecodebin.connect('pad-added', self.__on_pad_added)
        self.use_clock(None)

    def __emit_info(self, informemodel, info):
        self.emit("info", info)
        
    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.__informar()
                    self.__t1 = datetime.datetime.now()

        elif mensaje.type == Gst.MessageType.EOS:
            self.__t2 = datetime.datetime.now()
            self.__timeProcess = self.__t2 - self.__t1
            self.__informeModel.setInfo('tiempo de proceso', str(self.__timeProcess))
            self.stop()
            self.emit("end")

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__informeModel.setInfo('errores', str(mensaje.parse_error()))
            self.stop()
            self.emit("error", "ERROR en: " + self.__newpath + ' => ' + str(mensaje.parse_error()))
        
    '''def __del__(self):
        print("CODEC PIPELINE DESTROY")'''

    def __informar(self):
        pad = self.__pipe.emit('get-video-pad',0)
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('video/'):
                self.__informeModel.setInfo("archivo", self.__origen)
                self.__informeModel.setInfo("codec",self.__codec)
                self.__informeModel.setInfo("formato inicial", self.__tipo)
                self.__informeModel.setInfo("entrada de video", currentcaps)           
                width, height = getSize(currentcaps)
                self.__informeModel.setInfo("relacion", float(width)/float(height))
        pad = self.__pipe.emit('get-audio-pad',0) 
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('audio/'):
                self.__informeModel.setInfo("entrada de sonido", currentcaps)
                pass

    def stop(self):
        self.__new_handle(False)
        self.set_state(Gst.State.NULL)

    def play(self):
        self.__new_handle(True)
        self.set_state(Gst.State.PLAYING)

    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(300, self.__handle)

    def __handle(self):
        bool1, valor1 = self.query_duration(Gst.Format.TIME)
        if self.__duration != valor1:
            self.__duration = valor1
            self.__informeModel.setInfo("duracion", "{0}".format(format_ns(self.__duration)))

        bool2, valor2 = self.query_position(Gst.Format.TIME)
        pos = 0
        try:
            pos = int(float(valor2) * 100 / float(valor1))
        except:
            pass
        if pos != self.__position:
            self.__position = pos
            self.emit("progress", self.__position, self.__codec)
        return True

GObject.type_register(audioBin)