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

'''
                      / videoscale | capsfilter | mpeg2enc \
filesrc | decodebin --                                       -- mpegpsmux | filesink
                      \ audioconvert | twolamemp2enc ----- /
'''


class mpgPipeline(Gst.Pipeline):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "mpgPipeline")

        self.__controller = None
        self.__codec = "mpg"
        self.__origen = origen
        self.__duration = 0
        self.__position = 0

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(self.__origen)
        informeName = self.__origen
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

        self.__videoSink = None
        self.__audioSink = None
        self.__bus = None

        self.__Init()

    def __emit_info(self, informemodel, info):
        self.emit("info", info)

    def __Init(self):
        # ORIGEN (Siempre un archivo)
        filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        decodebin = Gst.ElementFactory.make("decodebin", "decodebin")

        # VIDEO
        videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
        self.__capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        mpeg2enc = Gst.ElementFactory.make("mpeg2enc", "mpeg2enc")

        # AUDIO
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        twolamemp2enc = Gst.ElementFactory.make("twolamemp2enc", "twolamemp2enc")

        # SALIDA
        mpegpsmux = Gst.ElementFactory.make("mpegpsmux", "mpegpsmux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(filesrc)
        self.add(decodebin)
        self.add(videoscale)
        self.add(self.__capsfilter)
        self.add(mpeg2enc)
        self.add(audioconvert)
        self.add(twolamemp2enc)
        self.add(mpegpsmux)
        self.add(filesink)

        filesrc.link(decodebin)
        videoscale.link(self.__capsfilter)
        self.__capsfilter.link(mpeg2enc)
        audioconvert.link(twolamemp2enc)
        mpeg2enc.link(mpegpsmux)
        twolamemp2enc.link(mpegpsmux)
        mpegpsmux.link(filesink)

        self.__videoSink = videoscale.get_static_pad("sink")
        self.__audioSink = audioconvert.get_static_pad("sink")

        filesink.set_property("location", self.__newpath)
        filesrc.set_property("location", self.__origen)
        decodebin.connect('pad-added', self.__on_pad_added)

        self.__bus = self.get_bus()
        #self.__bus.add_signal_watch()
        #self.__bus.connect("message", self.busMessageCb)
        self.__bus.enable_sync_message_emission()
        self.__bus.connect("sync-message", self.busMessageCb)

        self.use_clock(None)

    def __on_pad_added(self, decodebin, pad):
        # FIXME: 1279 * 720 **ERROR: [python3] horizontal_size must be a even (4:2:0 / 4:2:2)
        # https://en.wikipedia.org/wiki/Chroma_subsampling  http://www.cinedigital.tv/que-es-todo-eso-de-444-422-420-o-color-subsampling/
        # Bug en la negociación automática de gstreamer. En el caso analizado, se recibe: width=(int)1279, height=(int)720
        # Pero se corrige al cambiar el ancho por 1280 lo cual es: Maximal output width of 1280 horizontal pixels - De-Interlacing and YUV 4:2:2 to 4:2:0 Conversion Algorithm
        # Se corrige con videorate y filtrando con pixel-aspect-ratio=(fraction)1/1
        tpl_property = pad.get_property("template")  # https://lazka.github.io/pgi-docs/Gst-1.0/classes/PadTemplate.html
        currentcaps = pad.get_current_caps().to_string()
        if currentcaps.startswith('video/'):
            self.__informeModel.setInfo("archivo", self.__origen)
            self.__informeModel.setInfo("codec",self.__codec)
            self.__informeModel.setInfo("formato inicial", self.__tipo)
            self.__informeModel.setInfo("entrada de video", currentcaps)           
            width, height = getSize(currentcaps)
            self.__informeModel.setInfo("relacion", float(width)/float(height))
            caps = Gst.Caps.from_string('video/x-raw, pixel-aspect-ratio=(fraction)1/1, width=(int)%s, height=(int)%s' % (width, height))  #framerate=(fraction)24000/1001
            self.__capsfilter.set_property("caps", caps)
            pad.link(self.__videoSink)
        elif currentcaps.startswith('audio/'):
            self.__informeModel.setInfo("entrada de sonido", currentcaps)
            pad.link(self.__audioSink)

    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.__t1 = datetime.datetime.now()

        elif mensaje.type == Gst.MessageType.EOS:
            self.__endProcess()

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__errorProcess(str(mensaje.parse_error()))

    def __endProcess(self):
        self.__t2 = datetime.datetime.now()
        self.__timeProcess = self.__t2 - self.__t1
        self.__informeModel.setInfo('tiempo de proceso', str(self.__timeProcess))
        self.emit("end")
        self.stop()
        
    def __errorProcess(self, error):
        self.__informeModel.setInfo('errores', error)
        self.emit("error", "ERROR en: " + self.__origen + ' => ' + error)
        self.stop()

    def stop(self):
        self.__new_handle(False)
        self.set_state(Gst.State.NULL)
        if os.path.exists(self.__newpath):
            statinfo = os.stat(self.__newpath)
            if not statinfo.st_size:
                os.remove(self.__newpath)

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
