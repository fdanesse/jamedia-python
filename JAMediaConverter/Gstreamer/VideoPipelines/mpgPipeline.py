# -*- coding: utf-8 -*-

import os
import datetime

import gi
gi.require_version("Gst", "1.0")
gi.require_version("GstVideo", "1.0")

from gi.repository import Gst
from gi.repository import GstVideo


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
    rels = [1.7777777777777777, 1.3333333333333333]
    rel = float(width)/float(height)
    if rel not in rels:
        print ("REL:", rel) # width = float(height) # usar el mas cercano de los dos
    return width, height


class mpgPipeline(Gst.Pipeline):

    def __init__(self, origen, dirpath_destino):
        Gst.Pipeline.__init__(self, "mpgPipeline")

        self.set_name("mpgPipeline")

        self.__codec = "mpg"
        self.__origen = origen
        self.__status = Gst.State.NULL
        self.__t1 = None
        self.__t2 = None
        self.timeProcess = None

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
        videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')
        videoqueue.set_property("max-size-buffers", 10000)
        #videoqueue.set_property("max-size-bytes", 0)
        #videoqueue.set_property("max-size-time", 0)
        videoconvert1 = Gst.ElementFactory.make("videoconvert", "videoconvert1")
        deinterlace = Gst.ElementFactory.make("deinterlace", "deinterlace")
        deinterlace.set_property("mode", 2)  # disabled
        videoconvert2 = Gst.ElementFactory.make("videoconvert", "videoconvert2")
        #caps = Gst.Caps.from_string('video/x-raw,format=I420,framerate=30/1,width=640,height=480')
        _filter = Gst.ElementFactory.make("capsfilter", "_filter")
        #_filter.set_property("caps", caps)
        mpeg2enc = Gst.ElementFactory.make("mpeg2enc", "mpeg2enc")
        mpeg2enc.set_property("bufsize", 4000)

        # AUDIO
        audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
        twolamemp2enc = Gst.ElementFactory.make("twolamemp2enc", "twolamemp2enc")

        # SALIDA
        mpegpsmux = Gst.ElementFactory.make("mpegpsmux", "mpegpsmux")
        filesink = Gst.ElementFactory.make("filesink", "filesink")

        self.add(filesrc)
        self.add(decodebin)

        self.add(videoqueue)
        self.add(videoconvert1)
        self.add(deinterlace)
        self.add(videoconvert2)
        self.add(_filter)
        self.add(mpeg2enc)

        self.add(audioconvert)
        self.add(twolamemp2enc)

        self.add(mpegpsmux)
        self.add(filesink)

        filesrc.link(decodebin)

        videoqueue.link(videoconvert1)
        videoconvert1.link(deinterlace)
        deinterlace.link(videoconvert2)
        videoconvert2.link(_filter)
        _filter.link(mpeg2enc)
        mpeg2enc.link(mpegpsmux)
        mpegpsmux.link(filesink)

        audioconvert.link(twolamemp2enc)
        twolamemp2enc.link(mpegpsmux)

        self.__videoSink = videoqueue.get_static_pad("sink")
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
        # Necesitamos la resolucion del video para las capas del filtro porque hay un bug en la negociación automática de gstreamer
        # De no ser por este bug ni siquiera se necesitaría el filtro
        # En el caso analizado, se recibe: width=(int)1279, height=(int)720
        # Pero se corrige al cambiar el ancho por 1280
        # Lo cual es: Maximal output width of 1280 horizontal pixels - De-Interlacing and YUV 4:2:2 to 4:2:0 Conversion Algorithm
        tpl_property = pad.get_property("template")  # https://lazka.github.io/pgi-docs/Gst-1.0/classes/PadTemplate.html
        tpl_name = tpl_property.name_template
        currentcaps = pad.get_current_caps().to_string()
        print ("Template: %s => %s" % (tpl_name, currentcaps))
        if currentcaps.startswith('video/'):
            width, height = getSize(currentcaps)
            # FIXME: 1279 * 720 **ERROR: [python3] horizontal_size must be a even (4:2:0 / 4:2:2)
            # https://en.wikipedia.org/wiki/Chroma_subsampling
            # http://www.cinedigital.tv/que-es-todo-eso-de-444-422-420-o-color-subsampling/
            print ("SIZE:", width, height)
            width = 1280
            caps = Gst.Caps.from_string('video/x-raw,format=I420,framerate=30/1,width=%s,height=%s' % (width, height))
            _filter = self.get_by_name("_filter")
            _filter.set_property("caps", caps)

    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.__t1 = datetime.datetime.now()

        elif mensaje.type == Gst.MessageType.EOS:
            self.__t2 = datetime.datetime.now()
            self.timeProcess = self.__t2 - self.__t1
            print("END:", str(self.timeProcess))

        elif mensaje.type == Gst.MessageType.ERROR:
            print("ERROR:", str(mensaje.parse_error()))
        
    def __del__(self):
        print("DESTROY OK")
        