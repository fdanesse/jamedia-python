#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Toolbars.py por:
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
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from Widgets import Credits
from Widgets import Help

from Globales import get_colors
from Globales import get_separador
from Globales import get_boton
from Globales import get_my_files_directory
from Globales import describe_acceso_uri
from Globales import copiar
from Globales import borrar
from Globales import mover

ICONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Iconos")


class Toolbar(Gtk.EventBox):
    """
    Toolbar principal de JAMedia.
    """

    __gsignals__ = {
    'accion': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(ICONS_PATH, "JAMedia.svg")
        boton = get_boton(archivo, flip=False, pixels=35)
        boton.set_tooltip_text("Creditos")
        boton.connect("clicked", self.__show_credits)
        toolbar.insert(boton, -1)

        archivo = os.path.join(ICONS_PATH, "JAMedia-help.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Ayuda")
        boton.connect("clicked", self.__show_help)
        toolbar.insert(boton, -1)

        archivo = os.path.join(ICONS_PATH, "configurar.svg")
        self.configurar = get_boton(archivo, flip=False, pixels=24)
        self.configurar.set_tooltip_text("Configuraciones")
        self.configurar.connect("clicked", self.__emit_accion, "show-config")
        toolbar.insert(self.configurar, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Salir")
        boton.connect("clicked", self.__emit_accion, "salir")
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.add(toolbar)
        self.show_all()

    def __show_credits(self, widget):
        dialog = Credits(parent=self.get_toplevel())
        dialog.run()
        dialog.destroy()

    def __show_help(self, widget):
        dialog = Help(parent=self.get_toplevel())
        dialog.run()
        dialog.destroy()

    def __emit_accion(self, widget, accion):
        self.emit('accion', accion)


class ToolbarAccion(Gtk.EventBox):
    """
    Toolbar para que el usuario confirme las acciones que se realizan sobre
    items que se seleccionan en la lista de reproduccion.
        (Borrar, mover, copiar, quitar).
    """

    __gsignals__ = {
    "grabar": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "accion-stream": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,
        GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        self.lista = None
        self.accion = None
        self.iter = None

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        toolbar.insert(boton, -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))
        self.label.show()
        item.add(self.label)
        toolbar.insert(item, -1)

        archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__realizar_accion)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()

    def __realizar_accion(self, widget):
        """
        Ejecuta una accion sobre un archivo o streaming en la lista.
        """
        uri = self.lista.get_model().get_value(self.iter, 2)
        if self.accion == "Quitar":
            path = self.lista.get_model().get_path(self.iter)
            path = (path[0] - 1, )
            self.lista.get_model().remove(self.iter)
            self.__reselect(path)
        else:
            if describe_acceso_uri(uri):
                if self.accion == "Copiar":
                    if os.path.isfile(uri):
                        copiar(uri, get_my_files_directory())
                elif self.accion == "Borrar":
                    if os.path.isfile(uri):
                        if borrar(uri):
                            path = self.lista.get_model().get_path(self.iter)
                            path = (path[0] - 1, )
                            self.lista.get_model().remove(self.iter)
                            self.__reselect(path)
                elif self.accion == "Mover":
                    if os.path.isfile(uri):
                        if mover(uri, get_my_files_directory()):
                            path = self.lista.get_model().get_path(self.iter)
                            path = (path[0] - 1, )
                            self.lista.get_model().remove(self.iter)
                            self.__reselect(path)
            else:
                if self.accion == "Borrar":
                    self.emit("accion-stream", "Borrar", uri)
                    path = self.lista.get_model().get_path(self.iter)
                    path = (path[0] - 1, )
                    self.lista.get_model().remove(self.iter)
                    self.__reselect(path)
                elif self.accion == "Copiar":
                    self.emit("accion-stream", "Copiar", uri)
                elif self.accion == "Mover":
                    self.emit("accion-stream", "Mover", uri)
                    path = self.lista.get_model().get_path(self.iter)
                    path = (path[0] - 1, )
                    self.lista.get_model().remove(self.iter)
                    self.__reselect(path)
                elif self.accion == "Grabar":
                    self.emit("grabar", uri)
        self.cancelar()

    def __reselect(self, path):
        try:
            if path[0] > -1:
                self.lista.get_selection().select_iter(
                    self.lista.get_model().get_iter(path))
            else:
                self.lista.seleccionar_primero()
        except:
            self.lista.seleccionar_primero()

    def set_accion(self, lista, accion, _iter):
        """
        Configura una accion sobre un archivo o streaming y muestra
        toolbaraccion para que el usuario confirme o cancele dicha accion.
        """
        self.lista = lista
        self.accion = accion
        self.iter = _iter
        if self.lista and self.accion and self.iter:
            uri = self.lista.get_model().get_value(self.iter, 2)
            texto = uri
            if os.path.exists(uri):
                texto = os.path.basename(uri)
            if len(texto) > 30:
                texto = " . . . " + str(texto[len(texto) - 30:-1])
            self.label.set_text("¿%s?: %s" % (accion, texto))
            self.show_all()

    def cancelar(self, widget=None):
        self.label.set_text("")
        self.lista = None
        self.accion = None
        self.iter = None
        self.hide()


class ToolbarSalir(Gtk.EventBox):
    """
    Toolbar para confirmar salir de la aplicación.
    """

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))
        self.label.show()
        item.add(self.label)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__emit_salir)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()

    def __emit_salir(self, widget):
        self.cancelar()
        self.emit('salir')

    def run(self, nombre_aplicacion):
        self.label.set_text("¿Salir de %s?" % (nombre_aplicacion))
        self.show()

    def cancelar(self, widget=None):
        self.label.set_text("")
        self.hide()


class ToolbarAddStream(Gtk.EventBox):
    """
    Toolbar para agregar streamings.
    """

    __gsignals__ = {
    "add-stream": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,
        GObject.TYPE_STRING, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        self.tipo = None

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        frame = Gtk.Frame()
        frame.set_label('Nombre')
        self.nombre = Gtk.Entry()
        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        event.set_border_width(4)
        event.add(self.nombre)
        frame.add(event)
        frame.show_all()
        item = Gtk.ToolItem()
        item.add(frame)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        frame = Gtk.Frame()
        frame.set_label('URL')
        self.url = Gtk.Entry()
        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        event.set_border_width(4)
        event.add(self.url)
        frame.add(event)
        frame.show_all()
        item = Gtk.ToolItem()
        self.url.show()
        item.add(frame)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__emit_add_stream)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()

    def __emit_add_stream(self, widget):
        nombre, url = (self.nombre.get_text(), self.url.get_text())
        if nombre and url:
            self.emit('add-stream', self.tipo, nombre, url)
        self.cancelar()

    def set_accion(self, tipo):
        self.show()
        self.nombre.set_text("")
        self.url.set_text("")
        self.tipo = tipo

    def cancelar(self, widget=None):
        self.tipo = None
        self.nombre.set_text("")
        self.url.set_text("")
        self.hide()
