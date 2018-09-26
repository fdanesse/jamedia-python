# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso
from JAMediaPlayer.derecha.BalanceWidget import ToolbarcontrolValores


class EqualizerWidget(Gtk.Table):

    __gsignals__ = {
    'equalizer-valor': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,(GObject.TYPE_FLOAT, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.Table.__init__(self, rows=11, columns=10, homogeneous=True)

        self.__bandas = []
        for row in range(0, 10):
            banda = ToolbarcontrolValores("Banda " + str(row))
            banda.get_style_context().add_class("equalizervalue")
            banda.set_progress((0+24)*100/36)  # en el reproductor un rango -24 - +12 default 0
            banda.connect('valor', self.__emit_senial, "band" + str(row))
            self.attach(banda, 0, 10, row, row+1)
            self.__bandas.append(banda)

        reset = Gtk.Button("Reset")
        reset.connect("clicked", self.__reset)
        reset.get_style_context().add_class("resetbutton")
        self.attach(reset, 0, 10, 10, 11)

        self.show_all()

        self.set_size_request(250, -1)

    def __emit_senial(self, widget, valor, tipo):
        self.emit('equalizer-valor', valor, tipo)

    def __reset(self, button):
        for banda in self.__bandas:
            banda.set_progress((0+24)*100/36)
            tipo = banda.name.lower().replace("banda ", "band")
            self.emit('equalizer-valor', (0+24)*100/36, tipo)
