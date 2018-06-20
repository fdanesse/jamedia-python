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
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton

BASE_PATH = os.path.dirname(os.path.dirname(__file__))


class ToolbarSalir(Gtk.Toolbar):
    """
    Toolbar para confirmar salir de la aplicación.
    """

    #__gtype_name__ = 'ToolbarSalir'

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("download"))

        self.insert(get_separador(
            draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(
            BASE_PATH, "Iconos", "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        self.insert(boton, -1)

        self.insert(get_separador(
            draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)

        self.insert(get_separador(
            draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(
            BASE_PATH, "Iconos", "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__emit_salir)
        self.insert(boton, -1)

        self.insert(get_separador(
            draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def __emit_salir(self, widget):
        """
        Confirma Salir de la aplicación.
        """
        self.cancelar()
        self.emit('salir')

    def run(self, nombre_aplicacion):
        """
        La toolbar se muestra y espera confirmación.
        """
        self.label.set_text("¿Salir de %s?" % (nombre_aplicacion))
        self.show()

    def cancelar(self, widget=None):
        """
        Cancela salir de la aplicación.
        """
        self.label.set_text("")
        self.hide()
        