# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.izquierda.videovisor import VideoVisor
# FIXME:from bufferinfo import BufferInfo
from JAMediaPlayer.izquierda.toolbarinfo import ToolbarInfo
from JAMediaPlayer.Widgets.ProgressPlayer import ProgressPlayer

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ocultar


class Izquierda(Gtk.EventBox):

    __gsignals__ = {
    "show-controls": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    'rotar': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "seek": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, )),
    "volumen": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))

        vbox = Gtk.VBox()

        self.video_visor = VideoVisor()
        #self.buffer_info = BufferInfo()
        self.toolbar_info = ToolbarInfo()
        self.progress = ProgressPlayer()

        vbox.pack_start(self.video_visor, True, True, 0)
        #vbox.pack_start(self.buffer_info, False, False, 0)
        vbox.pack_start(self.toolbar_info, False, False, 0)
        vbox.pack_start(self.progress, False, False, 0)

        self.add(vbox)
        self.show_all()

        self.video_visor.connect("ocultar_controles", self.__emit_show_controls)
        self.video_visor.connect("button_press_event", self.__set_fullscreen)
        self.toolbar_info.connect("rotar", self.__emit_rotar)
        self.progress.connect("seek", self.__emit_seek)
        self.progress.connect("volumen", self.__emit_volumen)

    def __emit_volumen(self, widget, valor):
        self.emit('volumen', valor)

    def __emit_seek(self, widget, valor):
        self.emit("seek", valor)

    def __emit_rotar(self, widget, sentido):
        self.emit('rotar', sentido)

    def __set_fullscreen(self, widget, event):
        if event.type.value_name == "GDK_2BUTTON_PRESS":
            GLib.idle_add(self.toolbar_info.set_full, None)

    def __emit_show_controls(self, widget, valor):
        zona, ocultar = (valor, self.toolbar_info.ocultar_controles)
        self.emit("show-controls", (zona, ocultar))

    def setup_init(self):
        self.toolbar_info.set_video(False)
        self.progress.set_sensitive(False)
