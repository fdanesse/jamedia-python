#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from PanelTube.jamediatube import JAMediaYoutube

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_boton

BASE_PATH = os.path.dirname(__file__)


class Help(Gtk.Dialog):

    #__gtype_name__ = 'TubeHelp'

    def __init__(self, parent=None):

        Gtk.Dialog.__init__(self, parent=parent, title="",
            buttons=("Cerrar", Gtk.ResponseType.OK))

        self.set_decorated(False)
        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window1"))
        self.set_border_width(15)

        tabla1 = Gtk.Table(columns=5, rows=2, homogeneous=False)

        vbox = Gtk.HBox()
        archivo = os.path.join(BASE_PATH, "Iconos", "play.svg")
        self.anterior = get_boton(archivo, flip=True, pixels=24,
            tooltip_text="Anterior")
        self.anterior.connect("clicked", self.__switch)
        self.anterior.show()
        vbox.pack_start(self.anterior, False, False, 0)

        archivo = os.path.join(BASE_PATH, "Iconos", "play.svg")
        self.siguiente = get_boton(archivo, pixels=24,
            tooltip_text="Siguiente")
        self.siguiente.connect("clicked", self.__switch)
        self.siguiente.show()
        vbox.pack_end(self.siguiente, False, False, 0)

        tabla1.attach_defaults(vbox, 0, 5, 0, 1)

        self.helps = []
        for x in range(1, 3):
            help = Gtk.Image()
            help.set_from_file(os.path.join(BASE_PATH,
                "Iconos", "help-%s.svg" % x))
            tabla1.attach_defaults(help, 0, 5, 1, 2)
            self.helps.append(help)

        self.vbox.pack_start(tabla1, True, True, 0)
        self.vbox.show_all()
        self.__switch(None)

    def __ocultar(self, objeto):
        if objeto.get_visible():
            objeto.hide()

    def __switch(self, widget):
        if not widget:
            map(self.__ocultar, self.helps[1:])
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
            map(self.__ocultar, helps)
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