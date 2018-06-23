#!/usr/bin/env python
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


class Toolbar_Guardar(Gtk.Toolbar):
    """
    Toolbar con widgets para guardar una lista de videos.
    """

    __gsignals__ = {
    "ok": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))

        item = Gtk.ToolItem()
        label = Gtk.Label("Nombre: ")
        #label.modify_fg(Gtk.StateType.NORMAL, get_colors("window1"))
        label.show()
        item.add(label)
        self.insert(item, -1)

        item = Gtk.ToolItem()
        item.set_expand(True)
        self.entrytext = Gtk.Entry()
        self.entrytext.set_size_request(50, -1)
        self.entrytext.set_max_length(10)
        self.entrytext.set_tooltip_text(
            "Nombre para Esta Lista")
        self.entrytext.show()
        self.entrytext.connect('activate', self.__emit_ok)
        item.add(self.entrytext)
        self.insert(item, -1)

        self.insert(get_separador(
            draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Guardar")
        boton.connect("clicked", self.__emit_ok)
        self.insert(boton, -1)

        self.show_all()

    def __emit_ok(self, widget):
        texto = self.entrytext.get_text().replace(" ", "_")
        self.cancelar()
        if texto:
            self.emit("ok", texto)

    def cancelar(self, widget=None):
        self.entrytext.set_text("")
        self.hide()
