# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import get_JAMedia_Directory
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar
from JAMediaPlayer.Globales import ICONS_PATH
# FIXME: Borrar las funciones que no se usan


class PlayerList(Gtk.Frame):

    __gsignals__ = {
    #"accion-list": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_STRING, GObject.TYPE_PYOBJECT))
    }

    def __init__(self):

        Gtk.Frame.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        self.directorio = get_JAMedia_Directory()
        self.mime = ['audio/*', 'video/*', 'application/ogg']

        vbox = Gtk.VBox()

        self.toolbar = JAMediaToolbarList()
        self.lista = Lista()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(scroll, True, True, 0)

        self.add(vbox)
        self.show_all()

        self.set_size_request(150, -1)

        self.toolbar.openfiles.connect("clicked", self.__openfiles, "load")
        self.toolbar.appendfiles.connect("clicked", self.__openfiles, "add")
        self.toolbar.clearlist.connect("clicked", self.__clearList)
        
    def __clearList(self, widget):
        self.lista.limpiar()

    def __openfiles(self, widget, tipo):
        selector = My_FileChooser(parent=self.get_toplevel(),
            filter_type=[], action=Gtk.FileChooserAction.OPEN,
            mime=self.mime, title="Abrir Archivos", path=self.directorio)
        selector.connect('load-files', self.__load_files, tipo)
        selector.run()
        if selector:
            selector.destroy()

    def __load_files(self, widget, archivos, tipo):
        items = []
        archivos.sort()
        for path in archivos:
            if not os.path.isfile(path):
                continue
            archivo = os.path.basename(path)
            items.append([archivo, path])
            self.directorio = os.path.dirname(path)
        self.__load_list(items, tipo)

    def __load_list(self, items, tipo):
        if tipo == "load":
            self.lista.limpiar()
        self.lista.agregar_items(items)


class Lista(Gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "len_items": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_INT, ))
    }

    def __init__(self):

        Gtk.TreeView.__init__(self, Gtk.ListStore(GdkPixbuf.Pixbuf, GObject.TYPE_STRING, GObject.TYPE_STRING))

        self.__valorSelected = None
        self.set_headers_clickable(True)
        self.set_headers_visible(True)
        self.set_reorderable(True)

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
            #NOTA: Al parecer nunca sucede pero no está de más
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
        #render.set_property("background", get_colors("window"))
        #render.set_property("foreground", get_colors("drawingplayer"))
        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __construir_columna_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        #render.set_property("cell-background", get_colors("toolbars"))
        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            if not self.__valorSelected:
                self.seleccionar_primero()
            self.emit("len_items", self.get_model().iter_n_children())
            return False

        texto, path = elementos[0]
        #descripcion = describe_uri(path)
        icono = os.path.join(ICONS_PATH, "sonido.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, 24, -1)
        '''
        if descripcion:
            if descripcion[2]:
                # Es un Archivo
                tipo = describe_archivo(path)
                if 'video' in tipo or 'application/ogg' in tipo:
                    icono = os.path.join(ICONS_PATH, "video.svg")
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                        icono, 24, -1)
        '''
        self.get_model().append([pixbuf, texto, path])
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def __getItems(self):
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
        elementos = [item for item in elementos if self.__filterItems(item, self.__getItems())]
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

    def limpiar(self, widget=None):
        self.get_selection().disconnect_by_func(self.__changedSelection)
        self.get_model().clear()
        self.get_selection().connect("changed", self.__changedSelection)


class JAMediaToolbarList(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        archivo = os.path.join(ICONS_PATH, "document-open.svg")
        self.openfiles = get_boton(archivo, flip=False, pixels=24)
        self.openfiles.set_tooltip_text("Cargar Archivos.")
        toolbar.insert(self.openfiles, -1)

        archivo = os.path.join(ICONS_PATH, "document-new.svg")
        self.appendfiles = get_boton(archivo, flip=False, pixels=24)
        self.appendfiles.set_tooltip_text("Agregar Archivos")
        toolbar.insert(self.appendfiles, -1)

        archivo = os.path.join(ICONS_PATH, "clear.svg")
        self.clearlist = get_boton(archivo, flip=False, pixels=24)
        self.clearlist.set_tooltip_text("Limpiar Lista")
        toolbar.insert(self.clearlist, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()


class My_FileChooser(Gtk.FileChooserDialog):

    __gsignals__ = {'load-files': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self, parent=None, action=None, filter_type=[], title=None, path=None, mime=[]):

        Gtk.FileChooserDialog.__init__(self, title=title, parent=parent, action=action)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        self.set_resizable(True)
        self.set_size_request(320, 240)

        self.set_current_folder_uri("file://%s" % path)
        self.set_select_multiple(True)

        hbox = Gtk.HBox()

        boton_abrir_directorio = Gtk.Button("Abrir")
        boton_seleccionar_todo = Gtk.Button("Seleccionar Todos")
        boton_salir = Gtk.Button("Salir")
        boton_salir.connect("clicked", self.__salir)

        boton_abrir_directorio.connect("clicked", self.__file_activated)
        boton_seleccionar_todo.connect("clicked", self.__select_all)

        hbox.pack_end(boton_salir, True, True, 5)
        hbox.pack_end(boton_seleccionar_todo, True, True, 5)
        hbox.pack_end(boton_abrir_directorio, True, True, 5)

        self.set_extra_widget(hbox)

        hbox.show_all()

        if filter_type:
            filtro = Gtk.FileFilter()
            filtro.set_name("Filtro")
            for fil in filter_type:
                filtro.add_pattern(fil)
            self.add_filter(filtro)
        elif mime:
            filtro = Gtk.FileFilter()
            filtro.set_name("Filtro")
            for mi in mime:
                filtro.add_mime_type(mi)
            self.add_filter(filtro)

        self.add_shortcut_folder_uri("file:///media/")
        self.connect("file-activated", self.__file_activated)
        self.connect("realize", self.__resize)

    def __resize(self, widget):
        self.resize(437, 328)

    def __file_activated(self, widget):
        self.emit('load-files', self.get_filenames())
        self.__salir(None)

    def __select_all(self, widget):
        self.select_all()

    def __salir(self, widget):
        self.destroy()
