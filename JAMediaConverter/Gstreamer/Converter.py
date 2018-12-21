# -*- coding: utf-8 -*-

# https://lazka.github.io/pgi-docs/Gst-1.0/functions.html

import os
#import gi
#gi.require_version('GstPbutils', '1.0')
from gi.repository import GObject
#from gi.repository import GstPbutils


class Converter(GObject.Object):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    #"info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)), FIXME: Ver audioFrame
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, codec, dirpath_destino):

        GObject.Object.__init__(self)

        self.__origen = origen
        self.__codec = codec
        self.__pipe = None

        '''self.__discovered = GstPbutils.Discoverer() #https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-libs/html/GstDiscoverer.html
        self.__discovered.connect('discovered', self.__succeed)
        self.__discovered.start()'''

        self.__configPipe(dirpath_destino)

    def getInfo(self):
        return self.__origen, self.__tipo, self.__codec

    def __configPipe(self, dirpath_destino):
        
        # EXTRACCION DE AUDIO
        if self.__codec in ["wav", "mp3", "ogg"]:
            from JAMediaConverter.Gstreamer.AudioPipelines.audioBin import audioBin
            self.__pipe = audioBin(self.__origen, dirpath_destino, self.__codec)

        # TRANSCODE AUDIO Y VIDEO
        elif self.__codec == "ogv":
            from JAMediaConverter.Gstreamer.VideoPipelines.ogvPipeline import ogvPipeline
            self.__pipe = ogvPipeline(self.__origen, dirpath_destino)

        elif self.__codec == "webm":
            from JAMediaConverter.Gstreamer.VideoPipelines.webmPipeline import webmPipeline
            self.__pipe = webmPipeline(self.__origen, dirpath_destino)

        elif self.__codec == "mpg":
            from JAMediaConverter.Gstreamer.VideoPipelines.mpgPipeline import mpgPipeline
            self.__pipe = mpgPipeline(self.__origen, dirpath_destino)

        elif self.__codec == "mp4":
            from JAMediaConverter.Gstreamer.VideoPipelines.mp4Pipeline import mp4Pipeline
            self.__pipe = mp4Pipeline(self.__origen, dirpath_destino)

        elif self.__codec == "avi":
            from JAMediaConverter.Gstreamer.VideoPipelines.aviPipeline import aviPipeline
            self.__pipe = aviPipeline(self.__origen, dirpath_destino)

        # EXTRACCION DE IMAGENES
        elif self.__codec == "png":
            from JAMediaConverter.Gstreamer.VideoPipelines.ImagenBin import ImagenBin
            self.__pipe = ImagenBin(self.__origen, dirpath_destino)

        self.__pipe.connect('progress', self.__updateProgress)
        self.__pipe.connect('error', self.__error)
        #self.__pipe.connect('info', self.__info) FIXME: Ver audioFrame
        self.__pipe.connect('end', self.__end)
        
    def __updateProgress(self, pipe, val1, codec):
        self.emit("progress", val1, codec)

    def __error(self, pipe, error):
        self.emit("error", error)

    #def __info(self, pipe, info):
    #    self.emit('info', info) FIXME: Ver audioFrame

    def __end(self, pipe):
        self.emit("end")

    '''def __del__(self):
        print("CONVERTER DESTROY")'''

    def play(self):
        #self.__discovered.discover_uri_async(self.__origen)
        time.sleep(1) # Fuerza espera para que otros converters no sobreescriban esta salida.
        self.__pipe.play()
        
    def stop(self):
        self.__pipe.stop()

    '''def __succeed(self, discoverer, info, error):
        result=GstPbutils.DiscovererInfo.get_result(info)
        if result != GstPbutils.DiscovererResult.ERROR:
            #https://lazka.github.io/pgi-docs/GstPbutils-1.0/classes/DiscovererInfo.html
            print("SEEKABLE:", info.get_seekable())
            print("DURATION:", info.get_duration())
            for i in info.get_stream_list():
                # https://lazka.github.io/pgi-docs/GstPbutils-1.0/classes/DiscovererStreamInfo.html
                if isinstance(i, GstPbutils.DiscovererAudioInfo):
                    print("AUDIO CAPS:", i.get_caps())
                    print("AUDIO LENGUAJE:", i.get_language())
                    print("AUDIO TAGS:", i.get_tags().to_string())
                    print("AUDIO MISC:", i.get_misc())
                elif isinstance(i, GstPbutils.DiscovererVideoInfo):
                    print("VIDEO CAPS:", i.get_caps())
                    print("VIDEO TAGS:", i.get_tags().to_string())
                    print("VIDEO MISC:", i.get_misc(), "\n")
            self.__pipe.play()
        else:
            print(error)'''

#GObject.type_register(Converter)
