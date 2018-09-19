# -*- coding: utf-8 -*-

# NOTA: Documentación Interesante => http://z25.org/static/_rd_/videostreaming_intro_plab/
# Audio to hdmi: http://trac.gateworks.com/wiki/Yocto/gstreamer/audio#Encoding
# Manual de gstreamer: https://gstreamer.freedesktop.org/documentation/application-development/

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import GstVideo


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
        # path de salida
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
            self.__pipe = self.__get_webm_out()
        elif self._codec == "mp4":
            self.__pipe = self.__get_mp4_out()
        elif self._codec == "avi":
            self.__pipe = self.__get_avi_out()
        elif self._codec == "mpg":
            # NOTA: Segun testeo: 100 imagenes x segundo 42.5Mb
            self.__pipe = self.__get_mpg_out()

        elif self._codec == "png":
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

        if self._codec in ['ogv', 'webm', 'mp4', 'avi', 'mpg']:
            '''self.__pipe.get_by_name('uridecodebin').connect('pad-added', self.__on_pad_added)
            self.__pipe.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.get_by_name('uridecodebin').set_property("uri", self._origen)'''
            self.__pipe.get_by_name('decodebin').connect('pad-added', self.__on_pad_added)
            self.__pipe.get_by_name('filesink').set_property("location", self._newpath)
            self.__pipe.get_by_name('filesrc').set_property("location", self._origen)

        self._bus = self.__pipe.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.__sync_message)

    #def __del__(self):
    #    print("DESTROY OK")

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

    def __get_mpg_out(self):
        bin = Gst.Pipeline()
        bin.set_name('bin')
        uridecodebin, videoconvert, videorate, audioconvert, audioresample = self.__get_Standard_bins()
        mpeg2enc = Gst.ElementFactory.make('mpeg2enc', 'mpeg2enc')
        twolamemp2enc = Gst.ElementFactory.make('twolamemp2enc', 'twolamemp2enc')
        mpegpsmux = Gst.ElementFactory.make('mpegpsmux', 'mpegpsmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(bin, [uridecodebin, audioconvert, audioresample, twolamemp2enc, mpegpsmux, filesink, videoconvert, videorate, mpeg2enc])
        audioconvert.link(audioresample)
        audioresample.link(twolamemp2enc)
        twolamemp2enc.link(mpegpsmux)
        videoconvert.link(videorate)
        videorate.link(mpeg2enc)
        mpeg2enc.link(mpegpsmux)
        mpegpsmux.link(filesink)
        self.__videoSink = videoconvert.get_static_pad('sink')
        self.__audioSink = audioconvert.get_static_pad('sink')
        return bin

    def __get_avi_out(self):
        # Nota: Avi admite audio y vieo en crudo
        bin = Gst.Pipeline()
        bin.set_name('bin')
        uridecodebin, videoconvert, videorate, audioconvert, audioresample = self.__get_Standard_bins()
        x264enc = Gst.ElementFactory.make('x264enc', 'x264enc')
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        avimux = Gst.ElementFactory.make('avimux', 'avimux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(bin, [uridecodebin, audioconvert, audioresample, lamemp3enc, avimux, filesink, videoconvert, videorate, x264enc])
        audioconvert.link(audioresample)
        audioresample.link(lamemp3enc)
        lamemp3enc.link(avimux)
        videoconvert.link(videorate)
        videorate.link(x264enc)
        x264enc.link(avimux)
        avimux.link(filesink)
        self.__videoSink = videoconvert.get_static_pad('sink')
        self.__audioSink = audioconvert.get_static_pad('sink')
        return bin

    def __get_mp4_out(self):
        bin = Gst.Pipeline()
        bin.set_name('bin')
        uridecodebin, videoconvert, videorate, audioconvert, audioresample = self.__get_Standard_bins()
        x264enc = Gst.ElementFactory.make('x264enc', 'x264enc')
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        mp4mux = Gst.ElementFactory.make('mp4mux', 'mp4mux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        self.__pipeline_Add_all(bin, [uridecodebin, audioconvert, audioresample, lamemp3enc, mp4mux, filesink, videoconvert, videorate, x264enc])
        audioconvert.link(audioresample)
        audioresample.link(lamemp3enc)
        lamemp3enc.link(mp4mux)
        videoconvert.link(videorate)
        videorate.link(x264enc)
        x264enc.link(mp4mux)
        mp4mux.link(filesink)
        self.__videoSink = videoconvert.get_static_pad('sink')
        self.__audioSink = audioconvert.get_static_pad('sink')
        return bin

    def __get_webm_out(self):
        # FIXME: Suele suceder que no graba el video, solo una pantalla verde.
        # Encoder parameters: https://www.webmproject.org/docs/encoder-parameters/
        # vp8enc: https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-good/html/gst-plugins-good-plugins-vp8enc.html

        # ejemplo de streaming en html: https://gist.github.com/vo/a0cc9313861888ad5180f442a4b7bf48
        # https://stackoverflow.com/questions/33306265/encode-decode-vp8-or-vp9-with-gstreamer
        # webmmux: https://developer.gnome.org/gst-plugins-libs/stable/gst-plugins-good-plugins-webmmux.html
        bin = Gst.Pipeline()
        bin.set_name('bin')

        '''
        uridecodebin, videoconvert, videorate, audioconvert, audioresample = self.__get_Standard_bins()

        vp8enc = Gst.ElementFactory.make('vp8enc', 'vp8enc')
        vp8enc.set_property("threads", 1)
        vp8enc.set_property("cq-level", 63)
        vp8enc.set_property("cpu-used", 0)

        vorbisenc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')
        webmmux = Gst.ElementFactory.make('webmmux', 'webmmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        self.__pipeline_Add_all(bin, [uridecodebin, audioconvert, audioresample, vorbisenc, webmmux, filesink, videoconvert, videorate, vp8enc])
        
        audioconvert.link(audioresample)
        audioresample.link(vorbisenc)
        vorbisenc.link(webmmux)
        videoconvert.link(videorate)
        videorate.link(vp8enc)
        vp8enc.link(webmmux)
        webmmux.link(filesink)
        '''

        filesrc = Gst.ElementFactory.make('filesrc', 'filesrc')
        decodebin = Gst.ElementFactory.make('decodebin', 'decodebin')

        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property("max-rate", 30)

        vp8enc = Gst.ElementFactory.make('vp8enc', 'vp8enc')
        vp8enc.set_property("threads", 1)
        vp8enc.set_property("cq-level", 63)
        vp8enc.set_property("cpu-used", 0)

        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        audioresample = Gst.ElementFactory.make('audioresample', 'audioresample')
        audioresample.set_property('quality', 10)
        vorbisenc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')

        webmmux = Gst.ElementFactory.make('webmmux', 'webmmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        bin.add(filesrc)
        bin.add(decodebin)

        bin.add(videoconvert)
        bin.add(videorate)

        bin.add(vp8enc)

        bin.add(audioconvert)
        bin.add(audioresample)
        bin.add(vorbisenc)

        bin.add(webmmux)
        bin.add(filesink)

        filesrc.link(decodebin)

        videoconvert.link(videorate)
        videorate.link(vp8enc)
        vp8enc.link(webmmux)
        webmmux.link(filesink)

        audioconvert.link(audioresample)
        audioresample.link(vorbisenc)
        vorbisenc.link(webmmux)

        self.__videoSink = videoconvert.get_static_pad('sink')
        self.__audioSink = audioconvert.get_static_pad('sink')
        return bin

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

    def __on_pad_added(self, uridecodebin, pad):
        # Agregar elementos en forma dinámica https://wiki.ubuntu.com/Novacut/GStreamer1.0
        string = pad.query_caps(None).to_string()
        if string.startswith('audio/'):
            pad.link(self.__audioSink)
            self._info['Audio'] = string
        elif string.startswith('video/'):
            pad.link(self.__videoSink)
            self._info['Video'] = string
        self.emit('info', self._info)

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
            self._bus.disconnect_by_func(self.__sync_message)
            self._bus.remove_signal_watch()
            self._bus = None
        if self.__pipe:
            try:
                self.__pipe.set_property('video-sink', None)
            except:
                pass
            try:
                self.__pipe.set_property('audio-sink', None)
            except:
                pass
        self.__videoSink = None
        self.__audioSink = None
        self.__pipe = None

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            self.stop()
            self.emit("end")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            if self.__pipe:
                bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
                bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
                self._duration = valor1
                self._position = valor2
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
        pos = 0
        try:
            pos = int(posicion * 100 / duracion)
        except:
            pass
        if self._duration != duracion:
            self._duration = duracion
        if pos != self._position:
            self._position = pos
            self.emit("progress", self._position, self._codec)
        return True

GObject.type_register(Converter)