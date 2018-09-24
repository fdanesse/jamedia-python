# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso


class BalanceWidget(Gtk.Table):

    __gsignals__ = {
    'balance-valor': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,(GObject.TYPE_FLOAT, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.Table.__init__(self, rows=5, columns=1, homogeneous=True)

        # FIXME: Agregar botón reset
        self.__brillo = ToolbarcontrolValores("Brillo")
        self.__contraste = ToolbarcontrolValores("Contraste")
        self.__saturacion = ToolbarcontrolValores("Saturación")
        self.__hue = ToolbarcontrolValores("Matíz")
        self.__gamma = ToolbarcontrolValores("Gamma")

        self.attach(self.__brillo, 0, 1, 0, 1)
        self.attach(self.__contraste, 0, 1, 1, 2)
        self.attach(self.__saturacion, 0, 1, 2, 3)
        self.attach(self.__hue, 0, 1, 3, 4)
        self.attach(self.__gamma, 0, 1, 4, 5)

        self.show_all()

        self.set_size_request(150, -1)

        self.__brillo.connect('valor',self.__emit_senial, 'brillo')
        self.__contraste.connect('valor',self.__emit_senial, 'contraste')
        self.__saturacion.connect('valor',self.__emit_senial, 'saturacion')
        self.__hue.connect('valor',self.__emit_senial, 'hue')
        self.__gamma.connect('valor',self.__emit_senial, 'gamma')

        self.set_balance()

    def __emit_senial(self, widget, valor, tipo):
        self.emit('balance-valor', valor, tipo)

    def set_balance(self, brillo=50.0, contraste=50.0, saturacion=50.0, hue=50.0, gamma=10.0):
        if saturacion != None: self.__saturacion.set_progress(saturacion)
        if contraste != None: self.__contraste.set_progress(contraste)
        if brillo != None: self.__brillo.set_progress(brillo)
        if hue != None: self.__hue.set_progress(hue)
        if gamma != None: self.__gamma.set_progress(gamma)


class ToolbarcontrolValores(Gtk.Toolbar):

    __gsignals__ = {
    'valor': (GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self, label):

        Gtk.Toolbar.__init__(self)

        self.__titulo = label
        self.__escala = BarraProgreso()

        self.__frame = Gtk.Frame()
        self.__frame.set_label(self.__titulo)
        self.__frame.set_label_align(0.5, 1.0)

        event = Gtk.EventBox()
        event.add(self.__escala)
        self.__frame.add(event)
        self.__frame.show_all()

        item = Gtk.ToolItem()
        item.set_expand(True)
        item.add(self.__frame)
        self.insert(item, -1)

        self.show_all()

        self.__escala.escala.connect("motion-notify-event", self.__user_set_value)

    def __user_set_value(self, widget, event):
        valor = self.__escala.escala.get_adjustment().get_value()
        self.emit("valor", valor)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(valor), "%"))

    def set_progress(self, valor):
        GLib.idle_add(self.__escala.escala.get_adjustment().set_value, valor)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(valor), "%"))
