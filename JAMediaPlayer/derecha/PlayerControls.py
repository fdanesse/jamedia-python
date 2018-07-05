# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar


class PlayerControls(Gtk.Toolbar):

    __gsignals__ = {"accion-controls": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarcontrols')
        self.set_name('toolbarcontrols')

        self.pix_play = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(ICONS_PATH, "play.svg"), 24, 24)
        self.pix_paused = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(ICONS_PATH, "pausa.svg"), 24, 24)

        self.atras = JAMediaToolButton(pixels=24)
        self.atras.set_imagen(archivo=os.path.join(ICONS_PATH, "siguiente.svg"), flip=True, rotacion=False)
        self.atras.set_tooltip_text("Anterior")
        self.atras.connect("clicked",self.__emit_accion, "atras")
        self.insert(self.atras, -1)

        self.play = JAMediaToolButton(pixels=24)
        self.play.set_imagen(archivo=os.path.join(ICONS_PATH, "play.svg"), flip=False, rotacion=False)
        self.play.set_tooltip_text("Play")
        self.play.connect("clicked",self.__emit_accion, "pausa-play")
        self.insert(self.play, -1)

        self.siguiente = JAMediaToolButton(pixels=24)
        self.siguiente.set_imagen(archivo=os.path.join(ICONS_PATH, "siguiente.svg"), flip=False, rotacion=False)
        self.siguiente.set_tooltip_text("Siguiente")
        self.siguiente.connect("clicked",self.__emit_accion, "siguiente")
        self.insert(self.siguiente, -1)

        self.stop = JAMediaToolButton(pixels=24)
        self.stop.set_imagen(archivo=os.path.join(ICONS_PATH, "stop.svg"),flip=False, rotacion=False)
        self.stop.set_tooltip_text("Detener Reproducción")
        self.stop.connect("clicked",self.__emit_accion, "stop")
        self.insert(self.stop, -1)

        self.show_all()

    def __emit_accion(self, widget, accion):
        self.emit("accion-controls", accion)

    def set_paused(self):
        self.play.set_tooltip_text("Pausa")
        self.play.set_paused(self.pix_play)

    def set_playing(self):
        self.play.set_tooltip_text("Play")
        self.play.set_playing(self.pix_paused)

    def activar(self, valor):
        if valor == 0:
            insensibilizar([self.atras, self.play, self.siguiente, self.stop])
        elif valor == 1:
            insensibilizar([self.atras, self.siguiente])
            sensibilizar([self.play, self.stop])
        else:
            sensibilizar([self.atras, self.play, self.siguiente, self.stop])


class JAMediaToolButton(Gtk.ToolButton):

    def __init__(self, pixels=34):

        Gtk.ToolButton.__init__(self)

        self.estado = False
        self.pixels = pixels
        self.imagen = Gtk.Image()
        self.set_icon_widget(self.imagen)
        self.imagen.show()

        self.imagen.set_size_request(self.pixels, self.pixels)
        self.show_all()

    def set_imagen(self, archivo=None,
        flip=False, rotacion=False):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(os.path.join(archivo), self.pixels, self.pixels)
        if flip:pixbuf = pixbuf.flip(True)
        if rotacion:pixbuf = pixbuf.rotate_simple(rotacion)
        self.imagen.set_from_pixbuf(pixbuf)

    def set_playing(self, pixbuf):
        if self.estado:return
        self.estado = True
        self.imagen.set_from_pixbuf(pixbuf)

    def set_paused(self, pixbuf):
        if not self.estado:return
        self.estado = False
        self.imagen.set_from_pixbuf(pixbuf)
