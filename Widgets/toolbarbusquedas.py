# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import ICONS_PATH


class ToolbarBusquedas(Gtk.Toolbar):

    __gsignals__ = {
    "comenzar_busqueda": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_INT))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarbusquedas')
        self.set_name('toolbarbusquedas')

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        label = Gtk.Label("Buscar")
        label.show()
        item.add(label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.entrycantidad = Gtk.Entry()
        self.entrycantidad.get_style_context().add_class("entradasdetexto")
        self.entrycantidad.props.placeholder_text = "50"
        self.entrycantidad.set_width_chars(3)
        self.entrycantidad.set_max_length(3)
        self.entrycantidad.set_tooltip_text("Escribe la cantidad de videos que deseas")
        self.entrycantidad.show()
        self.entrycantidad.connect('changed', self.__check_data)
        self.entrycantidad.connect('activate', self.__emit_buscar)
        item.add(self.entrycantidad)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        label = Gtk.Label("Videos Sobre")
        label.show()
        item.add(label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.entrytext = Gtk.Entry()
        self.entrytext.get_style_context().add_class("entradasdetexto")
        self.entrytext.props.placeholder_text = "Artista, Título o ambos."
        self.entrytext.set_width_chars(20)
        self.entrytext.set_max_length(50)
        self.entrytext.set_tooltip_text("Escribe lo que Buscas")
        self.entrytext.show()
        self.entrytext.connect('changed', self.__check_data)
        self.entrytext.connect('activate', self.__emit_buscar)
        item.add(self.entrytext)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.__run =  Gtk.ToolButton()
        self.__run.set_sensitive(False)
        self.__run.set_label("Run")
        self.__run.set_tooltip_text("Comenzar Búsqueda")
        self.__run.connect("clicked", self.__emit_buscar)
        self.insert(self.__run, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        lista = [self.entrycantidad, self.entrytext, self.__run]
        self.set_focus_chain(lista)
        self.show_all()

    def __emit_buscar(self, widget=None):
        texto = self.entrytext.get_text().strip()
        cantidad = self.entrycantidad.get_text()
        try:
            cantidad = int(cantidad)
        except:
            cantidad = 0
        self.entrytext.set_text("")
        self.entrycantidad.set_text("")
        if texto and cantidad:
            self.emit("comenzar_busqueda", texto, cantidad)

    def __check_data(self, widget):
        cantidad = self.entrycantidad.get_text()
        texto = self.entrytext.get_text()
        try:
            cantidad = int(cantidad)
        except:
            cantidad = 0
            self.entrycantidad.set_text("")
            self.entrycantidad.set_text("")
        self.__run.set_sensitive(cantidad and texto)
