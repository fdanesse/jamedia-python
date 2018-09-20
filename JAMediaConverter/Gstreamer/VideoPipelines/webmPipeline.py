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


def format_ns(ns):
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if not h:
        return "%02u:%02u" % (m, s)
    else:
        return "%02u:%02u:%02u" % (h, m, s)


def getSize(currentcaps):
    # video/x-raw(memory:VASurface), format=(string)NV12, width=(int)1279, height=(int)720, framerate=(fraction)30/1, interlace-mode=(string)progressive, pixel-aspect-ratio=(fraction)1/1
    items = currentcaps.split(",")
    width = 0
    height = 0
    for item in items:
        if "width" in item:
            if ")" in item:
                width = item.split(")")[-1]
        elif "height" in item:
            if ")" in item:
                height = item.split(")")[-1]
        if width and height: continue
    '''
    rels = [1.7777777777777777, 1.3333333333333333]
    rel = float(width)/float(height)
    if rel not in rels:
        print ("REL:", rel) # width = float(height) # usar el mas cercano de los dos
    '''
    return width, height


# FIXME: Suele suceder que no graba el video, solo una pantalla verde.

class webmPipeline(Gst.Pipeline):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "webmPipeline")

        self.__controller = None
        self.__codec = "webm"
        self.__origen = origen
        self.__duration = 0
        self.__position = 0

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(self.__origen)
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
        uridecodebin = Gst.ElementFactory.make("uridecodebin", "uridecodebin")

        # VIDEO
        videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        #caps = Gst.Caps.from_string('video/x-raw,format=(string)I420')
        _filter = Gst.ElementFactory.make("capsfilter", "_filter")
        #_filter.set_property("caps", caps)

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

        self.add(uridecodebin)

        self.add(videoconvert)
        self.add(_filter)
        self.add(vp8enc)
        self.add(videoqueue)

        self.add(audioconvert)
        self.add(vorbisenc)
        self.add(audioqueue)

        self.add(webmmux)
        self.add(filesink)

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
        uridecodebin.set_property("uri", Gst.filename_to_uri(self.__origen))
        uridecodebin.connect('pad-added', self.__on_pad_added)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.busMessageCb)

    def __on_pad_added(self, uridecodebin, pad):
        # FIXME: 1279 * 720 **ERROR: [python3] horizontal_size must be a even (4:2:0 / 4:2:2)
        #   https://en.wikipedia.org/wiki/Chroma_subsampling
        #   http://www.cinedigital.tv/que-es-todo-eso-de-444-422-420-o-color-subsampling/
        # Necesitamos la resolucion del video para las capas del filtro porque hay un bug en la negociación automática de gstreamer
        # De no ser por este bug ni siquiera se necesitaría el filtro
        # En el caso analizado, se recibe: width=(int)1279, height=(int)720
        # Pero se corrige al cambiar el ancho por 1280
        # Lo cual es: Maximal output width of 1280 horizontal pixels - De-Interlacing and YUV 4:2:2 to 4:2:0 Conversion Algorithm
        tpl_property = pad.get_property("template")  # https://lazka.github.io/pgi-docs/Gst-1.0/classes/PadTemplate.html
        #tpl_name = tpl_property.name_template
        currentcaps = pad.get_current_caps().to_string()
        #print ("Template: %s => %s" % (tpl_name, currentcaps))
        if currentcaps.startswith('video/'):
            self.__informeModel.setInfo("archivo", self.__origen)
            self.__informeModel.setInfo("codec",self.__codec)
            self.__informeModel.setInfo("formato inicial", self.__tipo)
            self.__informeModel.setInfo("entrada de video", currentcaps)           

            width, height = getSize(currentcaps)
            self.__informeModel.setInfo("relacion", float(width)/float(height))
            if width == 1279: width = 1280  # HACK
            caps = Gst.Caps.from_string('video/x-raw,format=I420,framerate=30/1,width=%s,height=%s' % (width, height))
            _filter = self.get_by_name("_filter")
            _filter.set_property("caps", caps)

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
            self.__t2 = datetime.datetime.now()
            self.__timeProcess = self.__t2 - self.__t1
            self.__informeModel.setInfo('tiempo de proceso', str(self.__timeProcess))
            self.stop()
            self.emit("end")

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__informeModel.setInfo('errores', str(mensaje.parse_error()))
            self.stop()
            self.emit("error", "ERROR en: " + self.__newpath + ' => ' + str(mensaje.parse_error()))
        
    def __del__(self):
        print("CODEC PIPELINE DESTROY")

    def stop(self):
        self.__new_handle(False)
        self.set_state(Gst.State.NULL)
        if self.__bus:
            self.__bus.disconnect_by_func(self.busMessageCb)
            self.__bus.remove_signal_watch()
            self.__bus = None

    def play(self):
        self.set_state(Gst.State.PLAYING)
        self.__new_handle(True)

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
