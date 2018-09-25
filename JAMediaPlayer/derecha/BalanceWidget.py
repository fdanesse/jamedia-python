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

        for name in valores:
            row = valores.index(name)
            banda = ToolbarcontrolValores(" %s " % (name))
            if name == "Gamma":
                banda.set_progress(10.0)
            else:
                banda.set_progress(50.0)
            tipo = name
            if name == "Saturación":
                tipo = "Saturacion"
            if name == "Matíz":
                tipo = "Matiz"
            banda.get_style_context().add_class("equalizervalue")
            banda.connect('valor', self.__emit_senial, tipo.lower())
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
        self.__progressBar = BarraProgreso()
        self.__progressBar.get_style_context().add_class("equalizerscale")
        
        self.__frame = Gtk.Frame()
        self.__frame.set_label(self.__titulo)
        self.__frame.set_label_align(0.5, 1.0)

        event = Gtk.EventBox()
        event.add(self.__progressBar)
        self.__frame.add(event)
        self.__frame.show_all()

        item = Gtk.ToolItem()
        item.set_expand(True)
        item.add(self.__frame)
        self.insert(item, -1)

        self.show_all()

        self.__progressBar.escala.connect("change-value", self.__moveSlider)

    def __moveSlider(self, widget, scroll, value):
        ret = value
        if value < 0.0:
            ret = 0.0
            self.set_progress(ret)
        elif value > 100.0:
            ret = 100.0
            self.set_progress(ret)
        self.emit("valor", ret)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(ret), "%"))

    def set_progress(self, valor):
        GLib.idle_add(self.__progressBar.escala.get_adjustment().set_value, valor)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(valor), "%"))
