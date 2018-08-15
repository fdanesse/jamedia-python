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
from gi.repository import GdkX11


class Converter(Gtk.Widget):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self, origen, codec, dirpath_destino):

        Gtk.Widget.__init__(self)

        self._origen = origen
        self._codec = codec
        self._newpath = ""
        self._controller = None
        self._player = None
        self._duration = 0
        self._position = 0
        self._pipe = Gst.Pipeline()

        # path de salida
        location = os.path.basename(self._origen)
        if "." in location:
            extension = ".%s" % self._origen.split(".")[-1]
            location = location.replace(extension, ".%s" % self._codec)
        else:
            location = "%s.%s" % (location, self._codec)
        self._newpath = os.path.join(dirpath_destino, location)
        self._origen = Gst.filename_to_uri(self._origen)
        # Formato de salida
        if self._codec == "wav":
            #self.__run_wav_out()
            pass
        elif self._codec == "mp3":
            self.__run_mp3_out()
        elif self._codec == "ogg":
            #self.__run_ogg_out()
            pass

    def free(self):
        if self._controller:
            GLib.source_remove(self._controller)
            self._controller = None
        #self._pipe.set_state(Gst.State.NULL)
        self._origen = None
        self._codec = None
        self._newpath = None
        self._controller = None
        self._player = None
        self._duration = None
        self._position = None
        self._pipe = None

    '''
    def __run_wav_out(self):
        from Bins import wav_bin
        self._player = gst.element_factory_make("playbin2", "playbin2")
        videoconvert = gst.element_factory_make("fakesink", "video-out")
        self._player.set_property('video-sink', videoconvert)

        wavenc = wav_bin(self._newpath)
        wavenc.set_name("audio-out")
        self._player.set_property('audio-sink', wavenc)

        self._player.set_property("uri", "file://" + self.origen)

        self.bus = self._player.get_bus()
        #self.bus.set_sync_handler(self.__bus_handler)
        self.bus.add_signal_watch()                             # ****
        self.bus.connect('message', self.__on_mensaje)          # ****
        #self.bus.enable_sync_message_emission()                 # ****
        #self.bus.connect('sync-message', self.__sync_message)   # ****
    '''

    def __run_mp3_out(self):
        self._player = Gst.ElementFactory.make("uridecodebin", "uridecodebin")
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')
        
        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        audioresample = Gst.ElementFactory.make('audioresample', 'audioresample')
        audioresample.set_property('quality', 10)
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        self._pipe.add(self._player)
        self._pipe.add(audioconvert)
        self._pipe.add(audioresample)
        self._pipe.add(lamemp3enc)
        self._pipe.add(filesink)
        self._pipe.add(videoconvert)
        self._pipe.add(fakesink)

        audioconvert.link(audioresample)
        audioresample.link(lamemp3enc)
        lamemp3enc.link(filesink)

        videoconvert.link(fakesink)

        self.video_sink = videoconvert.get_static_pad('sink')
        self.audio_sink = audioconvert.get_static_pad('sink')

        BASE_PATH = os.path.dirname(__file__)
        filesink.set_property("location", self._newpath)
        self._player.set_property("uri", self._origen)
        
        self.bus = self._pipe.get_bus()
        self.bus.enable_sync_message_emission()
        self.bus.connect('sync-message', self.__sync_message)
        self._player.connect('pad-added', self.__on_pad_added)
        self._player.connect("source-setup", self.__source_setup)
        
    def __on_pad_added(self, uridecodebin, pad):
        """
        Agregar elementos en forma dinámica
        https://wiki.ubuntu.com/Novacut/GStreamer1.0
        """
        string = pad.query_caps(None).to_string()
        if string.startswith('audio/'):
            pad.link(self.audio_sink)
            self.emit('info', string)
        elif string.startswith('video/'):
            pad.link(self.video_sink)
            self.emit('info', string)

    def play(self):
        self._pipe.set_state(Gst.State.PLAYING)
        self._controller = GLib.timeout_add(300, self.__handle)
    
    '''
    def stop(self):
        self._pipe.set_state(Gst.State.PAUSED)
        self._pipe.set_state(Gst.State.NULL)
        if self._controller:
            GLib.source_remove(self._controller)
            self._controller = None
    '''

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            if self._controller:
                GLib.source_remove(self._controller)
                self._controller = None
            self.emit("end")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, valor1 = self._player.query_duration(Gst.Format.TIME)
            bool2, valor2 = self._player.query_position(Gst.Format.TIME)
            self._duration = valor1
            self._position = valor2
        elif mensaje.type == Gst.MessageType.ERROR:
            if self._controller:
                GLib.source_remove(self._controller)
                self._controller = None
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
            print("ERROR en: " + name + ' => ' + str(mensaje.parse_error()))
            self.emit("error", "ERROR en: " + name + ' => ' + str(mensaje.parse_error()))
            
    def __handle(self):
        '''
        if os.path.exists(self._newpath):
            tamanio = os.path.getsize(self._newpath)
            tam = int(tamanio) / 1024.0 / 1024.0
            self.emit('progress', tam)
        '''
        bool1, valor1 = self._player.query_duration(Gst.Format.TIME)
        bool2, valor2 = self._player.query_position(Gst.Format.TIME)
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

    def __source_setup(self, player, source):
        #print '***', source.get_property('location')
        pass
