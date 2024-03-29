# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html
# Crear Elementos usando python: https://mathieuduponchelle.github.io/2018-02-01-Python-Elements.html?gi-language=undefined
# audioplotter: https://mathieuduponchelle.github.io/2018-02-15-Python-Elements-2.html?gi-language=undefined

# Drivers video ubuntu 18:04
# sudo add-apt-repository ppa:oibaf/graphics-drivers
# sudo apt install xserver-xorg-video-amdgpu
# sudo apt install mesa-vulkan-drivers

import os

import gi
gi.require_version('Gst', '1.0')

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst

Gst.init([])

from JAMediaPlayer.JAMediaReproductor.VideoOutput import VideoOutput
from JAMediaPlayer.JAMediaReproductor.AudioOutput import AudioOutput
from JAMediaPlayer.Globales import MAGIC
from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
from JAMediaConverter.Gstreamer.Globales import format_ns
from JAMediaConverter.Gstreamer.Globales import getSize
from JAMediaConverter.Gstreamer.Globales import clearFileName


class JAMediaReproductor(GObject.Object):

    __gsignals__ = {
    "endfile": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, []),
    "estado": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "newposicion": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "video": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_BOOLEAN,)),
    "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))
    }

    # Estados: playing, paused, None

    def __init__(self, sink):

        GObject.Object.__init__(self)
        
        self.__gtkSink = sink

        self.__origen = None
        self.__source = None
        self.__controller = False
        self.__status = Gst.State.NULL
        self.__duration = 0
        self.__position = 0

        self.__videoconfig = {
            'saturacion': 1.0,
            'contraste': 1.0,
            'brillo': 0.0,
            'matiz': 0.0,
            'gamma': 1.0,
            'rotacion': 0,
            'volumen': 0.1}

        #self.__audioconfig = {
        #    'band0': 0,
        #    'band1': 0,
        #    'band2': 0,
        #    'band3': 0,
        #    'band4': 0,
        #    'band5': 0,
        #    'band6': 0,
        #    'band7': 0,
        #    'band8': 0,
        #    'band9': 0}

        self.__tipo = None
        self.__pipe = None
        self.__videoBin = VideoOutput(self.__gtkSink)
        #self.__audioBin = AudioOutput(dict(self.__audioconfig))
        self.__bus = None

    def __reset(self):
        self.__origen = None
        self.__source = None
        #self.__controller = False
        self.__status = Gst.State.NULL
        self.__duration = 0
        self.__position = 0
        self.__tipo = None

        if not self.__videoBin: self.__videoBin = VideoOutput(self.__gtkSink)
        #if not self.__audioBin: self.__audioBin = AudioOutput(dict(self.__audioconfig))
        self.__pipe = Gst.ElementFactory.make("playbin", "player")
        self.__pipe.set_property('volume', self.__videoconfig['volumen'])
        self.__pipe.set_property('force-aspect-ratio', True)
        self.__pipe.set_property('video-sink', self.__videoBin)
        #self.__pipe.set_property('audio-sink', self.__audioBin)

        self.__bus = self.__pipe.get_bus()
        #self.__bus.enable_sync_message_emission()
        #self.__bus.connect('sync-message', self.__sync_message)
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.__sync_message)

    def __emit_info(self, informemodel, info):
        # FIXME: señal actualmente no conectada, Mostrará en la interfaz las características del video
        # self.emit("info", info)
        pass

    def __sync_message(self, bus, mensaje):
        #https://gstreamer.freedesktop.org/documentation/design/messages.html
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    self.__autoSet()
                    self.__informar()
                    self.emit("estado", "playing")
                    self.__new_handle(True)

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

        elif mensaje.type == Gst.MessageType.LATENCY:
            # http://cgit.collabora.com/git/farstream.git/tree/examples/gui/fs-gui.py
            #La latencia es el tiempo que tarda una muestra capturada en la marca de tiempo X para alcanzar el sink
            self.__pipe.recalculate_latency()

        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, self.__duration = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, self.__position = self.__pipe.query_position(Gst.Format.TIME)

        elif mensaje.type == Gst.MessageType.EOS:
            self.__endProcess()

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__errorProcess(str(mensaje.parse_error()))

    def __endProcess(self):
        self.__new_handle(False)
        self.emit("endfile")

    def __errorProcess(self, error):
        self.__new_handle(False)
        self.__informeModel.setInfo('errores', error)

    def __informar(self):
        pad = self.__pipe.emit('get-video-pad',0)
        self.emit("video", bool(pad))
        # FIXME: Si no hay video Dibujar el audio ?
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('video/'):
                self.__informeModel.setInfo("entrada de video", currentcaps)           
                width, height = getSize(currentcaps)
                self.__informeModel.setInfo("relacion", float(width)/float(height))
        pad = self.__pipe.emit('get-audio-pad',0) 
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('audio/'):
                self.__informeModel.setInfo("entrada de sonido", currentcaps)
        #pad = self.__pipe.emit('get-text-pad',0)
        #if pad:
        #    currentcaps = pad.get_current_caps().to_string()

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
        if self.__duration != duracion:
            self.__duration = duracion
        pos = 0.0
        try:
            pos = float(posicion * 100.0 / self.__duration)
        except:
            pass
        if pos != self.__position:
            self.__position = pos
            # Se emite un flotante de 0.0 a 100.?
            label = "{0} - {1}".format(format_ns(valor2), format_ns(valor1))
            self.emit("newposicion", self.__position, label)
            '''
            NOTA: https://github.com/gkralik/python-gst-tutorial/blob/master/basic-tutorial-4.py
            query = Gst.Query.new_seeking(Gst.Format.TIME)
            self.__pipe.query(query)
            fmt, val, start, end = query.parse_seeking()
            print(fmt, val, start, end)
            print("{0} to {1}".format(format_ns(start), format_ns(end)))
            print("{0} - {1}".format(format_ns(valor2), format_ns(valor1)))
            '''
        return True
    
    def __pause(self):
        if self.__pipe: self.__pipe.set_state(Gst.State.PAUSED)

    def __play(self):
        if self.__pipe: self.__pipe.set_state(Gst.State.PLAYING)

    def pause_play(self):
        if self.__status == Gst.State.PAUSED \
            or self.__status == Gst.State.NULL \
            or self.__status == Gst.State.READY:
            self.__play()
        elif self.__status == Gst.State.PLAYING:
            self.__pause()

    def stop(self):
        if self.__pipe:  # and (self.__status != Gst.State.NULL and self.__status != Gst.State.PAUSED):
            self.__new_handle(False)
            self.__pipe.set_state(Gst.State.NULL)
            # Porque no se captura en Gst.MessageType.STATE_CHANGED
            self.__status = Gst.State.NULL
            self.emit("estado", "None")
        
    def __autoSet(self):
        self.__videoBin.videobalance.set_property('saturation', self.__videoconfig['saturacion'])
        self.__videoBin.videobalance.set_property('contrast', self.__videoconfig['contraste'])
        self.__videoBin.videobalance.set_property('brightness', self.__videoconfig['brillo'])
        self.__videoBin.videobalance.set_property('hue', self.__videoconfig["matiz"])
        self.__videoBin.gamma.set_property('gamma', self.__videoconfig['gamma'])
        self.__pipe.set_property('volume', self.__videoconfig['volumen'])
        self.__videoBin.videoflip.set_property('method', self.__videoconfig['rotacion'])
        #self.__audioBin.setting(self.__audioconfig)

    def set_balance(self, brillo=False, contraste=False, saturacion=False, matiz=False, gamma=False):
        if saturacion:
            # Double. Range: 0 - 2 Default: 1
            self.__videoconfig['saturacion'] = 2.0 * saturacion / 100.0
            self.__videoBin.videobalance.set_property('saturation', self.__videoconfig['saturacion'])
        elif contraste:
            # Double. Range: 0 - 2 Default: 1
            self.__videoconfig['contraste'] = 2.0 * contraste / 100.0
            self.__videoBin.videobalance.set_property('contrast', self.__videoconfig['contraste'])
        if brillo:
            # Double. Range: -1 - 1 Default: 0
            self.__videoconfig['brillo'] = (2.0 * brillo / 100.0) - 1.0
            self.__videoBin.videobalance.set_property('brightness', self.__videoconfig['brillo'])
        if matiz:
            # Double. Range: -1 - 1 Default: 0
            self.__videoconfig["matiz"] = (2.0 * matiz / 100.0) - 1.0
            self.__videoBin.videobalance.set_property('hue', self.__videoconfig["matiz"])
        if gamma:
            # Double. Range: 0,01 - 10 Default: 1
            self.__videoconfig['gamma'] = (10.0 * gamma / 100.0)
            self.__videoBin.gamma.set_property('gamma', self.__videoconfig['gamma'])

    def rotar(self, valor):
        rot = self.__videoBin.videoflip.get_property('method')
        if valor == "Derecha":
            if rot < 3:
                rot += 1
            else:
                rot = 0
        elif valor == "Izquierda":
            if rot > 0:
                rot -= 1
            else:
                rot = 3
        self.__videoBin.videoflip.set_property('method', rot)
        self.__videoconfig['rotacion'] = rot

    #def set_banda(self, valor, banda):
    #    # Convertir a rango -24 - +12 default 0
    #    hz = (valor / 100.0 * 36.0) - 24.0
    #    if self.__audioconfig[banda] != hz:
    #        self.__audioconfig[banda] = hz
    #        self.__audioBin.setting(dict(self.__audioconfig))

    def set_volumen(self, valor):
        # recibe de 0.0 a 1.0
        self.__videoconfig['volumen'] = valor # float(valor)*10.0 playbin es de 0.0 a 10.0
        self.__pipe.set_property('volume', self.__videoconfig['volumen'])

    def set_position(self, posicion):
        posicion = self.__duration * posicion / 100
        self.__pipe.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH |
            Gst.SeekFlags.KEY_UNIT,
            posicion)

    def set_subtitulos(self, path):
        # self.__pipe.set_property("subtitle-font-desc", "Sans, 18")
        # gst-launch-1.0 filesrc location=cartoon.mp4 ! decodebin ! video/x-raw ! videoconvert ! subtitleoverlay name=over ! autovideosink  filesrc location=subs.srt ! subparse ! over.
        # self.__pipe.set_property('text-sink', self.__textBin)
        # self.__pipe.set_property("subtitle-font-desc", Pango.FontDescription("%s %s" % ("Monospace", 12)))
        # self.__subtitleoverlay.set_property("silent", False)
        self.load(self.__origen, path)

    def load(self, uri, suburi=''):
        self.stop()
        self.__reset()
        self.__origen = uri
        temp = uri

        informeName = uri
        if os.path.exists(temp):
            informeName = clearFileName(os.path.basename(temp))
            self.__tipo = MAGIC.file(uri)
            temp = Gst.filename_to_uri(uri)

        if Gst.uri_is_valid(temp):
            self.__source = temp
            self.__informeModel = InformeTranscoderModel("PLAYER" + "-" + informeName)
            self.__informeModel.connect("info", self.__emit_info)
            self.__informeModel.setInfo("archivo", self.__source)
            self.__informeModel.setInfo("formato inicial", self.__tipo)
            self.__pipe.set_property("uri", self.__source)
            if suburi: self.__pipe.set_property("suburi", Gst.filename_to_uri(suburi))
            self.__play()
        else:
            print ("Dirección no válida", temp)
