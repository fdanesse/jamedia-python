#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

#from toolbargrabar import ToolbarGrabar
from videovisor import VideoVisor
#from bufferinfo import BufferInfo
from toolbarinfo import ToolbarInfo
from JAMediaPlayer.Widgets.ProgressPlayer import ProgressPlayer

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar


class Izquierda(Gtk.EventBox):

    __gsignals__ = {
    "show-controls": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    'rotar': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    #'actualizar_streamings': (GObject.SIGNAL_RUN_LAST,
    #    GObject.TYPE_NONE, []),
    #'stop-record': (GObject.SIGNAL_RUN_LAST,
    #    GObject.TYPE_NONE, []),
    "seek": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT, )),
    "volumen": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))

        vbox = Gtk.VBox()

        #self.toolbar_record = ToolbarGrabar()
        self.video_visor = VideoVisor()
        #self.buffer_info = BufferInfo()
        self.toolbar_info = ToolbarInfo()
        self.progress = ProgressPlayer()

        #vbox.pack_start(self.toolbar_record, False, False, 0)
        vbox.pack_start(self.video_visor, True, True, 0)
        #vbox.pack_start(self.buffer_info, False, False, 0)
        vbox.pack_start(self.toolbar_info, False, False, 0)
        vbox.pack_start(self.progress, False, False, 0)

        self.add(vbox)
        self.show_all()

        #self.toolbar_record.connect("stop", self.__emit_stop_record)

        self.video_visor.connect("ocultar_controles", self.__emit_show_controls)
        self.video_visor.connect("button_press_event", self.__set_fullscreen)

        self.toolbar_info.connect("rotar", self.__emit_rotar)
        #self.toolbar_info.connect("actualizar_streamings", self.__emit_actualizar_streamings)

        self.progress.connect("seek", self.__emit_seek)
        self.progress.connect("volumen", self.__emit_volumen)

    def __emit_volumen(self, widget, valor):
        self.emit('volumen', valor)

    def __emit_seek(self, widget, valor):
        self.emit("seek", valor)

    #def __emit_stop_record(self, widget):
    #    self.emit("stop-record")

    #def __emit_actualizar_streamings(self, widget):
    #    self.emit('actualizar_streamings')

    def __emit_rotar(self, widget, sentido):
        self.emit('rotar', sentido)

    def __set_fullscreen(self, widget, event):
        if event.type.value_name == "GDK_2BUTTON_PRESS":
            win = self.get_toplevel()
            widget.set_sensitive(False)
            screen = win.get_screen()
            w, h = win.get_size()
            ww, hh = (screen.get_width(), screen.get_height())
            if ww == w and hh == h:
                win.set_border_width(2)
                GLib.idle_add(self.__set_full, win, False)
            else:
                win.set_border_width(0)
                GLib.idle_add(self.__set_full, win, True)
            widget.set_sensitive(True)

    def __set_full(self, win, valor):
        if valor:
            win.fullscreen()
        else:
            win.unfullscreen()

    def __emit_show_controls(self, widget, valor):
        zona, ocultar = (valor, self.toolbar_info.ocultar_controles)
        self.emit("show-controls", (zona, ocultar))

    def setup_init(self):
        #map(ocultar, [self.toolbar_record, self.buffer_info])
        self.toolbar_info.set_video(False)
        self.progress.set_sensitive(False)

    #def set_ip(self, valor):
    #    self.toolbar_info.set_ip(valor)