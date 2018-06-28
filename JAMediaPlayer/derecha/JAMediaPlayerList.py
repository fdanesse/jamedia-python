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

        self.toolbar.openfiles.connect("clicked", self.__openfiles)
        #self.toolbar.appendfiles.connect("clicked", self.__openfiles) #FIXME: append files
        #self.toolbar.clearlist.connect("clicked", self.lista.get_model().clear)
        #FIXME: self.lista.connect("button-press-event", self.__click_derecho_en_lista)

    def __openfiles(self, widget):
        selector = My_FileChooser(parent=self.get_toplevel(),
            filter_type=[], action=Gtk.FileChooserAction.OPEN,
            mime=self.mime, title="Abrir Archivos", path=self.directorio)
        selector.connect('load-files', self.__load_files)
        selector.run()
        if selector:
            selector.destroy()

    def __load_files(self, widget, archivos):
        items = []
        archivos.sort()
        for path in archivos:
            if not os.path.isfile(path):
                continue
            archivo = os.path.basename(path)
            items.append([archivo, path])
            self.directorio = os.path.dirname(path)
        self.__load_list(items, "load")

    def __load_list(self, items, tipo):
        if tipo == "load":
            self.lista.get_model().clear()
        self.lista.agregar_items(items)

    '''
    def __click_derecho_en_lista(self, widget, event):
        boton = event.button
        pos = (event.x, event.y)
        tiempo = event.time
        path, columna, xdefondo, ydefondo = (None, None, None, None)
        try:
            path, columna, xdefondo, ydefondo = widget.get_path_at_pos(
                int(pos[0]), int(pos[1]))
        except:
            return
        # TreeView.get_path_at_pos(event.x, event.y) devuelve:
        # * La ruta de acceso en el punto especificado (x, y),
        # en relación con las coordenadas widget
        # * El Gtk.TreeViewColumn en ese punto
        # * La coordenada X en relación con el fondo de la celda
        # * La coordenada Y en relación con el fondo de la celda
        if boton == 1 or boton == 2:
            return
        elif boton == 3:
            self.__emit_menu_activo()
            #menu = MenuList(widget, boton, pos, tiempo, path, widget.get_model())
            #menu.connect('accion', self.__emit_accion_list)
            #menu.popup(None, None, None, None, boton, tiempo)
    '''

    '''
    def select_valor(self, path_origen):
        self.lista.select_valor(path_origen)
    '''

    '''
    def get_selected_path(self):
        modelo, _iter = self.lista.get_selection().get_selected()
        valor = self.lista.get_model().get_value(_iter, 2)
        return valor
    '''

    '''
    def get_items_paths(self):
        filepaths = []
        model = self.lista.get_model()
        item = model.get_iter_first()
        self.lista.get_selection().select_iter(item)
        while item:
            filepaths.append(model.get_value(item, 2))
            item = model.iter_next(item)
        return filepaths
    '''


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

        self.show_all()

    def __changedSelection(self, treeSelection):
        modelo, _iter = self.get_selection().get_selected()
        valor = self.get_model().get_value(_iter, 2)
        if self.__valorSelected != valor:
            self.__valorSelected = valor
            self.emit('nueva-seleccion', self.__valorSelected)
            self.scroll_to_cell(self.get_model().get_path(_iter))

    def __setear_columnas(self):
        self.append_column(self.__construir_columna_icono('', 0, True))
        self.append_column(self.__construir_columa('Archivo', 1, True))
        self.append_column(self.__construir_columa('', 2, False))

    def __construir_columa(self, text, index, visible):
        render = Gtk.CellRendererText()
        # FIXME: render.set_property("background", get_colors("window"))
        # FIXME: render.set_property("foreground", get_colors("drawingplayer"))
        columna = Gtk.TreeViewColumn(text, render, text=index)
        columna.set_sort_column_id(index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __construir_columna_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        # FIXME: render.set_property("cell-background", get_colors("toolbars"))
        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        if not elementos:
            self.emit("len_items", self.get_model().iter_n_children())
            self.seleccionar_primero()
            return False

        texto, path = elementos[0]
        #FIXME: descripcion = describe_uri(path)
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

    def agregar_items(self, elementos):
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_siguiente(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        iternext = self.get_model().iter_next(_iter)
        if iternext:
            self.get_selection().select_iter(iternext)
        else:
            self.seleccionar_primero()
        return False

    def seleccionar_anterior(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        previous = self.get_model().iter_previous(_iter)
        if previous:
            self.get_selection().select_iter(previous)
        else:
            self.seleccionar_ultimo()
        return False

    def seleccionar_primero(self, widget=None):
        self.get_selection().select_iter(self.get_model().get_iter_first())

    def seleccionar_ultimo(self, widget=None):
        model = self.get_model()
        item = model.get_iter_first()
        _iter = None
        while item:
            _iter = item
            item = model.iter_next(item)
        if _iter:
            self.get_selection().select_iter(_iter)


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
