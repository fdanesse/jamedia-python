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

from JAMediaPlayer.Globales import ICONS_PATH


class JAMediaPlayer(Gtk.VBox):

    __gsignals__ = {"salir": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.__mouse_in_visor = False
        self.__cursor_root = Gdk.Cursor(Gdk.CursorType.BLANK_CURSOR)
        icono = os.path.join(ICONS_PATH, "jamedia_cursor.svg")
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icono, -1, 24)
        self.__jamedia_cursor = Gdk.Cursor(Gdk.Display.get_default(), pixbuf, 0, 0)

        self.__toolbar = Toolbar()
        self.base_panel = BasePanel()

        self.pack_start(self.__toolbar, False, False, 0)
        self.pack_start(self.base_panel, True, True, 0)

        self.connect("realize", self.__realize)

        self.show_all()

        # Controlador del mouse. http://www.pyGtk.org/pyGtk2reference/class-gdkdisplay.html
        self.mouse_listener = MouseSpeedDetector(self)
        self.mouse_listener.new_handler(True)

        self.__toolbar.salir.connect("clicked", self.__emit_salir)
        self.__toolbar.connect("show_config", self.__show_config)
        
        #FIXME: self.base_panel.connect("menu_activo", self.__cancel_toolbars)
        self.base_panel.player.connect("video", self.__set_video)
        self.base_panel.izquierda.video_visor.connect("ocultar_controles", self.__show_controls)
        self.base_panel.izquierda.video_visor.connect("button_press_event", self.__set_fullscreen)

        self.mouse_listener.connect("estado", self.__set_mouse)
        self.connect("hide", self.__hide_show)
        self.connect("show", self.__hide_show)

        GLib.idle_add(self.__setup_init)

    def __set_fullscreen(self, widget, event):
        if event.type.value_name == "GDK_2BUTTON_PRESS":
            GLib.idle_add(self.__toolbar.set_full, None)

    def __set_video(self, widget, valor):
        self.__toolbar.configurar.set_active(False)
        self.__toolbar.configurar.set_sensitive(valor)

    def __realize(self, window):
        self.__cursor_root = self.get_property("window").get_cursor()
        self.get_property("window").set_cursor(self.__jamedia_cursor)

    def __setup_init(self):
        self.__toolbar.configurar.set_sensitive(False)
        self.base_panel.izquierda.setup_init()
        self.base_panel.derecha.setup_init()
        return False

    def __emit_salir(self, widget):
        self.emit('salir')

    def __show_config(self, widget, val):
        self.base_panel.derecha.show_config(val)

    def __hide_show(self, widget):
        self.mouse_listener.new_handler(widget.get_visible())

    def __set_mouse(self, widget, estado):
        """
        Muestra u oculta el mouse de jamedia según su posición.
        """
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
        zona, ocultar = (valor, self.__toolbar.ocultar_controles)
        self.__mouse_in_visor = zona
        if zona and ocultar:
            self.__toolbar.hide()
            self.base_panel.derecha.hide()
            self.base_panel.izquierda.toolbar_info.hide()
            self.base_panel.izquierda.progress.hide()
        elif not zona and ocultar:
            self.__toolbar.show()
            self.base_panel.derecha.show()
            self.base_panel.izquierda.toolbar_info.show()
            self.base_panel.izquierda.progress.show()
        elif not zona and not ocultar:
            pass
        elif zona and not ocultar:
            pass
