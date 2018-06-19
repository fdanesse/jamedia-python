#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   JAMediaReproductor.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')  # FIXME: Necesario => AttributeError: 'GstXvImageSink' object has no attribute 'set_window_handle'

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import GstVideo


class JAMediaReproductor(GObject.GObject):

    __gsignals__ = {
    "endfile": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, []),
    "estado": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "newposicion": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_INT,)),
    "video": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_BOOLEAN,)),
    "loading-buffer": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_INT, )),
        }

    # Estados: playing, paused, None

    def __init__(self, winId):

        GObject.GObject.__init__(self)

        self.__source = None
        self.__winId = winId
        self.__controller = False
        self.__status = Gst.State.NULL
        self.__hasVideo = False
        self.__duration = 0
        self.__position = 0
        self.__valVolume = 0.1

        self.__pipe = Gst.Pipeline()
        self.__player = Gst.ElementFactory.make("uridecodebin", "uridecodebin")
        #self.__player.set_property("buffer-size", 50000)
        #self.__player.set_property("buffer-duration", 50000)
        #self.__player.set_property("download", True)
        #self.__player.set_property("use-buffering", True)

        audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
        audioresample = Gst.ElementFactory.make('audioresample', 'audioresample')
        audioresample.set_property('quality', 10)
        self.__volume = Gst.ElementFactory.make('volume', 'volume')
        self.__volume.set_property('volume', self.__valVolume)
        autoaudiosink = Gst.ElementFactory.make("autoaudiosink", "autoaudiosink")

        videoconvert = Gst.ElementFactory.make('videoconvert', 'videoconvert')
        videorate = Gst.ElementFactory.make('videorate', 'videorate')
        videorate.set_property('skip-to-first', True)
        videorate.set_property('drop-only', True)
        videorate.set_property('max-rate', 30)
        xvimagesink = Gst.ElementFactory.make('xvimagesink', "xvimagesink")
        xvimagesink.set_property("force-aspect-ratio", True)
        xvimagesink.set_window_handle(self.__winId)

        self.__pipe.add(self.__player)
        self.__pipe.add(audioconvert)
        self.__pipe.add(audioresample)
        self.__pipe.add(self.__volume)
        self.__pipe.add(autoaudiosink)

        self.__pipe.add(videoconvert)
        self.__pipe.add(videorate)
        self.__pipe.add(xvimagesink)

        audioconvert.link(audioresample)
        audioresample.link(self.__volume)
        self.__volume.link(autoaudiosink)

        videoconvert.link(videorate)
        videorate.link(xvimagesink)

        self.__video_sink = videoconvert.get_static_pad('sink')
        self.__audio_sink = audioconvert.get_static_pad('sink')
        
        self.__bus = self.__pipe.get_bus()
        self.__bus.enable_sync_message_emission()
        self.__bus.connect('sync-message', self.__sync_message)
        self.__player.connect('pad-added', self.__on_pad_added)
        self.__player.connect('no-more-pads', self.__no_more_pads)

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "playing")
                    self.__new_handle(True)
                    # Si se llama enseguida falla.
                    #GLib.idle_add(self.__re_config)
            elif old == Gst.State.READY and new == Gst.State.PAUSED:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "paused")
                    self.__new_handle(False)
            elif old == Gst.State.READY and new == Gst.State.NULL:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "None")
                    self.__new_handle(False)
            elif old == Gst.State.PLAYING and new == Gst.State.PAUSED:
                if self.__status != new:
                    self.__status = new
                    self.emit("estado", "paused")
                    self.__new_handle(False)
        elif mensaje.type == Gst.MessageType.TAG:
            taglist = mensaje.parse_tag()
            datos = taglist.to_string()
            if 'audio-codec' in datos and not 'video-codec' in datos:
                if self.__hasVideo == True or \
                    self.__hasVideo == None:
                    self.__hasVideo = False
                    self.emit("video", False)
            elif 'video-codec' in datos:
                if self.__hasVideo == False or \
                    self.__hasVideo == None:
                    self.__hasVideo = True
                    self.emit("video", True)
        elif mensaje.type == Gst.MessageType.WARNING:
            print "\n Gst.MessageType.WARNING:", mensaje.parse_warning()
        elif mensaje.type == Gst.MessageType.LATENCY:
            # http://cgit.collabora.com/git/farstream.git/tree/examples/gui/fs-gui.py
            #print "\n Gst.MessageType.LATENCY"
            self.__pipe.recalculate_latency()
        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
            self.__duration = valor1
            self.__position = valor2
        elif mensaje.type == Gst.MessageType.QOS:
            pass  #print "\n Gst.MessageType.QOS:"
        elif mensaje.type == Gst.MessageType.BUFFERING:
            '''
            print "\n Gst.MessageType.BUFFERING:"
            print mensaje.parse_buffering()
            print mensaje.parse_buffering_stats()
            '''
            pass
        elif mensaje.type == Gst.MessageType.EOS:
            #self.video_pipeline.seek_simple(Gst.Format.TIME,
            #Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, 0)
            print "\n Gst.MessageType.EOS:"
            self.__new_handle(False)
            self.emit("endfile")
        elif mensaje.type == Gst.MessageType.ERROR:
            print "\n Gst.MessageType.ERROR:"
            print mensaje.parse_error()
            self.__new_handle(False)
            '''
            Gst.MessageType.WARNING: (gerror=GLib.Error('Se están desechando muchos búferes.', 'gst-core-error-quark', 13), debug='gstbasesink.c(2901): gst_base_sink_is_too_late (): /GstPipeline:pipeline0/GstXvImageSink:xvimagesink:\nThere may be a timestamping problem, or this computer is too slow.')
            Gst.MessageType.ERROR: (gerror=GLib.Error('Failed to configure the buffer pool', 'gst-resource-error-quark', 13), debug='../../../gst/vaapi/gstvaapipluginbase.c(709): gst_vaapi_plugin_base_create_pool (): /GstPipeline:pipeline2/GstURIDecodeBin:uridecodebin/GstDecodeBin:decodebin2/GstVaapiDecodeBin:vaapidecodebin2/GstVaapiPostproc:vaapipostproc2:\nConfiguration is most likely invalid, please report this issue.')
            '''

    def __on_pad_added(self, uridecodebin, pad):
        """
        Agregar elementos en forma dinámica
        https://wiki.ubuntu.com/Novacut/GStreamer1.0
        """
        string = pad.query_caps(None).to_string()
        if string.startswith('audio/'):
            pad.link(self.__audio_sink)
            #self.emit('info', string)
            print string
        elif string.startswith('video/'):
            pad.link(self.__video_sink)
            #self.emit('info', string)
            print string

    def __no_more_pads(self, objeto):
        print objeto

    def __pause(self):
        self.__pipe.set_state(Gst.State.PAUSED)

    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(500, self.__handle)

    def __handle(self):
        bool1, valor1 = self.__pipe.query_duration(Gst.Format.TIME)
        bool2, valor2 = self.__pipe.query_position(Gst.Format.TIME)
        duracion = float(valor1)
        posicion = float(valor2)
        pos = 0
        try:
            pos = int(posicion * 100 / duracion)
        except:
            pass
        if self.__duration != duracion:
            self.__duration = duracion
        if pos != self.__position:
            self.__position = pos
            self.emit("newposicion", self.__position)
        return True

    def __pause(self):
        self.__pipe.set_state(Gst.State.PAUSED)
    
    def play(self):
        self.__pipe.set_state(Gst.State.PLAYING)

    def pause_play(self):
        if self.__status == Gst.State.PAUSED \
            or self.__status == Gst.State.NULL \
            or self.__status == Gst.State.READY:
            self.play()
        elif self.__status == Gst.State.PLAYING:
            self.__pause()

    def stop(self):
        #self.__pipe.set_state(Gst.State.PAUSED)
        self.__pipe.set_state(Gst.State.NULL)

    def set_volumen(self, valor):
        self.__valVolume = float(valor)  # 0.0 - 10.0
        print self.__valVolume
        self.__volume.set_property('volume', self.__valVolume)

    def load(self, uri):
        self.stop()
        #self.__reset()
        if not uri:
            return False
        temp = uri
        if os.path.exists(temp):
            temp = Gst.filename_to_uri(uri)
        if Gst.uri_is_valid(temp):
            self.__source = temp
            self.__player.set_property("uri", self.__source)
        else:
            print "FIXME:", "Dirección no válida", temp