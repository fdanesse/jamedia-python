#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf
from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar


class PlayerControls(Gtk.EventBox):
    """
    Controles de reproduccion: play/pausa, stop, siguiente, atras.
    """

    __gsignals__ = {
    "accion-controls": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        vbox = Gtk.HBox()

        self.pix_play = GdkPixbuf.Pixbuf.new_from_file_at_size(
            os.path.join(ICONS_PATH, "play.svg"), 24, 24)
        self.pix_paused = GdkPixbuf.Pixbuf.new_from_file_at_size(
            os.path.join(ICONS_PATH, "pausa.svg"), 24, 24)

        self.atras = JAMediaToolButton(pixels=24)
        archivo = os.path.join(ICONS_PATH, "siguiente.svg")
        self.atras.set_imagen(archivo=archivo, flip=True, rotacion=False)
        self.atras.set_tooltip_text("Anterior")
        self.atras.connect("clicked", self.__emit_accion, "atras")
        vbox.pack_start(self.atras, False, True, 0)

        self.play = JAMediaToolButton(pixels=24)
        archivo = os.path.join(ICONS_PATH, "play.svg")
        self.play.set_imagen(archivo=archivo, flip=False, rotacion=False)
        self.play.set_tooltip_text("Reproducir")
        self.play.connect("clicked", self.__emit_accion, "pausa-play")
        vbox.pack_start(self.play, False, True, 0)

        self.siguiente = JAMediaToolButton(pixels=24)
        archivo = os.path.join(ICONS_PATH, "siguiente.svg")
        self.siguiente.set_imagen(archivo=archivo, flip=False, rotacion=False)
        self.siguiente.set_tooltip_text("Siguiente")
        self.siguiente.connect("clicked", self.__emit_accion, "siguiente")
        vbox.pack_start(self.siguiente, False, True, 0)

        self.stop = JAMediaToolButton(pixels=24)
        archivo = os.path.join(ICONS_PATH, "stop.svg")
        self.stop.set_imagen(archivo=archivo, flip=False, rotacion=False)
        self.stop.set_tooltip_text("Detener Reproducción")
        self.stop.connect("clicked", self.__emit_accion, "stop")
        vbox.pack_start(self.stop, False, True, 0)

        self.add(vbox)
        self.show_all()

    def __emit_accion(self, widget, accion):
        self.emit("accion-controls", accion)

    def set_paused(self):
        self.play.set_paused(self.pix_play)

    def set_playing(self):
        self.play.set_playing(self.pix_paused)

    def activar(self, valor):
        if valor == 0:
            map(insensibilizar, [self.atras, self.play,
                self.siguiente, self.stop])
        elif valor == 1:
            map(insensibilizar, [self.atras, self.siguiente])
            map(sensibilizar, [self.play, self.stop])
        else:
            map(sensibilizar, [self.atras, self.play,
                self.siguiente, self.stop])


class JAMediaToolButton(Gtk.ToolButton):

    def __init__(self, pixels=34):

        Gtk.ToolButton.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        self.estado = False
        self.pixels = pixels
        self.imagen = Gtk.Image()
        self.set_icon_widget(self.imagen)
        self.imagen.show()

        self.imagen.set_size_request(self.pixels, self.pixels)
        self.show_all()

    def set_imagen(self, archivo=None, flip=False, rotacion=False):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
            os.path.join(archivo), self.pixels, self.pixels)
        if flip:
            pixbuf = pixbuf.flip(True)
        if rotacion:
            pixbuf = pixbuf.rotate_simple(rotacion)
        self.imagen.set_from_pixbuf(pixbuf)

    def set_playing(self, pixbuf):
        if self.estado:
            return
        self.estado = True
        self.imagen.set_from_pixbuf(pixbuf)

    def set_paused(self, pixbuf):
        if not self.estado:
            return
        self.estado = False
        self.imagen.set_from_pixbuf(pixbuf)
