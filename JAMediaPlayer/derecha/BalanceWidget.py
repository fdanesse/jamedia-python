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
        
        self.__bandas = []
        for name in valores:
            row = valores.index(name)
            banda = ToolbarcontrolValores(name)
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
            self.__bandas.append(banda)

        reset = Gtk.Button("Reset")
        reset.connect("clicked", self.__reset)
        reset.get_style_context().add_class("resetbutton")
        self.attach(reset, 0, 10, 5, 6)

        self.show_all()

        self.set_size_request(250, -1)

    def __emit_senial(self, widget, valor, tipo):
        self.emit('balance-valor', valor, tipo)

    def __reset(self, button):
        for banda in self.__bandas:
            valor = 50.0
            if banda.name == "Gamma":
                valor = 10.0
            banda.set_progress(valor)
            tipo = banda.name
            if banda.name == "Saturación":
                tipo = "Saturacion"
            if banda.name == "Matíz":
                tipo = "Matiz"
            self.emit('balance-valor', valor, tipo.lower())


class ToolbarcontrolValores(Gtk.Toolbar):

    __gsignals__ = {
    'valor': (GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self, label):

        Gtk.Toolbar.__init__(self)

        self.name = label
        self.progress = BarraProgreso()
        self.progress.get_style_context().add_class("equalizerscale")
        
        self.__frame = Gtk.Frame()
        self.__frame.set_label(" %s " % (self.name))
        self.__frame.set_label_align(0.5, 1.0)

        event = Gtk.EventBox()
        event.add(self.progress)
        self.__frame.add(event)
        self.__frame.show_all()

        item = Gtk.ToolItem()
        item.set_expand(True)
        item.add(self.__frame)
        self.insert(item, -1)

        self.show_all()

        self.progress.escala.connect("change-value", self.__moveSlider)

    def __moveSlider(self, widget, scroll, value):
        ret = value
        if value < 0.0:
            ret = 0.0
            self.set_progress(ret)
        elif value > 100.0:
            ret = 100.0
            self.set_progress(ret)
        self.emit("valor", ret)
        self.__frame.set_label("%s: %s%s" % (self.name, int(ret), "%"))

    def set_progress(self, valor):
        GLib.idle_add(self.progress.escala.get_adjustment().set_value, valor)
        self.__frame.set_label("%s: %s%s" % (self.name, int(valor), "%"))
