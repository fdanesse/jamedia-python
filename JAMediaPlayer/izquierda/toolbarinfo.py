#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar


class ToolbarInfo(Gtk.EventBox):

    __gsignals__ = {
    'rotar': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    'actualizar_streamings': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, [])}

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

        item = Gtk.ToolItem()
        label = Gtk.Label("Ocultar Controles:")
        label.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))
        label.show()
        item.add(label)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        switch = Gtk.CheckButton()
        item = Gtk.ToolItem()
        item.set_expand(False)
        item.add(switch)
        toolbar.insert(item, -1)

        archivo = os.path.join(ICONS_PATH, "iconplay.svg")
        self.descarga = get_boton(archivo, flip=False,
            rotacion=GdkPixbuf.PixbufRotation.CLOCKWISE, pixels=24)
        self.descarga.set_tooltip_text("Actualizar Streamings")
        self.descarga.set_sensitive(False)
        self.descarga.connect("clicked", self.__emit_actualizar_streamings)
        toolbar.insert(self.descarga, -1)

        self.add(toolbar)
        self.show_all()

        switch.connect('button-press-event', self.__set_controles_view)

    def __emit_actualizar_streamings(self, widget):
        self.emit('actualizar_streamings')

    def __emit_rotar(self, widget):
        if widget == self.boton_derecha:
            self.emit('rotar', "Derecha")
        elif widget == self.boton_izquierda:
            self.emit('rotar', "Izquierda")

    def __set_controles_view(self, widget, senial):
        self.ocultar_controles = not widget.get_active()

    def set_video(self, valor):
        if valor:
            map(sensibilizar, [self.boton_izquierda, self.boton_derecha])
        else:
            map(insensibilizar, [self.boton_izquierda, self.boton_derecha])

    def set_ip(self, valor):
        self.descarga.set_sensitive(valor)
        