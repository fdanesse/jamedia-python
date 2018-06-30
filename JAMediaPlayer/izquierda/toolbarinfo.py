# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar
from JAMediaPlayer.Globales import get_toggle_boton


class ToolbarInfo(Gtk.EventBox):

    __gsignals__ = {'rotar': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        self.ocultar_controles = False

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "rotar.svg")
        self.boton_izquierda = get_boton(archivo, flip=False, pixels=24)
        self.boton_izquierda.set_tooltip_text("Izquierda")
        self.boton_izquierda.connect("clicked", self.__emit_rotar)
        toolbar.insert(self.boton_izquierda, -1)

        archivo = os.path.join(ICONS_PATH, "rotar.svg")
        self.boton_derecha = get_boton(archivo, flip=True, pixels=24)
        self.boton_derecha.set_tooltip_text("Derecha")
        self.boton_derecha.connect("clicked", self.__emit_rotar)
        toolbar.insert(self.boton_derecha, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "controls.svg")
        controls = get_toggle_boton(archivo, flip=True, pixels=24)
        controls.set_tooltip_text("Ocultar/Mostrar Controles")
        controls.connect("toggled", self.__set_controles_view)
        toolbar.insert(controls, -1)

        archivo = os.path.join(ICONS_PATH, "fullscreen.png")
        self.__full = get_toggle_boton(archivo, flip=True, pixels=24)
        self.__full.set_tooltip_text("Full/UnFull Screen")
        self.__full.connect("toggled", self.__set_full)
        toolbar.insert(self.__full, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        
        self.add(toolbar)
        self.show_all()

    def set_full(self, widget):
        self.__full.set_active(not self.__full.get_active())

    def __set_full(self, widget):
        win = self.get_toplevel()
        if self.__full.get_active():
            win.fullscreen()
        else:
            win.unfullscreen()

    def __emit_rotar(self, widget):
        if widget == self.boton_derecha:
            self.emit('rotar', "Derecha")
        elif widget == self.boton_izquierda:
            self.emit('rotar', "Izquierda")

    def __set_controles_view(self, widget):
        self.ocultar_controles = widget.get_active()

    def set_video(self, valor):
        if valor:
            sensibilizar([self.boton_izquierda, self.boton_derecha])
        else:
            insensibilizar([self.boton_izquierda, self.boton_derecha])
