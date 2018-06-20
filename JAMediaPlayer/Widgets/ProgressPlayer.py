#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ICONS_PATH


class ProgressPlayer(Gtk.EventBox):

    __gsignals__ = {
    "seek": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT, )),
    "volumen": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        self.__presed = False

        self.__progressBar = BarraProgreso()
        self.__volumen = Gtk.VolumeButton()
        self.__volumen.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))
        self.__volumen.set_value(0.1)

        hbox = Gtk.HBox()
        hbox.pack_start(self.__progressBar, True, True, 0)
        hbox.pack_end(self.__volumen, False, False, 0)

        self.add(hbox)

        self.__progressBar.escala.connect(
            "button-press-event", self.__button_press_event)
        self.__progressBar.escala.connect(
            "button-release-event", self.__button_release_event)
        self.__progressBar.escala.connect(
            "motion-notify-event", self.__motion_notify_event)
        self.__volumen.connect("value-changed", self.__set_volumen)

        self.show_all()

    def __set_volumen(self, widget, valor):
        valor = int(valor * 10)
        self.emit('volumen', valor)
    
    def get_volumen(self):
        return int(self.__volumen.get_value() * 10)

    def set_progress(self, valor):
        if not self.__presed:
            GLib.idle_add(self.__progressBar.escala.get_adjustment().set_value, valor)

    def __button_press_event(self, widget, event):
        self.__presed = True
    
    def __button_release_event(self, widget, event):
        self.__presed = False

    def __motion_notify_event(self, widget, event):
        if self.__presed:
            self.emit("seek", self.__progressBar.escala.get_adjustment().get_value())


class BarraProgreso(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        self.escala = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL)
        self.escala.set_adjustment(Gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))
        self.escala.set_digits(0)
        self.escala.set_draw_value(False)

        self.add(self.escala)
        self.show_all()

        self.set_size_request(-1, 24)  #FIXME: Necesario para que funcione la escala
