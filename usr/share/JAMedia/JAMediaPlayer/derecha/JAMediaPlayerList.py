# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class PlayerList(Gtk.Frame):

    def __init__(self):

        Gtk.Frame.__init__(self)

        self.get_style_context().add_class('frameplayerlist')

        vbox = Gtk.VBox()

        self.toolbar = JAMediaToolbarList()
        self.lista = Lista()

        scroll = Gtk.ScrolledWindow()
        scroll.get_style_context().add_class('scrolllist')
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(scroll, True, True, 0)

        self.add(vbox)
        self.show_all()

        self.set_size_request(250, -1)

        self.toolbar.clearlist.connect("clicked", self.lista.limpiar)
        self.lista.connect("len_items", self.__len_items)

    def __len_items(self, widget, val):
        self.toolbar.clearlist.set_sensitive(bool(val))


class Lista(Gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "len_items": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_INT, ))
    }

    def __init__(self):

        Gtk.TreeView.__init__(self, Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING, GObject.TYPE_STRING))

        self.get_style_context().add_class('treeviewlist')

        self.__valorSelected = None
        self.set_headers_visible(False)

        self.__setear_columnas()
        self.get_selection().connect("changed", self.__changedSelection)
        self.get_model().connect("row-deleted", self.__rowDeleted)
        self.show_all()
    
    def __rowDeleted(self, widget, _row):
        if self.get_model().iter_n_children() == 0:
            self.__valorSelected = None
            self.emit("len_items", 0)

    def __changedSelection(self, treeSelection):
        modelo, _iter = treeSelection.get_selected()
        if not _iter:
            # NOTA: Al parecer nunca sucede pero no está de más
            self.__valorSelected = None
            self.emit("len_items", 0)
            return
        valor = modelo.get_value(_iter, 2)
        if self.__valorSelected != valor:
            self.__valorSelected = valor
            self.emit('nueva-seleccion', self.__valorSelected)
            self.scroll_to_cell(modelo.get_path(_iter))

    def __setear_columnas(self):
        self.append_column(self.__construir_columna_icono('', 0, True))
        self.append_column(self.__construir_columa('Archivo', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):
        render = Gtk.CellRendererText()
        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __construir_columna_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            if not self.__valorSelected:self.seleccionar_primero()
            self.emit("len_items", self.get_model().iter_n_children())
            return False

        texto, path = elementos[0]
        icono = os.path.join(ICONS_PATH, "sonido.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, 24, -1)
        self.get_model().append([pixbuf, texto.strip(), path.strip()])
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def getItems(self):
        modelo = self.get_model()
        item = modelo.get_iter_first()
        items = []
        _iter = None
        while item:
            _iter = item
            items.append([modelo.get_value(_iter, 1), modelo.get_value(_iter, 2)])
            item = modelo.iter_next(item)
        return items

    def __filterItems(self, item, items):
        return not item in items

    def agregar_items(self, elementos):
        elementos = [item for item in elementos if self.__filterItems(item, self.getItems())]
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_siguiente(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        if _iter:
            iternext = modelo.iter_next(_iter)
            if iternext:
                self.get_selection().select_iter(iternext)
            else:
                self.seleccionar_primero()
        return False

    def seleccionar_anterior(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        if _iter:
            previous = modelo.iter_previous(_iter)
            if previous:
                self.get_selection().select_iter(previous)
            else:
                self.seleccionar_ultimo()
        return False

    def seleccionar_primero(self, widget=None):
        _iter = self.get_model().get_iter_first()
        if _iter: self.get_selection().select_iter(_iter)

    def seleccionar_ultimo(self, widget=None):
        model = self.get_model()
        item = model.get_iter_first()
        _iter = None
        while item:
            _iter = item
            item = model.iter_next(item)
        if _iter:
            self.get_selection().select_iter(_iter)

    def seleccionar_pista(self, pista):
        model = self.get_model()
        item = model.get_iter_first()
        while item:
            if model.get_value(item, 2) == pista:
                self.get_selection().select_iter(item)
                break
            item = model.iter_next(item)

    def limpiar(self, widget=None):
        self.get_selection().disconnect_by_func(self.__changedSelection)
        self.get_model().clear()
        self.get_selection().connect("changed", self.__changedSelection)


class JAMediaToolbarList(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.get_style_context().add_class('toolbarlist')
        self.openfiles = get_boton(os.path.join(ICONS_PATH, "document-open.svg"), flip=False, pixels=18, tooltip_text="Cargar Archivos")
        self.insert(self.openfiles, -1)
        self.appendfiles = get_boton(os.path.join(ICONS_PATH, "document-new.svg"), flip=False, pixels=18, tooltip_text="Agregar Archivos")
        self.insert(self.appendfiles, -1)
        self.clearlist = get_boton(os.path.join(ICONS_PATH, "clear.svg"), flip=False, pixels=18, tooltip_text="Limpiar Lista")
        self.insert(self.clearlist, -1)
        self.subtitulos = get_boton(os.path.join(ICONS_PATH, "subtitulo.png"), flip=False, pixels=18, tooltip_text="Cargar Subtítulos")
        self.insert(self.subtitulos, -1)
        #self.tv = get_boton(os.path.join(ICONS_PATH, "tvicon.png"), flip=False, pixels=18, tooltip_text="Cargar Lista de Tv")
        #self.insert(self.tv, -1)
        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)
        self.show_all()
        self.clearlist.set_sensitive(False)
        self.subtitulos.set_sensitive(False)
