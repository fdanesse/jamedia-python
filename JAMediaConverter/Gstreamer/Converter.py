# -*- coding: utf-8 -*-

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import GstVideo


'''def format_ns(ns):
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if not h:
        return "%02u:%02u" % (m, s)
    else:
        return "%02u:%02u:%02u" % (h, m, s)'''


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
        self.__pipe = None  #Gst.ElementFactory.make("playbin", "player")

        # FIXME: Implementar limpieza del nombre del archivo ?
        location = os.path.basename(self.__origen)
        if "." in location:
            extension = ".%s" % self.__origen.split(".")[-1]
            location = location.replace(extension, ".%s" % self.__codec)
        else:
            location = "%s.%s" % (location, self.__codec)
        self._newpath = os.path.join(dirpath_destino, location)

        self.__configPipe(dirpath_destino)

    def __configPipe(self, dirpath_destino):
        # Formato de salida
        if self.__codec == "wav":
            self.__audioSink = self.__get_wav_audio_out()
        elif self.__codec == "mp3":
            self.__audioSink = self.__get_mp3_audio_out()
        elif self.__codec == "ogg":
            self.__audioSink = self.__get_ogg_audio_out()

        elif self.__codec == "ogv":
            self.__pipe = self.__get_ogv_out()

        elif self.__codec == "webm":
            from JAMediaConverter.Gstreamer.VideoPipelines.webmPipeline import webmPipeline
            self.__pipe = webmPipeline(self.__origen, dirpath_destino)
            self.__pipe.connect('progress', self.__updateProgress)
            self.__pipe.connect('error', self.__error)
            self.__pipe.connect('info', self.__info)
            self.__pipe.connect('end', self.__end)


        elif self.__codec == "mp4":
            from JAMediaConverter.Gstreamer.VideoPipelines.mp4Pipeline import mp4Pipeline
            self.__pipe = mp4Pipeline(self.__origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)
        elif self.__codec == "avi":
            from JAMediaConverter.Gstreamer.VideoPipelines.aviPipeline import aviPipeline
            self.__pipe = aviPipeline(self.__origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)
        elif self.__codec == "mpg":
            pass
            # FIXME: Rendimiento inaceptable
            '''from JAMediaConverter.Gstreamer.VideoPipelines.mpgPipeline import mpgPipeline
            self.__pipe = mpgPipeline(self.__origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)'''

        elif self.__codec == "png":
            # NOTA: Segun testeo: 100 imagenes x segundo 42.5Mb
            self.__videoSink = self.__get_png_out()
            self.__pipe.set_property('video-sink', self.__videoSink)
            self.__pipe.set_property('audio-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
            self.__videoSink.get_by_name('multifilesink').set_property('location', "%s/img%s06d.png" % (dirpath_destino, "%"))
            self.__pipe.set_property("uri", self.__origen)

        if self.__codec in ['wav', 'mp3', 'ogg']:
            self.__pipe.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
            self.__pipe.set_property('audio-sink', self.__audioSink)
            self.__audioSink.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.set_property("uri", self.__origen)

        '''if self.__codec in ['ogv', 'mpg']:
            self.__pipe.get_by_name('uridecodebin').connect('pad-added', self.__on_pad_added)
            self.__pipe.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.get_by_name('uridecodebin').set_property("uri", self.__origen)'''

        '''self._bus = self.__pipe.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.busMessageCb)'''

    def __updateProgress(self, pipe, val1, codec):
        self.emit("progress", val1, codec)

    def __error(self, pipe, error):
        self.__pipe = None
        self.emit("error", error)

    def __info(self, pipe, info):
        self.emit('info', info)

    def __end(self, pipe):
        self.__pipe = None
        self.emit("end")

    def __del__(self):
        print("CONVERTER DESTROY")

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

    def __get_ogv_out(self):
        bin = Gst.Pipeline()
        bin.set_name('bin')
        uridecodebin, videoconvert, videorate, audioconvert, audioresample = self.__get_Standard_bins()
        theoraenc = Gst.ElementFactory.make('theoraenc', 'theoraenc')
        theoraenc.set_property("quality", 63)
        vorbisenc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')
        oggmux = Gst.ElementFactory.make('oggmux', 'oggmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(bin, [uridecodebin, audioconvert, audioresample, vorbisenc, oggmux, filesink, videoconvert, videorate, theoraenc])
        audioconvert.link(audioresample)
        audioresample.link(vorbisenc)
        vorbisenc.link(oggmux)
        videoconvert.link(videorate)
        videorate.link(theoraenc)
        theoraenc.link(oggmux)
        oggmux.link(filesink)
        self.__videoSink = videoconvert.get_static_pad('sink')
        self.__audioSink = audioconvert.get_static_pad('sink')
        return bin

    def __get_mp3_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(audioBin, [lamemp3enc, filesink])
        lamemp3enc.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", lamemp3enc.get_static_pad("sink")))
        return audioBin

    def __get_wav_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        wavenc = Gst.ElementFactory.make('wavenc', 'wavenc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(audioBin, [wavenc, filesink])
        wavenc.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", wavenc.get_static_pad("sink")))
        return audioBin

    def __get_ogg_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        vorbisenc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')
        oggmux = Gst.ElementFactory.make('oggmux', 'oggmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(audioBin, [vorbisenc, oggmux, filesink])
        vorbisenc.link(oggmux)
        oggmux.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", vorbisenc.get_static_pad("sink")))
        return audioBin

    def play(self):
        self.__pipe.play()
        
    '''def stop(self):
        self.__pipe.stop()'''


GObject.type_register(Converter)