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

        Gtk.Table.__init__(self, rows=6, columns=10, homogeneous=True)

        valores = ["Brillo", "Contraste", "Saturación", "Matíz", "Gamma"]

        for valor in valores:
            row = valores.index(valor)
            banda = ToolbarcontrolValores(" %s " % (valor))
            if valor == "Gamma":
                banda.set_progress(10.0)
            else:
                banda.set_progress(50.0)
            banda.get_style_context().add_class("equalizervalue")
            banda.connect('valor', self.__emit_senial, valor.lower())
            self.attach(banda, 0, 10, row, row+1)

        reset = Gtk.Button("Reset")
        reset.get_style_context().add_class("resetbutton")
        self.attach(reset, 0, 10, 5, 6)

        self.show_all()

        self.set_size_request(250, -1)

    def __emit_senial(self, widget, valor, tipo):
        self.emit('balance-valor', valor, tipo)


class ToolbarcontrolValores(Gtk.Toolbar):

    __gsignals__ = {
    'valor': (GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self, label):

        Gtk.Toolbar.__init__(self)

        self.__titulo = label
        self.__escala = BarraProgreso()
        self.__escala.get_style_context().add_class("equalizerscale")
        
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
