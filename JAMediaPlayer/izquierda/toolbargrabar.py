# -*- coding: utf-8 -*-

# FIXME: Borrar si no se usa
'''
import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class ToolbarGrabar(Gtk.EventBox):
    """
    Informa al usuario cuando se está grabando desde un streaming.
    """

    __gsignals__ = {
    "stop": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))

        self.colors = [get_colors("window"), get_colors("naranaja")]
        self.color = self.colors[0]

        self.toolbar = Gtk.Toolbar()
        self.toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))

        self.toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(ICONS_PATH, "stop.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Detener")
        self.toolbar.insert(boton, -1)

        self.toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("Grabador Detenido.")
        self.label.modify_bg(Gtk.StateType.NORMAL, self.colors[0])
        self.label.show()
        item.add(self.label)
        self.toolbar.insert(item, -1)

        self.add(self.toolbar)

        self.show_all()

        boton.connect("clicked", self.__emit_stop)

    def __emit_stop(self, widget=None, event=None):
        self.stop()
        self.emit("stop")

    def __update(self):
        if self.color == self.colors[0]:
            self.color = self.colors[1]
        elif self.color == self.colors[1]:
            self.color = self.colors[0]
        self.label.modify_bg(Gtk.StateType.NORMAL, self.color)
        if not self.get_visible():
            self.show()

    def stop(self):
        self.color = self.colors[0]
        self.label.modify_bg(Gtk.StateType.NORMAL, self.color)
        self.label.set_text("Grabador Detenido.")
        self.hide()

    def set_info(self, datos):
        self.label.set_text(datos)
        self.__update()
'''