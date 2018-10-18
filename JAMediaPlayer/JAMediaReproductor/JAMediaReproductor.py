# -*- coding: utf-8 -*-

# https://gstreamer.freedesktop.org/documentation/tools/gst-launch.html

import os

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstVideo', '1.0')
gi.require_version('GstPbutils', '1.0')

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import GstVideo
from gi.repository import GstPbutils

from JAMediaPlayer.JAMediaReproductor.VideoOutput import VideoOutput
from JAMediaPlayer.JAMediaReproductor.AudioOutput import AudioOutput
from JAMediaPlayer.Globales import MAGIC
# FIXME: Reconstruir informe para posibles errores en el reproductor
#from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
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
        self.__duration = 0
        self.__position = 0

        self.__discovered = GstPbutils.Discoverer() #https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-libs/html/GstDiscoverer.html
        #self.__discovered.connect('source-setup', self.__sourceSetup)
        self.__discovered.connect('discovered', self.__succeed)
        self.__discovered.start()

        self.__videoconfig = {
            'saturacion': 1.0,
            'contraste': 1.0,
            'brillo': 0.0,
            'matiz': 0.0,
            'gamma': 1.0,
            'rotacion': 0,
            'volumen': 0.1}

        self.__audioconfig = {
            'band0': 0,
            'band1': 0,
            'band2': 0,
            'band3': 0,
            'band4': 0,
            'band5': 0,
            'band6': 0,
            'band7': 0,
            'band8': 0,
            'band9': 0}

        self.__tipo = None
        #self.__informeModel = None  # InformeTranscoderModel("PLAYER" + "-" + informeName)
        # self.__informeModel.connect("info", self.__emit_info)

        self.__pipe = None
        self.__videoBin = VideoOutput(self.__gtkSink)
        self.__audioBin = AudioOutput(dict(self.__audioconfig))
        self.__bus = None

    '''
    def __sourceSetup(self, parent, element):
        <GstPbutils.Discoverer object at 0x7fa35960abd0 (GstDiscoverer at 0x2c7a2f0)>
        <__gi__.GstFileSrc object at 0x7fa30a1b2ee8 (GstFileSrc at 0x4240600)>
        print(parent, element)
    '''

    def __succeed(self, discoverer, info, error):
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
            self.__pipe.set_property("uri", self.__source)
            self.__play()
        else:
            print(error)
        '''
        SEEKABLE: True
        DURATION: 152904000000
        AUDIO CAPS: audio/mpeg, mpegversion=(int)4, framed=(boolean)true, stream-format=(string)raw,
                    level=(string)2, base-profile=(string)lc, profile=(string)lc, codec_data=(buffer)121056e500,
                    rate=(int)44100, channels=(int)2
        AUDIO LENGUAJE: None
        AUDIO TAGS: taglist, audio-codec=(string)"MPEG-4\ AAC\ audio", maximum-bitrate=(uint)128000,
                    bitrate=(uint)127648, title=(string)"\"Udemy\ Video\ Asset\"", encoder=(string)Lavf57.71.100,
                    container-format=(string)"ISO\ MP4/M4A";
        AUDIO MISC: None
        VIDEO CAPS: video/x-h264, stream-format=(string)avc, alignment=(string)au, level=(string)3.1, profile=(string)high,
                    codec_data=(buffer)0164001fffe1001e6764001facd9405005bbff0bbd0bbe10000003001000000303c0f183196001000568eae3dc9c,
                    width=(int)1280, height=(int)720, framerate=(fraction)30/1, pixel-aspect-ratio=(fraction)39060/39073,
                    interlace-mode=(string)progressive, chroma-format=(string)4:2:0, bit-depth-luma=(uint)8, bit-depth-chroma=(uint)8,
                    parsed=(boolean)true
        VIDEO TAGS: taglist, video-codec=(string)"H.264\ /\ AVC", bitrate=(uint)117750, title=(string)"\"Udemy\ Video\ Asset\"",
                    encoder=(string)Lavf57.71.100, container-format=(string)"ISO\ MP4/M4A";
        VIDEO MISC: None
        '''
        '''
        {"archivo":
        "/home/flavio/Descargas/Tienda Angular/22 - A\u00f1adiendo y actualizando productos.mp4",
        "formato inicial": "video/mp4; charset=binary",
        "entrada de video": "video/x-raw, format=(string)I420, width=(int)1280, height=(int)720,
            interlace-mode=(string)progressive, multiview-mode=(string)mono,
            multiview-flags=(GstVideoMultiviewFlagsSet)0:ffffffff:
            /right-view-first/left-flipped/left-flopped/right-flipped/right-flopped/half-aspect/mixed-mono,
            pixel-aspect-ratio=(fraction)39060/39073, chroma-site=(string)mpeg2, colorimetry=(string)bt709,
            framerate=(fraction)30/1",
            "entrada de sonido": "audio/x-raw, format=(string)F32LE, layout=(string)interleaved,
            rate=(int)44100, channels=(int)2, channel-mask=(bitmask)0x0000000000000003",
            "codec": "webm", "duracion": "02:32", "relacion": 1.7777777777777777,
            "tiempo de proceso": "0:32:58.984548", "errores": ""}
        '''
        '''
        SEEKABLE: True
        DURATION: 152880000000
        AUDIO CAPS: audio/x-vorbis, channels=(int)2, rate=(int)44100, streamheader=(buffer)<
        AUDIO LENGUAJE: en
        AUDIO TAGS: taglist, container-format=(string)Matroska, language-code=(string)en, title=(string)"\"Udemy\ Video\ Asset\"",
                    encoder=(string)Lavf57.71.100, encoder-version=(uint)0, audio-codec=(string)Vorbis, nominal-bitrate=(uint)112000,
                    bitrate=(uint)112000;
        AUDIO MISC: None
        VIDEO CAPS: video/x-vp9, width=(int)1280, height=(int)720, pixel-aspect-ratio=(fraction)1/1, framerate=(fraction)30/1
        VIDEO TAGS: taglist, video-codec=(string)"VP9\ video", container-format=(string)Matroska, title=(string)"\"Udemy\ Video\ Asset\"",
                    encoder=(string)Lavf57.71.100;
        VIDEO MISC: None
        '''
    def __reset(self):
        self.__source = None
        #self.__controller = False
        self.__status = Gst.State.NULL
        self.__duration = 0
        self.__position = 0

        if not self.__videoBin: self.__videoBin = VideoOutput(self.__gtkSink)
        if not self.__audioBin: self.__audioBin = AudioOutput(dict(self.__audioconfig))
        self.__pipe = Gst.ElementFactory.make("playbin", "player")
        self.__pipe.set_property('volume', self.__videoconfig['volumen'])
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
        # FIXME: señal actualmente no conectada, Mostrará en la interfaz las características del video
        self.emit("info", info)

    def __sync_message(self, bus, mensaje):
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
            self.__pipe.recalculate_latency()

        elif mensaje.type == Gst.MessageType.DURATION_CHANGED:
            bool1, self.__duration = self.__pipe.query_duration(Gst.Format.TIME)
            bool2, self.__position = self.__pipe.query_position(Gst.Format.TIME)

        elif mensaje.type == Gst.MessageType.EOS:
            self.__new_handle(False)
            self.emit("endfile")

        elif mensaje.type == Gst.MessageType.ERROR:
            #self.__informeModel.setInfo('errores', str(mensaje.parse_error()))
            self.__new_handle(False)

    def __informar(self):
        pad = self.__pipe.emit('get-video-pad',0)
        self.emit("video", bool(pad))
        '''
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('video/'):
                self.__informeModel.setInfo("archivo", self.__source)
                self.__informeModel.setInfo("formato inicial", self.__tipo)
                self.__informeModel.setInfo("entrada de video", currentcaps)           
                width, height = getSize(currentcaps)
                self.__informeModel.setInfo("relacion", float(width)/float(height))
        pad = self.__pipe.emit('get-audio-pad',0) 
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('audio/'):
                self.__informeModel.setInfo("entrada de sonido", currentcaps)
        '''
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
        self.__audioBin.setting(self.__audioconfig)

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

    def set_banda(self, valor, banda):
        # Convertir a rango -24 - +12 default 0
        hz = (valor / 100.0 * 36.0) - 24.0
        if self.__audioconfig[banda] != hz:
            self.__audioconfig[banda] = hz
            self.__audioBin.setting(dict(self.__audioconfig))

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

    # FIXME: Subtítulos no funcionan
    #def set_subtitulos(self, path):
    #    self.__pipe.set_property("suburi", path)

    def load(self, uri):
        self.stop()
        self.__reset()
        temp = uri

        if os.path.exists(temp):
            # FIXME: Implementar limpieza del nombre del archivo
            informeName = os.path.basename(temp)
            if "." in informeName:
                extension = ".%s" % informeName.split(".")[-1]
                informeName = informeName.replace(extension, "")
            #self.__informeModel = InformeTranscoderModel("PLAYER" + "-" + informeName)
            #self.__informeModel.connect("info", self.__emit_info)
                
            self.__tipo = MAGIC.file(uri)
            temp = Gst.filename_to_uri(uri)
        else:
            #self.__informeModel = InformeTranscoderModel("PLAYER" + "-" + uri)
            #self.__informeModel.connect("info", self.__emit_info)
            pass

        if Gst.uri_is_valid(temp):
            self.__source = temp
            self.__discovered.discover_uri_async(self.__source)
        else:
            print ("Dirección no válida", temp)

GObject.type_register(JAMediaReproductor)
