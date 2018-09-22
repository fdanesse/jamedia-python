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


# FIXME: Suele suceder que no graba el video, solo una pantalla verde. No graba el audio
'''
               / queue | videoconvert | videorate | videoscale | capsfilter | theoraenc
uridecodebin --                                                                      \-- multiqueue | oggmux | filesink
               \ audioconvert | audioresample | audiorate | vorbisenc ---------------/
'''


class ogvPipeline(Gst.Pipeline):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "ogvPipeline")

        self.__controller = None
        self.__codec = "ogv"
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
        uridecodebin = Gst.ElementFactory.make("uridecodebin", "uridecodebin")

        # VIDEO
        vqueue = Gst.ElementFactory.make("queue", "vqueue")
        videoconvert = Gst.ElementFactory.make("videoconvert", "videoconvert")
        videorate = Gst.ElementFactory.make("videorate", "videorate")
        videorate.set_property("drop-only", True)
        videorate.set_property("max-rate", 30)
        videoscale = Gst.ElementFactory.make("videoscale", "videoscale")
        #caps = Gst.Caps.from_string('video/x-raw,format=(string)I420')
        capsfilter = Gst.ElementFactory.make("capsfilter", "capsfilter")
        #capsfilter.set_property("caps", caps)

        theoraenc = Gst.ElementFactory.make('theoraenc', 'theoraenc')
        theoraenc.set_property("quality", 63)

        # AUDIO
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        audioresample = Gst.ElementFactory.make('audioresample', "audioresample")
        audioresample.set_property("quality", 10)
        audiorate = Gst.ElementFactory.make('audiorate', "audiorate")
        vorbisenc = Gst.ElementFactory.make("vorbisenc", "vorbisenc")

        # SALIDA
        multiqueue = Gst.ElementFactory.make("multiqueue", "multiqueue")
        oggmux = Gst.ElementFactory.make("oggmux", "oggmux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(uridecodebin)

        self.add(vqueue)
        self.add(videoconvert)
        self.add(videorate)
        self.add(videoscale)
        self.add(capsfilter)
        self.add(theoraenc)

        self.add(audioconvert)
        self.add(audioresample)
        self.add(audiorate)
        self.add(vorbisenc)

        self.add(multiqueue)
        self.add(oggmux)
        self.add(filesink)

        vqueue.link(videoconvert)
        videoconvert.link(videorate)
        videorate.link(videoscale)
        videoscale.link(capsfilter)
        capsfilter.link(theoraenc)
        theoraenc.link(multiqueue)

        audioconvert.link(audioresample)
        audioresample.link(audiorate)
        audiorate.link(vorbisenc)
        vorbisenc.link(multiqueue)

        multiqueue.link(oggmux)
        oggmux.link(filesink)

        self.__videoSink = vqueue.get_static_pad("sink")
        self.__audioSink = audioconvert.get_static_pad("sink")

        filesink.set_property("location", self.__newpath)
        uridecodebin.set_property("uri", Gst.filename_to_uri(self.__origen))
        uridecodebin.connect('pad-added', self.__on_pad_added)

        self.__bus = self.get_bus()
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.busMessageCb)

        '''
        self.__bus.enable_sync_message_emission()
        self.__bus.connect("sync-message", self.busMessageCbSync)

    def busMessageCbSync(self, bus, message):
        print(message.type)'''

    def __on_pad_added(self, uridecodebin, pad):
        tpl_property = pad.get_property("template")  # https://lazka.github.io/pgi-docs/Gst-1.0/classes/PadTemplate.html
        currentcaps = pad.get_current_caps().to_string()
        if currentcaps.startswith('video/'):
            self.__informeModel.setInfo("archivo", self.__origen)
            self.__informeModel.setInfo("codec",self.__codec)
            self.__informeModel.setInfo("formato inicial", self.__tipo)
            self.__informeModel.setInfo("entrada de video", currentcaps)           

            width, height = getSize(currentcaps)
            self.__informeModel.setInfo("relacion", float(width)/float(height))
            if width == 1279: width = 1280  # HACK
            caps = Gst.Caps.from_string('video/x-raw,framerate=30/1,width=%s,height=%s' % (width, height))
            capsfilter = self.get_by_name("capsfilter")
            capsfilter.set_property("caps", caps)

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
        ret = self.get_state(1000)
        print("STOP", ret)
        if self.__bus:
            self.__bus.disconnect_by_func(self.busMessageCb)
            self.__bus.remove_signal_watch()
            self.__bus = None

    def play(self):
        self.__new_handle(True)
        self.set_state(Gst.State.PLAYING)
        ret = self.get_state(1000)
        print("PLAY", ret)
        '''
        if ret == Gst.State.PLAYING:
            self.__new_handle(True)
        else:
            print("PLAY", ret)
            self.stop()
            self.emit("end")'''

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
