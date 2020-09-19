# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador


class ToolbarAlerta(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.get_style_context().add_class('alertabusquedas')

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        item = Gtk.ToolItem()
        self.__label = Gtk.Label()
        item.add(self.__label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        boton = Gtk.ToolButton()
        boton.set_label('OK')
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def run(self, text):
        self.__label.set_text(text)
        self.show()

    def cancelar(self, widget=None):
        self.hide()
        