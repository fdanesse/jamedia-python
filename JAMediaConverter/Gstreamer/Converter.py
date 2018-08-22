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
        self.__controller = False
        self._duration = 0
        self._position = 0
        self.__pipe = Gst.ElementFactory.make("playbin", "player")
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
            self.__pipe.set_property('video-sink', self.__get_video_fakesink())
            audioBin = self.__get_wav_audio_out()
            self.__pipe.set_property('audio-sink', audioBin)
            audioBin.get_by_name('filesink').set_property("location", self._newpath)
        elif self._codec == "mp3":
            self.__pipe.set_property('video-sink', self.__get_video_fakesink())
            audioBin = self.__get_mp3_audio_out()
            self.__pipe.set_property('audio-sink', audioBin)
            audioBin.get_by_name('filesink').set_property("location", self._newpath)
        elif self._codec == "ogg":
            self.__pipe.set_property('video-sink', self.__get_video_fakesink())
            audioBin = self.__get_ogg_audio_out()
            self.__pipe.set_property('audio-sink', audioBin)
            audioBin.get_by_name('filesink').set_property("location", self._newpath)

        self.__pipe.set_property("uri", self._origen)
        
        self._bus = self.__pipe.get_bus()
        self._bus.add_signal_watch()
        self._bus.connect("message", self.__sync_message)

    #def __del__(self):
    #    print("DESTROY OK")

    def __get_video_fakesink(self):
        videoBin = Gst.Bin()
        videoBin.set_name('videobin')
        videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')
        fakesink = Gst.ElementFactory.make('fakesink', 'fakesink')
        videoBin.add(videoqueue)
        videoBin.add(fakesink)
        videoqueue.link(fakesink)
        videoBin.add_pad(Gst.GhostPad.new("sink", videoqueue.get_static_pad("sink")))
        return videoBin

    def __get_mp3_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        lamemp3enc = Gst.ElementFactory.make('lamemp3enc', 'lamemp3enc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        audioBin.add(lamemp3enc)
        audioBin.add(filesink)
        lamemp3enc.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", lamemp3enc.get_static_pad("sink")))
        return audioBin

    def __get_wav_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        wavenc = Gst.ElementFactory.make('wavenc', 'wavenc')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        audioBin.add(wavenc)
        audioBin.add(filesink)
        wavenc.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", wavenc.get_static_pad("sink")))
        return audioBin

    def __get_ogg_audio_out(self):
        audioBin = Gst.Bin()
        audioBin.set_name('audiobin')
        vorbisenc = Gst.ElementFactory.make('vorbisenc', 'vorbisenc')
        oggmux = Gst.ElementFactory.make('oggmux', 'oggmux')
        filesink = Gst.ElementFactory.make('filesink', 'filesink')
        audioBin.add(vorbisenc)
        audioBin.add(oggmux)
        audioBin.add(filesink)
        vorbisenc.link(oggmux)
        oggmux.link(filesink)
        audioBin.add_pad(Gst.GhostPad.new("sink", vorbisenc.get_static_pad("sink")))
        return audioBin

    def play(self):
        self.__pipe.set_state(Gst.State.PLAYING)
        self.__new_handle(True)
        return False
    
    def stop(self):
        if self.__pipe:
            #self.__pipe.set_state(Gst.State.PAUSED)
            self.__pipe.set_state(Gst.State.NULL)
        self.__new_handle(False)
        self.__pipe = None

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.EOS:
            self.__new_handle(False)
            self.emit("end")
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
            self._duration = valor1
            self._position = valor2
        elif mensaje.type == Gst.MessageType.ERROR:
            self.__new_handle(False)
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
            self.__pipe = None
            self.emit("error", "ERROR en: " + name + ' => ' + str(mensaje.parse_error()))
            
    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(300, self.__handle)

    def __handle(self):
        if not self.__pipe:
            self.__new_handle(False)
            name = ''
            try:
                name = os.path.basename(self._origen)
            except:
                pass
            self.__pipe = None
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