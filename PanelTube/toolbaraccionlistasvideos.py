# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class ToolbarAccionListasVideos(Gtk.Toolbar):

    __gsignals__ = {
    "ok": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.objetos = None

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        '''archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__realizar_accion)
        self.insert(boton, -1)'''

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def __realizar_accion(self, widget):
        objetos = self.objetos
        self.cancelar()
        GLib.idle_add(self.__emit_ok, objetos)

    def __emit_ok(self, objetos):
        self.emit('ok', objetos)

    def set_accion(self, objetos):
        self.objetos = objetos
        self.label.set_text("¿Eliminar?")
        self.show_all()

    def cancelar(self, widget=None):
        self.objetos = None
        self.label.set_text("")
        self.hide()
        