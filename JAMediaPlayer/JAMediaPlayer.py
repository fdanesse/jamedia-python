# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Widgets.Toolbars import Toolbar
from JAMediaPlayer.Widgets.mousespeeddetector import MouseSpeedDetector
from JAMediaPlayer.BasePanel import BasePanel
from JAMediaPlayer.FileChooser import FileChooser

from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import json_file

BASE_PATH = os.path.dirname(__file__)


class JAMediaPlayer(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.directorio = ''

        self.set_css_name('jamediabox')
        self.set_name('jamediabox')

        self.__mouse_in_visor = False
        self.__cursor_root = Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR)
        icono = os.path.join(ICONS_PATH, "jamedia_cursor.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, -1, 24)
        self.__jamedia_cursor = Gdk.Cursor(Gdk.Display.get_default(), pixbuf, 0, 0)

        self.toolbar = Toolbar()
        self.base_panel = BasePanel()
        self.__filechooser = FileChooser()

        self.pack_start(self.toolbar, False, False, 0)
        self.pack_start(self.base_panel, True, True, 0)
        self.pack_start(self.__filechooser, True, True, 0)

        self.connect("realize", self.__realize)
        self.show_all()

        # Controlador del mouse. http://www.pyGtk.org/pyGtk2reference/class-gdkdisplay.html
        self.mouse_listener = MouseSpeedDetector(self)
        self.mouse_listener.new_handler(True)

        self.toolbar.connect("show_config", self.__show_config)
        
        self.base_panel.izquierda.video_visor.connect("ocultar_controles", self.__show_controls)
        self.base_panel.izquierda.video_visor.connect("button_press_event", self.__set_fullscreen)
        self.base_panel.derecha.lista.toolbar.openfiles.connect("clicked", self.__openfiles, 'load')
        self.base_panel.derecha.lista.toolbar.appendfiles.connect("clicked", self.__openfiles, 'add')
        #self.base_panel.derecha.lista.toolbar.tv.connect("clicked", self.__openTv)
        self.base_panel.derecha.lista.toolbar.subtitulos.connect("clicked", self.__openfiles, 'suburi')

        self.__filechooser.open.connect("clicked", self.__load_files)
        self.__filechooser.connect("file-activated", self.__load_files)
        self.__filechooser.salir.connect("clicked", self.__return_to_player)

        self.mouse_listener.connect("estado", self.__set_mouse)
        self.connect("hide", self.__hide_show)
        self.connect("show", self.__hide_show)

        GLib.idle_add(self.__setup_init)

    def __load_files(self, widget):
        if self.__filechooser.tipo == 'suburi':
            self.base_panel.set_subtitulos(self.__filechooser.get_filename())
            self.__return_to_player(None)
        else:
            archivos = self.__filechooser.get_filenames()
            items = []
            archivos.sort()
            for path in archivos:
                if not os.path.isfile(path): continue
                archivo = os.path.basename(path)
                items.append([archivo, path])
                self.directorio = os.path.dirname(path)
            self.__return_to_player(None)
            if self.__filechooser.tipo == "load": self.base_panel.derecha.lista.lista.limpiar()
            self.base_panel.derecha.lista.lista.agregar_items(items)

    def setFiles(self, files):
        # Archivos abiertos desde nautilus
        items = []
        files.sort()
        for p in files:
            path = p.get_path()
            if not os.path.isfile(path): continue
            archivo = os.path.basename(path)
            items.append([archivo, path])
            self.directorio = os.path.dirname(path)
        self.__return_to_player(None)
        self.base_panel.derecha.lista.lista.limpiar()
        self.base_panel.derecha.lista.lista.agregar_items(items)

    def __return_to_player(self, widget):
        self.__filechooser.hide()
        self.toolbar.show()
        self.base_panel.show()

    def __openfiles(self, widget, tipo):
        self.toolbar.hide()
        self.base_panel.hide()
        self.__filechooser.run(self.directorio, tipo)

    def __set_fullscreen(self, widget, event):
        if event.type.value_name == "GDK_2BUTTON_PRESS":
            GLib.idle_add(self.toolbar.set_full, None)

    def __realize(self, window):
        self.__cursor_root = self.get_property("window").get_cursor()
        self.get_property("window").set_cursor(self.__jamedia_cursor)

    def __setup_init(self):
        self.base_panel.izquierda.setup_init()
        self.base_panel.derecha.setup_init()
        self.__filechooser.hide()
        return False

    def __show_config(self, widget, val):
        self.base_panel.derecha.show_config(val)

    def __hide_show(self, widget):
        self.mouse_listener.new_handler(widget.get_visible())

    def __set_mouse(self, widget, estado):
        # Muestra u oculta el mouse de jamedia según su posición.
        win = self.get_property("window")
        if self.__mouse_in_visor:  # Solo cuando el mouse está sobre el Visor.
            if estado == "moviendose":
                if win.get_cursor() != self.__jamedia_cursor:
                    win.set_cursor(self.__jamedia_cursor)
                    return
            elif estado == "detenido":
                if win.get_cursor() != Gdk.CursorType.BLANK_CURSOR:
                    win.set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
                    return
            elif estado == "fuera":
                if win.get_cursor() != self.__cursor_root:
                    win.set_cursor(self.__cursor_root)
                    return
        else:
            if estado == "moviendose" or estado == "detenido":
                if win.get_cursor() != self.__jamedia_cursor:
                    win.set_cursor(self.__jamedia_cursor)
                    return
            elif estado == "fuera":
                if win.get_cursor() != self.__cursor_root:
                    win.set_cursor(self.__cursor_root)
                    return

    def __show_controls(self, widget, valor):
        zona, ocultar = (valor, self.toolbar.ocultar_controles)
        self.__mouse_in_visor = zona
        if zona and ocultar:
            self.toolbar.hide()
            self.base_panel.derecha.hide()
            self.base_panel.izquierda.toolbar_info.hide()
            self.base_panel.izquierda.progress.hide()
        elif not zona and ocultar:
            self.toolbar.show()
            self.base_panel.derecha.show()
            self.base_panel.izquierda.toolbar_info.show()
            self.base_panel.izquierda.progress.show()
        elif not zona and not ocultar:
            pass
        elif zona and not ocultar:
            pass
