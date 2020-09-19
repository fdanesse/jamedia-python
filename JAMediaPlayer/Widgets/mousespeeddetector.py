# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject


class MouseSpeedDetector(GObject.Object):

    __gsignals__ = {
        'estado': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self, parent):

        GObject.Object.__init__(self)

        self.actualizador = False
        self.mouse_pos = (0, 0)

    def __handler(self):
        try:
            display, posx, posy = Gdk.Display.get_default().get_window_at_pointer()
        except:
            return True
        if posx > 0 and posy > 0:
            if posx != self.mouse_pos[0] or posy != self.mouse_pos[1]:
                self.mouse_pos = (posx, posy)
                self.emit("estado", "moviendose")
            else:
                self.emit("estado", "detenido")
        else:
            self.emit("estado", "fuera")
        return True

    def new_handler(self, reset):
        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False
        if reset:
            self.actualizador = GLib.timeout_add(1000, self.__handler)
