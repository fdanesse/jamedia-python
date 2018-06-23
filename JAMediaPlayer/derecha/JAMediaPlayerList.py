#!/usr/bin/env python
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

from JAMediaPlayer.Globales import describe_uri
from JAMediaPlayer.Globales import describe_archivo
from JAMediaPlayer.Globales import describe_acceso_uri
from JAMediaPlayer.Globales import get_streamings
from JAMediaPlayer.Globales import stream_en_archivo

from JAMediaPlayer.Globales import get_JAMedia_Directory
from JAMediaPlayer.Globales import get_data_directory
from JAMediaPlayer.Globales import get_my_files_directory
from JAMediaPlayer.Globales import get_tube_directory
from JAMediaPlayer.Globales import get_audio_directory
from JAMediaPlayer.Globales import get_video_directory
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar
from JAMediaPlayer.Globales import ICONS_PATH


class PlayerList(Gtk.Frame):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "accion-list": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,
        GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
    "menu_activo": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, []),
    #"add_stream": (GObject.SIGNAL_RUN_LAST,
    #    GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "len_items": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_INT, ))}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        self.directorio = get_JAMedia_Directory()
        self.mime = ['audio/*', 'video/*']

        vbox = Gtk.VBox()

        self.toolbar = JAMediaToolbarList()
        self.lista = Lista()

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(
            Gtk.PolicyType.AUTOMATIC,
            Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.lista)

        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(scroll, True, True, 0)

        self.add(vbox)
        self.show_all()

        self.set_size_request(150, -1)

        self.toolbar.connect("cargar_lista",
            self.cargar_lista)
        #self.toolbar.connect("add_stream", self.__emit_add_stream)
        self.toolbar.connect("menu_activo",
            self.__emit_menu_activo)

        self.lista.connect("nueva-seleccion",
            self.__emit_nueva_seleccion)
        self.lista.connect("button-press-event",
            self.__click_derecho_en_lista)
        self.lista.connect("len_items",
            self.__re_emit_len_items)

    def __re_emit_len_items(self, widget, items):
        self.emit("len_items", items)

    '''
    def __emit_add_stream(self, widget):
        # El usuario agregará una dirección de streaming
        self.emit("add_stream", self.toolbar.label.get_text())
    '''

    def __emit_menu_activo(self, widget=False):
        # hay un menu contextual presente
        self.emit("menu_activo")

    def __emit_accion_list(self, widget, lista, accion, _iter):
        # borrar, copiar, mover, grabar, etc . . .
        self.emit("accion-list", lista, accion, _iter)

    def __emit_nueva_seleccion(self, widget, pista):
        # item seleccionado en la lista
        self.emit('nueva-seleccion', pista)

    def __seleccionar_lista_de_stream(self, archivo, titulo):
        items = get_streamings(archivo)
        self.__load_list(items, "load", titulo)

    def __seleccionar_lista_de_archivos(self, directorio, titulo):
        archivos = sorted(os.listdir(directorio))
        lista = []
        for path in archivos:
            archivo = os.path.join(directorio, path)
            if os.path.isfile(archivo):
                lista.append(archivo)
        self.__load_files(False, lista, titulo)

    def __load_files(self, widget, archivos, titulo=False):
        items = []
        archivos.sort()
        for path in archivos:
            if not os.path.isfile(path):
                continue
            archivo = os.path.basename(path)
            items.append([archivo, path])
            self.directorio = os.path.dirname(path)
        self.__load_list(items, "load", titulo)
        # FIXME: Mostrar clear y add para agregar archivos a la lista

    def __load_list(self, items, tipo, titulo=False):
        if tipo == "load":
            self.lista.limpiar()
            self.emit("accion-list", False, "limpiar", False)
        if items:
            self.lista.agregar_items(items)
        else:
            self.emit('nueva-seleccion', False)
        if titulo != False:
            self.toolbar.label.set_text(titulo)

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
            menu = MenuList(
                widget, boton, pos, tiempo, path, widget.get_model())
            menu.connect('accion', self.__emit_accion_list)
            menu.popup(None, None, None, None, boton, tiempo)

    def seleccionar_primero(self):
        self.lista.seleccionar_primero()

    def seleccionar_ultimo(self):
        self.lista.seleccionar_ultimo()

    def seleccionar_anterior(self):
        self.lista.seleccionar_anterior()

    def seleccionar_siguiente(self):
        self.lista.seleccionar_siguiente()

    def select_valor(self, path_origen):
        self.lista.select_valor(path_origen)

    def limpiar(self):
        self.lista.limpiar()

    def set_mime_types(self, mime):
        self.mime = mime

    def get_selected_path(self):
        modelo, _iter = self.lista.get_selection().get_selected()
        valor = self.lista.get_model().get_value(_iter, 2)
        return valor

    def get_items_paths(self):
        filepaths = []
        model = self.lista.get_model()
        item = model.get_iter_first()
        self.lista.get_selection().select_iter(item)
        while item:
            filepaths.append(model.get_value(item, 2))
            item = model.iter_next(item)
        return filepaths

    def setup_init(self):
        ocultar(self.toolbar.boton_agregar)

    def cargar_lista(self, widget, indice):
        data = get_data_directory()
        _dict = {
            0: os.path.join(data, 'JAMediaRadio.JAMedia'),
            2: os.path.join(data, 'MisRadios.JAMedia'),
            5: get_my_files_directory(),
            6: get_tube_directory(),
            7: get_audio_directory(),
            8: get_video_directory(),
            }
        ocultar(self.toolbar.boton_agregar)
        if indice == 0:
            self.__seleccionar_lista_de_stream(_dict[0], "JAM-Radio")
        elif indice == 2:
            self.__seleccionar_lista_de_stream(_dict[2], "Radios")
            mostrar(self.toolbar.boton_agregar)
        elif indice == 5:
            self.__seleccionar_lista_de_archivos(_dict[indice], "Archivos")
        elif indice == 6:
            self.__seleccionar_lista_de_archivos(_dict[indice], "JAM-Tube")
        elif indice == 7:
            self.__seleccionar_lista_de_archivos(_dict[indice], "JAM-Audio")
        elif indice == 8:
            self.__seleccionar_lista_de_archivos(_dict[indice], "JAM-Video")
        elif indice == 9:
            selector = My_FileChooser(parent=self.get_toplevel(),
                filter_type=[], action=Gtk.FileChooserAction.OPEN,
                mime=self.mime, title="Abrir Archivos", path=self.directorio)
            selector.connect('load-files', self.__load_files, "Archivos")
            selector.run()
            if selector:
                selector.destroy()

    '''
    def set_ip(self, valor):
        self.toolbar.ip = valor
    '''

    def set_nueva_lista(self, archivos):
        self.__load_files(False, archivos, titulo="Archivos")


class Lista(Gtk.TreeView):

    __gsignals__ = {
    "nueva-seleccion": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, )),
    "len_items": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_INT, ))}

    def __init__(self):

        Gtk.TreeView.__init__(self,
            Gtk.ListStore(GdkPixbuf.Pixbuf,
            GObject.TYPE_STRING, GObject.TYPE_STRING))

        #self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        self.set_property("rules-hint", True)
        self.set_headers_clickable(True)
        self.set_headers_visible(True)

        self.len_items = 0
        self.permitir_select = True
        self.valor_select = False

        self.__setear_columnas()

        self.get_selection().set_select_function(
            self.__selecciones, self.get_model())

        self.show_all()

    def __selecciones(self, treeselection,
        model, path, is_selected, listore):
        if not self.permitir_select:
            return True
        self.permitir_select = False
        _iter = self.get_model().get_iter(path)
        valor = self.get_model().get_value(_iter, 2)
        if self.valor_select != valor:
            GLib.timeout_add(3, self.__select, _iter, valor)
        return True

    def __select(self, _iter, valor):
        self.valor_select = valor
        self.emit('nueva-seleccion', self.valor_select)
        self.scroll_to_cell(self.get_model().get_path(_iter))
        self.permitir_select = True
        return False

    def __setear_columnas(self):
        self.append_column(self.__construir_columa_icono('', 0, True))
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

    def __construir_columa_icono(self, text, index, visible):
        render = Gtk.CellRendererPixbuf()
        # FIXME: render.set_property("cell-background", get_colors("toolbars"))
        columna = Gtk.TreeViewColumn(text, render, pixbuf=index)
        columna.set_property('visible', visible)
        columna.set_property('resizable', False)
        columna.set_sizing(Gtk.TreeViewColumnSizing.AUTOSIZE)
        return columna

    def __ejecutar_agregar_elemento(self, elementos):
        self.permitir_select = False
        self.set_sensitive(False)
        if not elementos:
            self.permitir_select = True
            self.seleccionar_primero()
            self.set_sensitive(True)
            return False

        texto, path = elementos[0]
        descripcion = describe_uri(path)
        icono = os.path.join(ICONS_PATH, "sonido.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, 24, -1)

        if descripcion:
            if descripcion[2]:
                # Es un Archivo
                tipo = describe_archivo(path)
                if 'video' in tipo or 'application/ogg' in tipo:
                    icono = os.path.join(ICONS_PATH, "video.svg")
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                        icono, 24, -1)

        self.get_model().append([pixbuf, texto, path])
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)
        return False

    def limpiar(self):
        self.permitir_select = False
        self.get_model().clear()
        self.valor_select = False
        self.ultimo_select = False
        self.permitir_select = True
        self.len_items = 0
        self.emit("len_items", 0)

    def agregar_items(self, elementos):
        self.len_items = len(elementos)
        self.emit("len_items", self.len_items)
        GLib.idle_add(self.__ejecutar_agregar_elemento, elementos)

    def seleccionar_siguiente(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        try:
            self.get_selection().select_iter(
                self.get_model().iter_next(_iter))
        except:
            if self.len_items == 1:
                self.emit('nueva-seleccion', self.valor_select)
            else:
                self.seleccionar_primero()
        return False

    def seleccionar_anterior(self, widget=None):
        modelo, _iter = self.get_selection().get_selected()
        path = self.get_model().get_path(_iter)
        path = (path[0] - 1, )
        if path[0] > -1:
            self.get_selection().select_iter(
                self.get_model().get_iter(path))
        else:
            self.seleccionar_ultimo()
        return False

    def seleccionar_primero(self, widget=None):
        self.get_selection().select_path(0)

    def seleccionar_ultimo(self, widget=None):
        model = self.get_model()
        item = model.get_iter_first()
        _iter = None
        while item:
            _iter = item
            item = model.iter_next(item)
        if _iter:
            self.get_selection().select_iter(_iter)

    def select_valor(self, path_origen):
        model = self.get_model()
        _iter = model.get_iter_first()
        valor = model.get_value(_iter, 2)
        while valor != path_origen:
            _iter = model.iter_next(_iter)
            valor = model.get_value(_iter, 2)
        if _iter:
            self.get_selection().select_iter(_iter)


class My_FileChooser(Gtk.FileChooserDialog):

    __gsignals__ = {
    'load-files': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, ))}

    def __init__(self, parent=None, action=None,
        filter_type=[], title=None, path=None, mime=[]):

        Gtk.FileChooserDialog.__init__(self,
            title=title, parent=parent,
            action=action)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window"))
        self.set_resizable(True)
        self.set_size_request(320, 240)

        self.set_current_folder_uri("file://%s" % path)
        self.set_select_multiple(True)

        hbox = Gtk.HBox()

        boton_abrir_directorio = Gtk.Button("Abrir")
        boton_seleccionar_todo = Gtk.Button("Seleccionar Todos")
        boton_salir = Gtk.Button("Salir")
        boton_salir.connect("clicked", self.__salir)

        boton_abrir_directorio.connect("clicked",
            self.__file_activated)
        boton_seleccionar_todo.connect("clicked",
            self.__select_all)

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


class MenuList(Gtk.Menu):

    __gsignals__ = {
    'accion': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,
        GObject.TYPE_STRING, GObject.TYPE_PYOBJECT))}

    def __init__(self, widget, boton, pos, tiempo, path, modelo):

        Gtk.Menu.__init__(self)

        _iter = modelo.get_iter(path)
        uri = modelo.get_value(_iter, 2)

        quitar = Gtk.MenuItem("Quitar de la Lista")
        self.append(quitar)
        quitar.connect_object("activate", self.__emit_accion,
            widget, path, "Quitar")

        my_files_directory = get_my_files_directory()

        if describe_acceso_uri(uri):
            lectura, escritura, ejecucion = describe_acceso_uri(uri)
            if lectura and os.path.dirname(uri) != my_files_directory:
                copiar = Gtk.MenuItem("Copiar a JAMedia")
                self.append(copiar)
                copiar.connect_object("activate", self.__emit_accion,
                    widget, path, "Copiar")
            if escritura and os.path.dirname(uri) != my_files_directory:
                mover = Gtk.MenuItem("Mover a JAMedia")
                self.append(mover)
                mover.connect_object("activate", self.__emit_accion,
                    widget, path, "Mover")
            if escritura:
                borrar = Gtk.MenuItem("Borrar el Archivo")
                self.append(borrar)
                borrar.connect_object("activate", self.__emit_accion,
                    widget, path, "Borrar")
        else:
            borrar = Gtk.MenuItem("Borrar Streaming")
            self.append(borrar)
            borrar.connect_object("activate", self.__emit_accion,
                widget, path, "Borrar")
            listas = [
                os.path.join(get_data_directory(), "JAMediaRadio.JAMedia"),
                os.path.join(get_data_directory(), "MisRadios.JAMedia"),
                ]
            jr = stream_en_archivo(uri, listas[0])
            r = stream_en_archivo(uri, listas[1])

            if (jr and not r):
                copiar = Gtk.MenuItem("Copiar a JAMedia")
                self.append(copiar)
                copiar.connect_object("activate", self.__emit_accion,
                    widget, path, "Copiar")
                mover = Gtk.MenuItem("Mover a JAMedia")
                self.append(mover)
                mover.connect_object("activate", self.__emit_accion,
                    widget, path, "Mover")

            grabar = Gtk.MenuItem("Grabar")
            self.append(grabar)
            grabar.connect_object("activate", self.__emit_accion,
                widget, path, "Grabar")

        self.show_all()
        self.attach_to_widget(widget, self.__null)

    def __null(self):
        pass

    def __emit_accion(self, widget, path, accion):
        _iter = widget.get_model().get_iter(path)
        self.emit('accion', widget, accion, _iter)


class JAMediaToolbarList(Gtk.EventBox):

    __gsignals__ = {
    "cargar_lista": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_INT,)),
    "add_stream": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, []),
    "menu_activo": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.ip = False

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("toolbars"))
        toolbar.modify_bg(Gtk.StateType.NORMAL,
            get_colors("toolbars"))

        archivo = os.path.join(ICONS_PATH, "lista.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Selecciona una Lista")
        boton.connect("clicked", self.__get_menu)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(
            draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer"))
        self.label.show()
        item.add(self.label)
        toolbar.insert(item, -1)

        toolbar.insert(get_separador(
            draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "agregar.svg")
        self.boton_agregar = get_boton(
            archivo, flip=False, pixels=24)
        self.boton_agregar.set_tooltip_text("Agregar Streaming")
        self.boton_agregar.connect(
            "clicked", self.__emit_add_stream)
        toolbar.insert(self.boton_agregar, -1)

        self.add(toolbar)
        self.show_all()

    def __get_menu(self, widget):
        self.emit("menu_activo")
        menu = Gtk.Menu()

        if self.ip:
            item = Gtk.MenuItem("JAMedia Radio")
            menu.append(item)
            item.connect_object("activate",
                self.__emit_load_list, 0)

            item = Gtk.MenuItem("Mis Emisoras")
            menu.append(item)
            item.connect_object("activate",
                self.__emit_load_list, 2)

        item = Gtk.MenuItem("Mis Archivos")
        menu.append(item)
        item.connect_object("activate",
            self.__emit_load_list, 5)

        item = Gtk.MenuItem("JAMediaTube")
        menu.append(item)
        item.connect_object("activate",
            self.__emit_load_list, 6)

        item = Gtk.MenuItem("Audio-JAMediaVideo")
        menu.append(item)
        item.connect_object("activate",
            self.__emit_load_list, 7)

        item = Gtk.MenuItem("Video-JAMediaVideo")
        menu.append(item)
        item.connect_object("activate",
            self.__emit_load_list, 8)

        item = Gtk.MenuItem("Archivos Externos")
        menu.append(item)
        item.connect_object("activate",
            self.__emit_load_list, 9)

        menu.show_all()
        menu.attach_to_widget(widget, self.__null)
        menu.popup(None, None, None, None, 1, 0)

    def __null(self):
        pass

    def __emit_load_list(self, indice):
        self.emit("cargar_lista", indice)

    def __emit_add_stream(self, widget):
        self.emit("add_stream")