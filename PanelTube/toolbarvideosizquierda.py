# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar_Videos_Izquierda(Gtk.Toolbar):

    __gsignals__ = {
    "borrar": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    "mover_videos": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarvideos')
        self.set_name('toolbarvideos')

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        boton = get_boton(os.path.join(ICONS_PATH, "alejar.svg"), flip=False, pixels=24, tooltip_text="Borrar Lista")
        boton.connect("clicked", self.__emit_borrar)
        self.insert(boton, -1)

        boton = get_boton(os.path.join(ICONS_PATH, "play.svg"), flip=False, pixels=24, tooltip_text="Enviar a Descargas")
        boton.connect("clicked", self.__emit_adescargas)
        self.insert(boton, -1)

        self.show_all()

    def __emit_adescargas(self, widget):
        self.emit('mover_videos')

    def __emit_borrar(self, widget):
        self.emit('borrar')
