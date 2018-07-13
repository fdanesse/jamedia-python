# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class ToolbarAccionListasVideos(Gtk.Toolbar):

    __gsignals__ = {
    "ok": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        style_context = self.get_style_context()
        style_context.add_class("toolbaraccionvideos")

        self.__box = None

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        boton = Gtk.ToolButton()
        boton.set_label('Cancelar')
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        boton = Gtk.ToolButton()
        boton.set_label('Limpiar')
        boton.set_tooltip_text("Limpiar")
        boton.connect("clicked", self.__realizar_accion)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def __realizar_accion(self, widget):
        self.cancelar()
        GLib.idle_add(self.__emit_ok)

    def __emit_ok(self):
        self.emit('ok', self.__box)

    def set_clear(self, box):
        self.__box = box
        if self.get_visible():
            self.cancelar()
        else:
            self.show()

    def cancelar(self, widget=None):
        self.objetos = None
        self.hide()
        