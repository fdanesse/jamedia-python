#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso

from JAMediaPlayer.Globales import get_colors


class BalanceWidget(Gtk.EventBox):

    __gsignals__ = {
    'balance-valor': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,
        (GObject.TYPE_FLOAT, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        tabla = Gtk.Table(rows=5, columns=1, homogeneous=True)

        self.modify_bg(
            Gtk.StateType.NORMAL, get_colors("window"))
        tabla.modify_bg(
            Gtk.StateType.NORMAL, get_colors("window"))

        self.__brillo = ToolbarcontrolValores("Brillo")
        self.__contraste = ToolbarcontrolValores("Contraste")
        self.__saturacion = ToolbarcontrolValores("Saturación")
        self.__hue = ToolbarcontrolValores("Matíz")
        self.__gamma = ToolbarcontrolValores("Gamma")

        tabla.attach(self.__brillo, 0, 1, 0, 1)
        tabla.attach(self.__contraste, 0, 1, 1, 2)
        tabla.attach(self.__saturacion, 0, 1, 2, 3)
        tabla.attach(self.__hue, 0, 1, 3, 4)
        tabla.attach(self.__gamma, 0, 1, 4, 5)

        self.add(tabla)
        self.show_all()

        self.set_size_request(150, -1)

        self.__brillo.connect('valor',
            self.__emit_senial, 'brillo')
        self.__contraste.connect('valor',
            self.__emit_senial, 'contraste')
        self.__saturacion.connect('valor',
            self.__emit_senial, 'saturacion')
        self.__hue.connect('valor',
            self.__emit_senial, 'hue')
        self.__gamma.connect('valor',
            self.__emit_senial, 'gamma')

    def __emit_senial(self, widget, valor, tipo):
        self.emit('balance-valor', valor, tipo)

    def set_balance(self, brillo=50.0, contraste=50.0,
        saturacion=50.0, hue=50.0, gamma=10.0):
        if saturacion != None:
            self.__saturacion.set_progress(saturacion)
        if contraste != None:
            self.__contraste.set_progress(contraste)
        if brillo != None:
            self.__brillo.set_progress(brillo)
        if hue != None:
            self.__hue.set_progress(hue)
        if gamma != None:
            self.__gamma.set_progress(gamma)


class ToolbarcontrolValores(Gtk.Toolbar):

    __gsignals__ = {
    'valor': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self, label):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(
            Gtk.StateType.NORMAL, get_colors("window"))

        self.__titulo = label
        self.__escala = BarraProgreso()

        item = Gtk.ToolItem()
        item.set_expand(True)

        self.__frame = Gtk.Frame()
        self.__frame.set_border_width(4)
        self.__frame.set_label(self.__titulo)
        self.__frame.get_property("label-widget").modify_fg(
            0, get_colors("drawingplayer"))
        self.__frame.set_label_align(0.5, 1.0)
        event = Gtk.EventBox()
        event.set_border_width(4)
        event.modify_bg(
            Gtk.StateType.NORMAL, get_colors("window"))
        event.add(self.__escala)
        self.__frame.add(event)
        self.__frame.show_all()
        item.add(self.__frame)
        self.insert(item, -1)

        self.show_all()

        self.__escala.escala.connect(
            "motion-notify-event", self.__user_set_value)

    def __user_set_value(self, widget, event):
        valor = self.__escala.escala.get_adjustment().get_value()
        self.emit("valor", valor)
        self.__frame.set_label(
            "%s: %s%s" % (self.__titulo, int(valor), "%"))

    def set_progress(self, valor):
        GLib.idle_add(
            self.__escala.escala.get_adjustment().set_value, valor)
        self.__frame.set_label(
            "%s: %s%s" % (self.__titulo, int(valor), "%"))
