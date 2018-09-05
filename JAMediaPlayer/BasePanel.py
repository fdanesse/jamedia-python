# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GdkX11 # NOTA: Necesario para obtener el id de la ventana

from JAMediaPlayer.izquierda.Izquierda import Izquierda
from JAMediaPlayer.derecha.Derecha import Derecha

from JAMediaPlayer.JAMediaReproductor.JAMediaReproductor import JAMediaReproductor


class BasePanel(Gtk.HPaned):

    def __init__(self):

        Gtk.HPaned.__init__(self)

        self.set_css_name('jamediaplayerpanel')
        self.set_name('jamediaplayerpanel')

        self.izquierda = Izquierda()
        self.derecha = Derecha()

        self.pack1(self.izquierda, resize=True, shrink=True)
        self.pack2(self.derecha, resize=False, shrink=False)

        self.player = JAMediaReproductor(self.izquierda.video_visor.gtkSink)
        self.player.connect("endfile", self.__endfile)
        self.player.connect("estado", self.__state_changed)
        self.player.connect("newposicion", self.__update_progress)
        self.player.connect("video", self.__set_video)
        
        self.show_all()

        self.derecha.lista.lista.connect("nueva-seleccion", self.__cargar_reproducir)
        self.derecha.playercontrols.connect("accion-controls", self.__accion_controls)
        self.derecha.balance.connect("balance-valor", self.__accion_balance)
        self.derecha.lista.lista.connect("len_items", self.__len_items)
        # FIXME: Subtítulos no funcionan self.derecha.lista.connect("subtitulos", self.__load_subtitulos)
        self.izquierda.toolbar_info.connect("rotar", self.__rotar)
        self.izquierda.progress.connect("seek", self.__user_set_progress)
        self.izquierda.progress.connect("volumen", self.__set_volumen)

    def __len_items(self, widget, items):
        if items == 0 and self.player:
            self.player.stop()

    def __accion_balance(self, widget, valor, prop):
        if prop == "saturacion":
            self.player.set_balance(saturacion=valor)
        elif prop == "contraste":
            self.player.set_balance(contraste=valor)
        elif prop == "brillo":
            self.player.set_balance(brillo=valor)
        elif prop == "hue":
            self.player.set_balance(hue=valor)
        elif prop == "gamma":
            self.player.set_balance(gamma=valor)

    def __accion_controls(self, widget, accion):
        if accion == "atras":
            self.derecha.lista.lista.seleccionar_anterior()
        elif accion == "siguiente":
            self.derecha.lista.lista.seleccionar_siguiente()
        elif accion == "stop":
            if self.player:
                self.player.stop()
        elif accion == "pausa-play":
            if self.player:
                self.player.pause_play()

    def __set_volumen(self, widget, valor):
        if self.player:
            self.player.set_volumen(valor)

    def __user_set_progress(self, widget, valor):
        if self.player:
            self.player.set_position(valor)

    # FIXME: Subtítulos no funcionan
    #def __load_subtitulos(self, widget, path):
    #    self.player.set_subtitulos(path)

    def __cargar_reproducir(self, widget, path):
        volumen = 1.0
        volumen = float("{:.1f}".format(self.izquierda.progress.get_volumen()))
        self.izquierda.progress.set_sensitive(False)
        self.player.load(path)
        self.player.set_volumen(volumen)
    
    def __rotar(self, widget, valor):
        if self.player:
            self.player.rotar(valor)

    def __set_video(self, widget, valor):
        self.izquierda.toolbar_info.set_video(valor)
        # FIXME: Subtítulos no funcionan self.derecha.lista.toolbar.subtitulos.set_sensitive(valor)

    def __update_progress(self, objetoemisor, pos, label):
        self.izquierda.toolbar_info.label.set_text(label)
        self.izquierda.progress.set_progress(pos)

    def __state_changed(self, widget=None, valor=None):
        if "playing" in valor:
            GLib.idle_add(self.derecha.playercontrols.set_playing)
            GLib.idle_add(self.izquierda.progress.set_sensitive, True)
            GLib.idle_add(self.__update_balance)
        elif "paused" in valor or "None" in valor:
            GLib.idle_add(self.derecha.playercontrols.set_paused)
            GLib.idle_add(self.__update_balance)
        else:
            print ("Estado del Reproductor desconocido:", valor)

    def __update_balance(self):
        config = {}
        if self.player:
            config = self.player.get_balance()
        GLib.idle_add(self.derecha.balance.set_balance, 
            brillo=config.get('brillo', 50.0),
            contraste=config.get('contraste', 50.0),
            saturacion=config.get('saturacion', 50.0),
            hue=config.get('hue', 50.0),
            gamma=config.get('gamma', 10.0))
        return False

    def __endfile(self, widget=None, senial=None):
        GLib.idle_add(self.izquierda.toolbar_info.label.set_text, "00:00 - 00:00")
        GLib.idle_add(self.derecha.playercontrols.set_paused)
        GLib.idle_add(self.derecha.lista.lista.seleccionar_siguiente)
