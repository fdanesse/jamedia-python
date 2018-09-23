# -*- coding: utf-8 -*-

import os

from gi.repository import GObject


class Converter(GObject.Object):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, codec, dirpath_destino):

        GObject.Object.__init__(self)

        self.__origen = origen
        self.__codec = codec
        self.__pipe = None

        self.__configPipe(dirpath_destino)

    def getInfo(self):
        return self.__codec, self.__origen

    def __configPipe(self, dirpath_destino):
        
        # EXTRACCION DE AUDIO
        if self.__codec in ["wav", "mp3", "ogg"]:
            from JAMediaConverter.Gstreamer.AudioPipelines.audioBin import audioBin
            self.__pipe = audioBin(self.__origen, dirpath_destino, self.__codec)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)

        # TRANSCODE AUDIO Y VIDEO
        elif self.__codec == "ogv":
            from JAMediaConverter.Gstreamer.VideoPipelines.ogvPipeline import ogvPipeline
            self.__pipe = ogvPipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)
        elif self.__codec == "webm":
            from JAMediaConverter.Gstreamer.VideoPipelines.webmPipeline import webmPipeline
            self.__pipe = webmPipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)
        elif self.__codec == "mpg":
            from JAMediaConverter.Gstreamer.VideoPipelines.mpgPipeline import mpgPipeline
            self.__pipe = mpgPipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)
        elif self.__codec == "mp4":
            from JAMediaConverter.Gstreamer.VideoPipelines.mp4Pipeline import mp4Pipeline
            self.__pipe = mp4Pipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)
        elif self.__codec == "avi":
            from JAMediaConverter.Gstreamer.VideoPipelines.aviPipeline import aviPipeline
            self.__pipe = aviPipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)
        
        # EXTRACCION DE IMAGENES
        elif self.__codec == "png":
            # NOTA: Segun testeo: 100 imagenes x segundo 42.5Mb
            self.__videoSink = self.__get_png_out()
            self.__pipe.set_property('video-sink', self.__videoSink)
            self.__pipe.set_property('audio-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
            self.__videoSink.get_by_name('multifilesink').set_property('location', "%s/img%s06d.png" % (dirpath_destino, "%"))
            self.__pipe.set_property("uri", self.__origen)

    def __updateProgress(self, pipe, val1, codec):
        self.emit("progress", val1, codec)

    def __error(self, pipe, error):
        self.stop()
        self.emit("error", error)

    def __info(self, pipe, info):
        self.emit('info', info)

    def __end(self, pipe):
        self.stop()
        self.emit("end")

    '''def __del__(self):
        print("CONVERTER DESTROY")'''

    def __get_png_out(self):
        pngBin = Gst.Bin()
        pngBin.set_name('pngBin')
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property("max-rate", 30)
        pngenc = Gst.ElementFactory.make('pngenc', 'pngenc')
        multifilesink = Gst.ElementFactory.make('multifilesink', 'multifilesink')
        self.__pipeline_Add_all(pngBin, [videoconvert, videorate, pngenc, multifilesink])
        videoconvert.link(videorate)
        videorate.link(pngenc)
        pngenc.link(multifilesink)
        pngBin.add_pad(Gst.GhostPad.new("sink", videoconvert.get_static_pad("sink")))
        return pngBin

    def play(self):
        self.__pipe.play()
        
    def stop(self):
        self.__pipe.stop()

GObject.type_register(Converter)