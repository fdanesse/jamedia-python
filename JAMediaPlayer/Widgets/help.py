#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import ICONS_PATH


class Help(Gtk.Dialog):

    def __init__(self, parent=None):

        Gtk.Dialog.__init__(self, parent=parent,
            buttons=("Cerrar", Gtk.ResponseType.ACCEPT))

        self.set_decorated(False)
        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("widgetvideoitem"))
        self.set_border_width(15)

        tabla1 = Gtk.Table(
            columns=5, rows=2, homogeneous=False)

        vbox = Gtk.HBox()
        archivo = os.path.join(ICONS_PATH, "play.svg")
        self.anterior = get_boton(archivo, flip=True,
            pixels=24, tooltip_text="Anterior")

        self.anterior.connect("clicked", self.__switch)
        self.anterior.show()
        vbox.pack_start(self.anterior, False, False, 0)

        archivo = os.path.join(ICONS_PATH, "play.svg")
        self.siguiente = get_boton(archivo, pixels=24,
            tooltip_text="Siguiente")

        self.siguiente.connect("clicked", self.__switch)
        self.siguiente.show()
        vbox.pack_end(self.siguiente, False, False, 0)

        tabla1.attach_defaults(vbox, 0, 5, 0, 1)

        self.helps = []

        for x in range(3, 7):
            try:
                help = Gtk.Image()
                help.set_from_file(
                    os.path.join(ICONS_PATH, "help-%s.svg" % x))
                tabla1.attach_defaults(help, 0, 5, 1, 2)
                self.helps.append(help)
            except:
                pass

        self.vbox.pack_start(tabla1, True, True, 0)
        self.vbox.show_all()

        self.__switch(None)

    def __switch(self, widget):
        if not widget:
            ocultar(self.helps[1:])
            self.anterior.hide()
            self.helps[0].show()
        else:
            index = self.__get_index_visible()
            helps = list(self.helps)
            new_index = index

            if widget == self.siguiente:
                if index < len(self.helps) - 1:
                    new_index += 1
            elif widget == self.anterior:
                if index > 0:
                    new_index -= 1

            helps.remove(helps[new_index])
            ocultar(helps)
            self.helps[new_index].show()

            if new_index > 0:
                self.anterior.show()
            else:
                self.anterior.hide()

            if new_index < self.helps.index(self.helps[-1]):
                self.siguiente.show()
            else:
                self.siguiente.hide()

    def __get_index_visible(self):
        for help in self.helps:
            if help.get_visible():
                return self.helps.index(help)
                