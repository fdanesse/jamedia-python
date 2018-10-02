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
                      / videorate | capsfilter | vp8enc
filesrc | decodebin --                                  \-- webmmux | filesink
                      \ audioresample | vorbisenc ------/
'''


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

        self.__videoSink = None
        self.__audioSink = None
        self.__bus = None

        self.__Init()

    def __emit_info(self, informemodel, info):
        self.emit("info", info)

    def __Init(self):
        # ORIGEN
        filesrc = Gst.ElementFactory.make("filesrc", "filesrc")
        decodebin = Gst.ElementFactory.make("decodebin", "decodebin")

        # VIDEO
        videorate = Gst.ElementFactory.make("videorate", "videorate")
        capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        caps = Gst.Caps.from_string('video/x-raw, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)24000/1001')
        capsfilter.set_property("caps", caps)
        vp8enc = Gst.ElementFactory.make("vp8enc", "vp8enc")
        #vp8enc.set_property("threads", 1)
        #vp8enc.set_property("cq-level", 63)
        #vp8enc.set_property("cpu-used", 0)

        # AUDIO
        audioresample = Gst.ElementFactory.make('audioresample', "audioresample")
        audioresample.set_property("quality", 10)
        vorbisenc = Gst.ElementFactory.make("vorbisenc", "vorbisenc")

        # SALIDA
        webmmux = Gst.ElementFactory.make("webmmux", "webmmux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(filesrc)
        self.add(decodebin)

        self.add(videorate)
        self.add(capsfilter)
        self.add(vp8enc)

        self.add(audioresample)
        self.add(vorbisenc)

        self.add(webmmux)
        self.add(filesink)

        filesrc.link(decodebin)

        videorate.link(capsfilter)
        capsfilter.link(vp8enc)
        vp8enc.link(webmmux)

        audioresample.link(vorbisenc)
        vorbisenc.link(webmmux)

        webmmux.link(filesink)

        self.__videoSink = videorate.get_static_pad("sink")
        self.__audioSink = audioresample.get_static_pad("sink")

        filesink.set_property("location", self.__newpath)
        filesrc.set_property("location", self.__origen)
        decodebin.connect('pad-added', self.__on_pad_added)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.busMessageCb)

        #self.use_clock(None)

        '''
        self.__bus.enable_sync_message_emission()
        self.__bus.connect("sync-message", self.busMessageCbSync)

    def busMessageCbSync(self, bus, message):
        print(message.type)'''

    def __on_pad_added(self, decodebin, pad):
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
