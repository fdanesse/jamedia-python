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


def format_ns(ns):
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if not h:
        return "%02u:%02u" % (m, s)
    else:
        return "%02u:%02u:%02u" % (h, m, s)


class Converter(GObject.Object):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, codec, dirpath_destino):

        GObject.Object.__init__(self)

        self._origen = origen
        self._codec = codec
        self.__controller = False
        self._duration = 0
        self._position = 0
        self.__pipe = Gst.ElementFactory.make("playbin", "player")
        self._info = {'Audio': '', 'Video': ''}

        self.__videoSink = None
        self.__audioSink = None

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(self._origen)
        if "." in location:
            extension = ".%s" % self._origen.split(".")[-1]
            location = location.replace(extension, ".%s" % self._codec)
        else:
            location = "%s.%s" % (location, self._codec)
        self._newpath = os.path.join(dirpath_destino, location)
        #self._origen = Gst.filename_to_uri(self._origen)

        self.__configPipe(dirpath_destino)

    def __configPipe(self, dirpath_destino):
        # Formato de salida
        if self._codec == "wav":
            self.__audioSink = self.__get_wav_audio_out()
        elif self._codec == "mp3":
            self.__audioSink = self.__get_mp3_audio_out()
        elif self._codec == "ogg":
            self.__audioSink = self.__get_ogg_audio_out()

        elif self._codec == "ogv":
            self.__pipe = self.__get_ogv_out()

        elif self._codec == "webm":
            from JAMediaConverter.Gstreamer.VideoPipelines.webmPipeline import webmPipeline
            self.__pipe = webmPipeline(self._origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)
        elif self._codec == "mp4":
            from JAMediaConverter.Gstreamer.VideoPipelines.mp4Pipeline import mp4Pipeline
            self.__pipe = mp4Pipeline(self._origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)
        elif self._codec == "avi":
            from JAMediaConverter.Gstreamer.VideoPipelines.aviPipeline import aviPipeline
            self.__pipe = aviPipeline(self._origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)
        elif self._codec == "mpg":
            from JAMediaConverter.Gstreamer.VideoPipelines.mpgPipeline import mpgPipeline
            self.__pipe = mpgPipeline(self._origen, dirpath_destino)
            decodebin, self.__videoSink, self.__audioSink = self.__pipe.getSinks()
            decodebin.connect('pad-added', self.__on_pad_added)

        elif self._codec == "png":
            # NOTA: Segun testeo: 100 imagenes x segundo 42.5Mb
            self.__videoSink = self.__get_png_out()
            self.__pipe.set_property('video-sink', self.__videoSink)
            self.__pipe.set_property('audio-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
            self.__videoSink.get_by_name('multifilesink').set_property('location', "%s/img%s06d.png" % (dirpath_destino, "%"))
            self.__pipe.set_property("uri", self._origen)

        if self._codec in ['wav', 'mp3', 'ogg']:
            self.__pipe.set_property('video-sink', Gst.ElementFactory.make('fakesink', 'fakesink'))
            self.__pipe.set_property('audio-sink', self.__audioSink)
            self.__audioSink.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.set_property("uri", self._origen)

        '''if self._codec in ['ogv', 'mpg']:
            self.__pipe.get_by_name('uridecodebin').connect('pad-added', self.__on_pad_added)
            self.__pipe.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.get_by_name('uridecodebin').set_property("uri", self._origen)'''

        self._bus = self.__pipe.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.busMessageCb)

    def __on_pad_added(self, uridecodebin, pad):
        # Agregar elementos en forma dinámica https://wiki.ubuntu.com/Novacut/GStreamer1.0
        currentcaps = pad.get_current_caps().to_string()  # pad.query_caps(None).to_string()
        if currentcaps.startswith('audio/'):
            pad.link(self.__audioSink)
            self._info['Audio'] = currentcaps
        elif currentcaps.startswith('video/'):
            pad.link(self.__videoSink)
            self._info['Video'] = currentcaps
        self.emit('info', self._info)

    def __del__(self):
        print("DESTROY OK")

    def __get_Standard_bins(self):
        uridecodebin = Gst.ElementFactory.make('uridecodebin', 'uridecodebin')
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property("max-rate", 30)
        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        audioresample = Gst.ElementFactory.make('audioresample', 'audioresample')
        audioresample.set_property('quality', 10)
        return uridecodebin, videoconvert, videorate, audioconvert, audioresample

    def __pipeline_Add_all(self, pipeline, bins):
        for bin in bins:
            pipeline.add(bin)

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
        self.__pipe.set_state(Gst.State.PLAYING)
        self.__new_handle(True)
    
    def stop(self):
        self.__new_handle(False)
        if self.__pipe:
            self.__pipe.set_state(Gst.State.NULL)
        if self._bus:
            self._bus.disconnect_by_func(self.busMessageCb)
            self._bus.remove_signal_watch()
            self._bus = None
        if self.__pipe:
            try:
                self.__pipe.set_property('video-sink', None)  # Solo salidas de audio
            except:
                pass
            try:
                self.__pipe.set_property('audio-sink', None)  # Solo salidas de audio
            except:
                pass
        self.__videoSink = None
        self.__audioSink = None
        del(self.__pipe)
        self.__pipe = None

    def busMessageCb(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            self.stop()
            self.emit("end")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            if self.__pipe:
                bool1, self._duration = self.__pipe.query_duration(Gst.Format.TIME)
                bool2, self._position = self.__pipe.query_position(Gst.Format.TIME)
        elif mensaje.type == Gst.MessageType.ERROR:
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
            self.stop()
            self.emit("error", "ERROR en: " + name + ' => ' + str(mensaje.parse_error()))
            
    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(300, self.__handle)

    def __handle(self):
        if not self.__pipe:
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
            self.stop()
            self.emit("error", "ERROR en: " + name + " - No se puede convertir a " + self._codec)
            return False

        '''
        if os.path.exists(self._newpath):
            tamanio = os.path.getsize(self._newpath)
            tam = int(tamanio) / 1024.0 / 1024.0
            self.emit('progress', tam)
        '''
        bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
        bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
        duracion = float(valor1)
        posicion = float(valor2)
        if self._duration != duracion:
            self._duration = duracion
            print ("DURATION: {0}".format(format_ns(valor1)))  # FIXME: Imprimir tiempos de proceso
        pos = 0
        try:
            pos = int(posicion * 100 / duracion)
        except:
            pass
        if pos != self._position:
            self._position = pos
            self.emit("progress", self._position, self._codec)
        return True

GObject.type_register(Converter)