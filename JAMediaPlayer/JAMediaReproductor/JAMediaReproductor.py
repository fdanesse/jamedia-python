# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import GstVideo

from JAMediaPlayer.JAMediaReproductor.VideoOutput import VideoOutput
from JAMediaPlayer.JAMediaReproductor.AudioOutput import AudioOutput
from JAMediaPlayer.Globales import MAGIC
from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
from JAMediaConverter.Gstreamer.Globales import format_ns, getSize

GObject.threads_init()
Gst.init("--opengl-hwdec-interop=vaapi-glx")


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

        self.__source = None
        self.__controller = False
        self.__status = Gst.State.NULL
        self.__hasVideo = False
        self.__duration = 0
        self.__position = 0

        self.__config = {
            'saturacion': 1.0,
            'contraste': 1.0,
            'brillo': 0.0,
            'hue': 0.0,
            'gamma': 1.0,
            'rotacion': 0,
            'volumen': 1.0
            }

        self.__tipo = None
        self.__informeModel = None  # InformeTranscoderModel("PLAYER" + "-" + informeName)
        # self.__informeModel.connect("info", self.__emit_info)

        self.__pipe = None
        self.__videoBin = VideoOutput(self.__gtkSink, self.__config)
        self.__audioBin = AudioOutput()
        self.__bus = None

    def __reset(self):
        self.__source = None
        #self.__controller = False
        self.__status = Gst.State.NULL
        self.__hasVideo = False
        self.__duration = 0
        self.__position = 0

        if not self.__videoBin: self.__videoBin = VideoOutput(self.__gtkSink, self.__config)
        if not self.__audioBin: self.__audioBin = AudioOutput()
        self.__pipe = Gst.ElementFactory.make("playbin", "player")
        self.__pipe.set_property('volume', self.__config['volumen'])
        self.__pipe.set_property('force-aspect-ratio', True)
        self.__pipe.set_property('video-sink', self.__videoBin)
        self.__pipe.set_property('audio-sink', self.__audioBin)

        # gst-launch-1.0 filesrc location=cartoon.mp4 ! decodebin ! video/x-raw ! videoconvert ! subtitleoverlay name=over ! autovideosink  filesrc location=subs.srt ! subparse ! over.
        # self.__pipe.set_property('text-sink', self.__textBin)
        # FIXME: Subtítulos no funcionan
        # self.__pipe.set_property("subtitle-font-desc", Pango.FontDescription("%s %s" % ("Monospace", 12)))
        # self.__subtitleoverlay.set_property("silent", False)

        self.__bus = self.__pipe.get_bus()
        #self.__bus.enable_sync_message_emission()
        #self.__bus.connect('sync-message', self.__sync_message)
        self.__bus.add_signal_watch()
        self.__bus.connect("message", self.__sync_message)

    def __emit_info(self, informemodel, info):
        self.emit("info", info)  # FIXME: señal actualmente no conectada

    def __sync_message(self, bus, mensaje):
        if mensaje.type == Gst.MessageType.STATE_CHANGED:
            old, new, pending = mensaje.parse_state_changed()
            if old == Gst.State.PAUSED and new == Gst.State.PLAYING:
                if self.__status != new:
                    self.__status = new
                    print(self.__config['rotacion'])
                    self.__autoSet()
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

        elif mensaje.type == Gst.MessageType.TAG:
            if 'video-codec' in mensaje.parse_tag().to_string():
                if self.__hasVideo == False or self.__hasVideo == None:
                    self.__hasVideo = True
                    self.emit("video", True)

        elif mensaje.type == Gst.MessageType.LATENCY:
            # http://cgit.collabora.com/git/farstream.git/tree/examples/gui/fs-gui.py
            self.__pipe.recalculate_latency()

        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, self.__duration = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, self.__position = self.__pipe.query_position(Gst.Format.TIME)

        elif mensaje.type == Gst.MessageType.EOS:
            self.__new_handle(False)
            self.emit("endfile")

        elif mensaje.type == Gst.MessageType.ERROR:
            self.__informeModel.setInfo('errores', str(mensaje.parse_error()))
            self.__new_handle(False)

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
        if self.__pipe:
            self.__pipe.set_state(Gst.State.PLAYING)
            '''self.__pipe.get_state(1000)  # FIXME: Mover todo esto de aquí
            pad = self.__pipe.emit('get-video-pad',0) 
            if pad:
                currentcaps = pad.get_current_caps().to_string()
                if currentcaps.startswith('video/'):
                    self.__informeModel.setInfo("archivo", self.__source)
                    self.__informeModel.setInfo("formato inicial", self.__tipo)
                    self.__informeModel.setInfo("entrada de video", currentcaps)           
                    width, height = getSize(currentcaps)
                    self.__informeModel.setInfo("relacion", float(width)/float(height))
                elif currentcaps.startswith('audio/'):
                    self.__informeModel.setInfo("entrada de sonido", currentcaps)'''

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
            # FIXME: Porque no se captura en Gst.MessageType.STATE_CHANGED
            self.__status = Gst.State.NULL
            self.emit("estado", "None")
        
    def __autoSet(self):
        self.__videoBin.videobalance.set_property('saturation', self.__config['saturacion'])
        self.__videoBin.videobalance.set_property('contrast', self.__config['contraste'])
        self.__videoBin.videobalance.set_property('brightness', self.__config['brillo'])
        self.__videoBin.videobalance.set_property('hue', self.__config['hue'])
        self.__videoBin.gamma.set_property('gamma', self.__config['gamma'])
        self.__pipe.set_property('volume', self.__config['volumen'])
        self.__videoBin.videoflip.set_property('method', self.__config['rotacion'])

    def set_balance(self, brillo=False, contraste=False, saturacion=False, hue=False, gamma=False):
        if saturacion:
            # Double. Range: 0 - 2 Default: 1
            self.__config['saturacion'] = 2.0 * saturacion / 100.0
            self.__videoBin.videobalance.set_property('saturation', self.__config['saturacion'])
        if contraste:
            # Double. Range: 0 - 2 Default: 1
            self.__config['contraste'] = 2.0 * contraste / 100.0
            self.__videoBin.videobalance.set_property('contrast', self.__config['contraste'])
        if brillo:
            # Double. Range: -1 - 1 Default: 0
            self.__config['brillo'] = (2.0 * brillo / 100.0) - 1.0
            self.__videoBin.videobalance.set_property('brightness', self.__config['brillo'])
        if hue:
            # Double. Range: -1 - 1 Default: 0
            self.__config['hue'] = (2.0 * hue / 100.0) - 1.0
            self.__videoBin.videobalance.set_property('hue', self.__config['hue'])
        if gamma:
            # Double. Range: 0,01 - 10 Default: 1
            self.__config['gamma'] = (10.0 * gamma / 100.0)
            self.__videoBin.gamma.set_property('gamma', self.__config['gamma'])

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
        self.__config['rotacion'] = rot

    def set_volumen(self, valor):
        # recibe de 1.0 a 10.0
        self.__config['volumen'] = float(valor)  # float(valor/10.0) # FIXME: Con valores sin modificar, en mis parlantes satura mucho por encima de 5.0
        self.__pipe.set_property('volume', self.__config['volumen'])

    def set_position(self, posicion):
        posicion = self.__duration * posicion / 100
        self.__pipe.seek_simple(
            Gst.Format.TIME,
            Gst.SeekFlags.FLUSH |
            Gst.SeekFlags.KEY_UNIT,
            posicion)

    # FIXME: Subtítulos no funcionan
    #def set_subtitulos(self, path):
    #    self.__pipe.set_property("suburi", path)

    def load(self, uri):
        self.stop()
        self.emit("video", False)
        self.__reset()
        temp = uri
        if os.path.exists(temp):
            # FIXME: Implementar limpieza del nombre del archivo
            location = os.path.basename(temp)
            informeName = temp
            if "." in location:
                extension = ".%s" % temp.split(".")[-1]
                informeName = location.replace(extension, "")
            self.__informeModel = InformeTranscoderModel("PLAYER" + "-" + informeName)
            self.__informeModel.connect("info", self.__emit_info)
                
            self.__tipo = MAGIC.file(uri)
            temp = Gst.filename_to_uri(uri)
        if Gst.uri_is_valid(temp):
            self.__source = temp
            self.__pipe.set_property("uri", self.__source)
            self.__play()
        else:
            print ("Dirección no válida", temp)

GObject.type_register(JAMediaReproductor)
