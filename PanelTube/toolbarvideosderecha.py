# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar_Videos_Derecha(Gtk.Toolbar):
    """
    toolbar inferior derecha para videos en descarga.
    """

    __gsignals__ = {
    "borrar": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    "mover_videos": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'comenzar_descarga': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer1"))

        archivo = os.path.join(ICONS_PATH, "iconplay.svg")
        boton = get_boton(archivo, flip=True, pixels=24)
        boton.set_tooltip_text("Quitar de Descargas")
        boton.connect("clicked", self.__emit_aencontrados)
        self.insert(boton, -1)

        archivo = os.path.join(ICONS_PATH, "alejar.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Borrar Lista")
        boton.connect("clicked", self.__emit_borrar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "iconplay.svg")
        boton = get_boton(archivo, flip=False, pixels=24, rotacion=GdkPixbuf.PixbufRotation.CLOCKWISE)
        boton.set_tooltip_text("Descargar")
        boton.connect("clicked", self.__emit_comenzar_descarga)
        self.insert(boton, -1)

        self.show_all()

    def __emit_comenzar_descarga(self, widget):
        """
        Para comenzar a descargar los videos en la lista de descargas.
        """
        self.emit('comenzar_descarga')

    def __emit_aencontrados(self, widget):
        """
        Para pasar los videos en descarga a la lista de encontrados.
        """
        self.emit('mover_videos')

    def __emit_borrar(self, widget):
        """
        Para borrar todos los videos de la lista.
        """
        self.emit('borrar')
