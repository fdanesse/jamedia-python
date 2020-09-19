# -*- coding: utf-8 -*-

import os
import datetime

import gi
gi.require_version("Gst", "1.0")

from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GLib
from JAMediaPlayer.Globales import MAGIC
from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
from JAMediaConverter.Gstreamer.Globales import format_ns, getSize

Gst.init(None)

# NOTA: Segun testeo: 100 imagenes x segundo 42.5Mb


class ImageBin1(Gst.Bin):

    def __init__(self):

        Gst.Bin.__init__(self) # FIXME: "ImageBin1"
 
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property("max-rate", 30)
        pngenc = Gst.ElementFactory.make('pngenc', 'pngenc')
        multifilesink = Gst.ElementFactory.make('multifilesink', 'multifilesink')
        
        self.add(videoconvert)
        self.add(videorate)
        self.add(pngenc)
        self.add(multifilesink)

        videoconvert.link(videorate)
        videorate.link(pngenc)
        pngenc.link(multifilesink)

        self.add_pad(Gst.GhostPad.new("sink", videoconvert.get_static_pad("sink")))


class ImagenBin(Gst.Pipeline):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self)  # FIXME: "ImagenBin"

        self.__controller = None
        self.__codec = "png"
        self.__origen = origen
        self.__dirpath_destino = dirpath_destino
        self.__duration = 0
        self.__position = 0

        informeName = location = os.path.basename(self.__origen)
        if "." in location:
            extension = ".%s" % self.__origen.split(".")[-1]
            informeName = location = location.replace(extension, "")
        informeName = "%s_to_%s" % (informeName, self.__codec)

        self.__tipo = MAGIC.file(self.__origen)
        self.__status = Gst.State.NULL
        self.__t1 = None
        self.__t2 = None
        self.__timeProcess = None
        self.__informeModel = InformeTranscoderModel(self.__codec + "-" + informeName)

        self.__videoSink = ImageBin1()

        self.__pipe = Gst.ElementFactory.make('playbin', 'playbin')
        self.add(self.__pipe)
        self.__pipe.set_property('audio-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
        self.__pipe.set_property('video-sink', self.__videoSink)
        p = os.path.join(dirpath_destino, location)
        if not os.path.exists(p): os.mkdir(p)
        self.__videoSink.get_by_name('multifilesink').set_property('location', "%s/%s/img%s06d.png" % (dirpath_destino, location, "%"))

        self.__pipe.set_property("uri", Gst.filename_to_uri(self.__origen))

        self.__bus = self.get_bus()
        self.__bus.enable_sync_message_emission()
        self.__bus.connect("sync-message", self.busMessageCb)

        self.use_clock(None)
        
    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.__informar()
                    self.__t1 = datetime.datetime.now()

        elif mensaje.type == Gst.MessageType.EOS:
            self.__endProcess()

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__errorProcess(str(mensaje.parse_error()))

    def __informar(self):
        self.__informeModel.setInfo("archivo", self.__origen)
        self.__informeModel.setInfo("codec",self.__codec)
        self.__informeModel.setInfo("formato inicial", self.__tipo)
        pad = self.__pipe.emit('get-video-pad',0)
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('video/'):
                self.__informeModel.setInfo("entrada de video", currentcaps)           
                width, height = getSize(currentcaps)
                self.__informeModel.setInfo("relacion", float(width)/float(height))
        pad = self.__pipe.emit('get-audio-pad',0) 
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('audio/'):
                self.__informeModel.setInfo("entrada de sonido", currentcaps)

    def __endProcess(self):
        self.__t2 = datetime.datetime.now()
        self.__timeProcess = self.__t2 - self.__t1
        self.__informeModel.setInfo('tiempo de proceso', str(self.__timeProcess))
        self.emit("end")
        self.stop()
        
    def __errorProcess(self, error):
        self.__informeModel.setInfo('errores', error)
        self.emit("error", "ERROR en: " + self.__origen + "No se pudo convertir a: " + self.__codec + ' => ' + error)
        self.stop()

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
            self.__controller = GLib.timeout_add(200, self.__handle)

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

    def getInfo(self):
        return self.__origen, self.__tipo, self.__codec
