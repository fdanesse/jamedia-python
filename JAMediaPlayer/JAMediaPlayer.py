# -*- coding: utf-8 -*-

import os
import sys

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Widgets.Toolbars import Toolbar
from JAMediaPlayer.Widgets.Toolbars import ToolbarSalir
from JAMediaPlayer.Widgets.Toolbars import ToolbarAccion
from JAMediaPlayer.Widgets.mousespeeddetector import MouseSpeedDetector
from JAMediaPlayer.BasePanel import BasePanel

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import eliminar_streaming
from JAMediaPlayer.Globales import get_my_files_directory

#GObject.threads_init()
#commands.getoutput('PATH=%s:$PATH' % (os.path.dirname(__file__)))

from JAMediaPlayer.Globales import ICONS_PATH


class JAMediaPlayer(Gtk.EventBox):

    __gsignals__ = {
    "salir": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        #self.set_sensitive(False)
        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        self.set_border_width(2)

        #self.archivos = []
        self.mouse_in_visor = False
        self.cursor_root = Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR)
        icono = os.path.join(ICONS_PATH, "jamedia_cursor.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, -1, 24)
        self.jamedia_cursor = Gdk.Cursor(Gdk.Display.get_default(), pixbuf, 0, 0)

        self.toolbar = Toolbar()
        self.toolbar_salir = ToolbarSalir()
        self.toolbar_accion = ToolbarAccion()

        self.base_panel = BasePanel()

        vbox = Gtk.VBox()
        vbox.pack_start(self.toolbar, False, False, 0)
        vbox.pack_start(self.toolbar_salir, False, False, 0)
        vbox.pack_start(self.toolbar_accion, False, False, 0)
        vbox.pack_start(self.base_panel, True, True, 0)

        self.connect("realize", self.__realize)

        self.add(vbox)
        self.show_all()

        # Controlador del mouse. http://www.pyGtk.org/pyGtk2reference/class-gdkdisplay.html
        self.mouse_listener = MouseSpeedDetector(self)
        self.mouse_listener.new_handler(True)

        self.toolbar.connect("accion", self.__accion_toolbar)

        self.base_panel.connect("show-controls", self.__ocultar_controles)
        #self.base_panel.connect("menu_activo", self.__cancel_toolbars)
        self.base_panel.player.connect("video", self.__set_video)
        self.toolbar_salir.connect("salir", self.__salir)

        self.mouse_listener.connect("estado", self.__set_mouse)
        self.connect("hide", self.__hide_show)
        self.connect("show", self.__hide_show)

        GLib.idle_add(self.__setup_init)

    def __set_video(self, widget, valor):
        self.toolbar.configurar.set_sensitive(valor)

    def __realize(self, window):
        self.cursor_root = self.get_property("window").get_cursor()
        self.get_property("window").set_cursor(self.jamedia_cursor)

    def __setup_init(self):
        self.__cancel_toolbars()
        #self.toolbar.configurar.set_sensitive(False)
        self.base_panel.izquierda.setup_init()
        self.base_panel.derecha.setup_init()
        '''if self.archivos:
            self.base_panel.derecha.set_nueva_lista(self.archivos)
            self.archivos = []'''
        #self.set_sensitive(True)
        return False

    def __accion_toolbar(self, widget, accion):
        self.__cancel_toolbars()
        if accion == "salir":
            self.emit('salir')
        elif accion == "show-config":
            self.base_panel.derecha.show_config()
        else:
            print (self.__accion_toolbar, accion)

    def __hide_show(self, widget):
        """
        Controlador del mouse funcionará solo si JAMedia es Visible.
        """
        self.mouse_listener.new_handler(widget.get_visible())

    def __set_mouse(self, widget, estado):
        """
        Muestra u oculta el mouse de jamedia según su posición.
        """
        win = self.get_property("window")
        if self.mouse_in_visor:  # Solo cuando el mouse está sobre el Visor.
            if estado == "moviendose":
                if win.get_cursor() != self.jamedia_cursor:
                    win.set_cursor(self.jamedia_cursor)
                    return
            elif estado == "detenido":
                if win.get_cursor() != Gdk.CursorType.BLANK_CURSOR:
                    win.set_cursor(Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR))
                    return
            elif estado == "fuera":
                if win.get_cursor() != self.cursor_root:
                    win.set_cursor(self.cursor_root)
                    return
        else:
            if estado == "moviendose" or estado == "detenido":
                if win.get_cursor() != self.jamedia_cursor:
                    win.set_cursor(self.jamedia_cursor)
                    return
            elif estado == "fuera":
                if win.get_cursor() != self.cursor_root:
                    win.set_cursor(self.cursor_root)
                    return

    def __ocultar_controles(self, widget, datos):
        zona, ocultar = datos
        self.mouse_in_visor = zona
        if zona and ocultar:
            self.__cancel_toolbars()
            self.set_border_width(0)
            self.base_panel.set_border_width(0)
            self.toolbar.hide()
            self.base_panel.derecha.hide()
            self.base_panel.izquierda.toolbar_info.hide()
            self.base_panel.izquierda.progress.hide()
        elif not zona and ocultar:
            self.toolbar.show()
            self.set_border_width(2)
            self.base_panel.set_border_width(2)
            self.base_panel.derecha.show()
            self.base_panel.izquierda.toolbar_info.show()
            self.base_panel.izquierda.progress.show()
        elif not zona and not ocultar:
            pass
        elif zona and not ocultar:
            pass

    def __salir(self, widget=None, senial=None):
        Gtk.main_quit()
        sys.exit(0)

    def __cancel_toolbars(self, widget=False):
        self.toolbar_salir.cancelar()
        self.toolbar_accion.cancelar()

    #def set_archivos(self, archivos):
    #    self.archivos = archivos
