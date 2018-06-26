# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkX11

from JAMediaPlayer.izquierda.Izquierda import Izquierda
from JAMediaPlayer.derecha.Derecha import Derecha

from JAMediaPlayer.Globales import get_colors

from JAMediaPlayer.JAMediaReproductor.JAMediaReproductor import JAMediaReproductor


class BasePanel(Gtk.HPaned):

    __gsignals__ = {
    "show-controls": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "accion-list": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
    "menu_activo": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    }

    def __init__(self):

        Gtk.HPaned.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        self.set_border_width(2)

        self.izquierda = Izquierda()
        self.derecha = Derecha()

        self.pack1(self.izquierda, resize=True, shrink=True)
        self.pack2(self.derecha, resize=False, shrink=False)

        self.player = JAMediaReproductor()
        self.player.start()
        self.player.connect("endfile", self.__endfile)
        self.player.connect("estado", self.__state_changed)
        self.player.connect("newposicion", self.__update_progress)
        self.player.connect("video", self.__set_video)
        #self.player.connect("loading-buffer", self.__loading_buffer)
        
        self.show_all()

        self.derecha.connect("cargar-reproducir", self.__cargar_reproducir)
        self.derecha.connect("accion-list", self.__emit_accion_list)
        self.derecha.connect("menu_activo", self.__emit_menu_activo)
        self.derecha.playercontrols.connect("accion-controls", self.__accion_controls)
        self.derecha.balance.connect("balance-valor", self.__accion_balance)

        self.izquierda.connect("show-controls", self.__emit_show_controls)
        self.izquierda.connect("rotar", self.__rotar)
        self.izquierda.connect("seek", self.__user_set_progress)
        self.izquierda.connect("volumen", self.__set_volumen)

    def __accion_balance(self, widget, valor, prop):
        # Setea valores de Balance en el reproductor.
        self.__emit_menu_activo()
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

    def __emit_menu_activo(self, widget=False):
        # hay un menu contextual presente
        self.emit("menu_activo")
        #self.izquierda.buffer_info.hide()

    def __emit_accion_list(self, widget, lista, accion, _iter):
        # borrar, copiar, mover, grabar, etc . . .
        self.emit("accion-list", lista, accion, _iter)

    def __accion_controls(self, widget, accion):
        # anterior, siguiente, pausa, play, stop
        self.__emit_menu_activo()
        if accion == "atras":
            self.derecha.lista.seleccionar_anterior()
        elif accion == "siguiente":
            self.derecha.lista.seleccionar_siguiente()
        elif accion == "stop":
            if self.player:
                self.player.stop()
        elif accion == "pausa-play":
            if self.player:
                self.player.pause_play()

    def __set_volumen(self, widget, valor):
        self.__emit_menu_activo()
        if self.player:
            self.player.set_volumen(valor)

    def __user_set_progress(self, widget, valor):
        self.__emit_menu_activo()
        if self.player:
            self.player.set_position(valor)

    def __emit_show_controls(self, widget, datos):
        self.emit("show-controls", datos)

    def __cargar_reproducir(self, widget, path):
        self.derecha.set_sensitive(False)
        volumen = 1.0
        volumen = float("{:.1f}".format(self.izquierda.progress.get_volumen()))
        self.izquierda.progress.set_sensitive(False)
        xid = self.izquierda.video_visor.get_property('window').get_xid()
        self.player.load(path, xid)
        self.player.set_volumen(volumen)
        self.derecha.set_sensitive(True)

    '''
    def __loading_buffer(self, player, buf):
        pass #self.izquierda.buffer_info.set_progress(float(buf))
    '''
    
    def __rotar(self, widget, valor):
        if self.player:
            self.__emit_menu_activo()
            self.player.rotar(valor)

    def __set_video(self, widget, valor):
        self.izquierda.toolbar_info.set_video(valor)

    def __update_progress(self, objetoemisor, valor):
        # Progreso de la reproducción.
        self.izquierda.progress.set_progress(valor)

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
        self.derecha.playercontrols.set_paused()
        self.derecha.lista.seleccionar_siguiente()

    def setup_init(self):
        self.izquierda.setup_init()
        self.derecha.setup_init()

    def salir(self):
        if self.player:
            self.player.disconnect_by_func(self.__endfile)
            self.player.disconnect_by_func(self.__state_changed)
            self.player.disconnect_by_func(self.__update_progress)
            self.player.disconnect_by_func(self.__set_video)
            #self.player.disconnect_by_func(self.__loading_buffer)
            self.player = False

    def set_nueva_lista(self, archivos):
        self.derecha.set_nueva_lista(archivos)
