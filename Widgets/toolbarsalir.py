# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador


class ToolbarSalir(Gtk.Toolbar):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarsalir')
        self.set_name('toolbarsalir')

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        boton = Gtk.ToolButton()
        boton.set_label('Salir')
        boton.set_tooltip_text("Salir")
        boton.connect("clicked", self.__emit_salir)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        boton = Gtk.ToolButton()
        boton.set_label('Cancelar')
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def __emit_salir(self, widget):
        self.cancelar()
        self.emit('salir')

    def run(self):
        if self.get_visible():
            self.cancelar()
        else:
            self.show()

    def cancelar(self, widget=None):
        self.hide()
        