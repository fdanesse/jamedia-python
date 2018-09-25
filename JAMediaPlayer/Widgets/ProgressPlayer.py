# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador


class ProgressPlayer(Gtk.Toolbar):

    __gsignals__ = {
    "seek": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, )),
    "volumen": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.__presed = False
        self.get_style_context().add_class("progressplayer")

        self.__progressBar = BarraProgreso()
        self.__volumen = Gtk.VolumeButton()
        self.__volumen.set_css_name('volumen')
        self.__volumen.set_name('volumen')
        self.__volumen.set_value(0.1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        item = Gtk.ToolItem()
        item.set_expand(True)
        item.add(self.__progressBar)
        self.insert(item, -1)
        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        item = Gtk.ToolItem()
        item.set_expand(False)
        item.add(self.__volumen)
        self.insert(item, -1)
        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.__progressBar.escala.connect("button-press-event", self.__button_press_event)
        self.__progressBar.escala.connect("button-release-event", self.__button_release_event)
        self.__progressBar.escala.connect("motion-notify-event", self.__motion_notify_event)
        self.__volumen.connect("value-changed", self.__set_volumen)

        self.show_all()

    def __set_volumen(self, widget, valor):
        self.emit('volumen', valor)

    def set_progress(self, valor):
        if not self.__presed:
            adj = self.__progressBar.escala.get_adjustment()
            GLib.idle_add(adj.set_value, valor)

    def __button_press_event(self, widget, event):
        self.__presed = True
    
    def __button_release_event(self, widget, event):
        self.__presed = False

    def __motion_notify_event(self, widget, event):
        if self.__presed:
            adj = self.__progressBar.escala.get_adjustment()
            self.emit("seek", adj.get_value())


class BarraProgreso(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        # NOTA: tambien se puede hacer: __gtype_name__ = 'BarraProgreso'
        # self.set_css_name('progressplayerscale')
        # self.set_name('progressplayerscale')

        self.escala = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        # FIXME: Mejorar saltos del ajuste
        self.escala.set_adjustment(Gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))
        self.escala.set_digits(0)
        self.escala.set_draw_value(False)

        self.add(self.escala)
        self.show_all()

        # NOTA: Necesario para que funcione la escala
        self.set_size_request(-1, 24)
