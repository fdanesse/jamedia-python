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
        self._newpath = ""
        self._controller = None
        self._duration = 0
        self._position = 0
        self._bus = None
        self.__pipe = Gst.Pipeline()
        self._video_sink = None
        self._audio_sink = None
        self._info = {'Audio': '', 'Video': ''}

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
            self.__run_wav_out()
        elif self._codec == "mp3":
            self.__run_mp3_out()
        elif self._codec == "ogg":
            self.__run_ogg_out() # FIXME: Violación de segmento (`core' generado)

        self.__pipe.set_property("uri", self._origen)
        
        self._bus = self.__pipe.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.__sync_message)

    def __del__(self):
        print("DESTROY OK")

    def __run_mp3_out(self):
        # VIDEO
        videoBin = Gst.Pipeline()
        videoBin.set_name('videobin')
        videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')
        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')

        videoBin.add(videoqueue)
        videoBin.add(videoconvert)
        videoBin.add(fakesink)

        videoqueue.link(videoconvert)
        videoconvert.link(fakesink)

        pad = videoqueue.get_static_pad("sink")
        videoBin.add_pad(Gst.GhostPad.new("sink", pad))

        # AUDIO
        audioBin = Gst.Pipeline()
        audioBin.set_name('audiobin')
        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        audioresample = Gst.ElementFactory.make('audioresample', 'audioresample')
        audioresample.set_property('quality', 10)
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')

        audioBin.add(audioconvert)
        audioBin.add(audioresample)
        audioBin.add(lamemp3enc)
        audioBin.add(filesink)

        audioconvert.link(audioresample)
        audioresample.link(lamemp3enc)
        lamemp3enc.link(filesink)

        pad = audioconvert.get_static_pad("sink")
        audioBin.add_pad(Gst.GhostPad.new("sink", pad))

        self.__pipe = Gst.ElementFactory.make("playbin", "player")
        self.__pipe.set_property('video-sink', videoBin)
        self.__pipe.set_property('audio-sink', audioBin)
        filesink.set_property("location", self._newpath)

    def play(self):
        self.__pipe.set_state(Gst.State.PLAYING)
        self._controller = GLib.timeout_add(300, self.__handle)
        return False
    
    def stop(self):
        if self.__pipe:
            self.__pipe.set_state(Gst.State.PAUSED)
            self.__pipe.set_state(Gst.State.NULL)
        if self._controller:
            GLib.source_remove(self._controller)
            self._controller = None

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            if self._controller:
                GLib.source_remove(self._controller)
                self._controller = None
            self.emit("end")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
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
            self.emit("error", "ERROR en: " + name + ' => ' + str(mensaje.parse_error()))
            
    def __handle(self):
        if not self.__pipe:
            if self._controller:
                GLib.source_remove(self._controller)
                self._controller = None
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
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