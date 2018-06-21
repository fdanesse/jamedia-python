#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors


class VideoVisor(Gtk.DrawingArea):

    __gsignals__ = {
    "ocultar_controles": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_BOOLEAN,))}

    def __init__(self):

        Gtk.DrawingArea.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))

        # FIXME:
        '''
        self.add_events(
            Gtk.gdk.KEY_PRESS_MASK |
            Gtk.gdk.KEY_RELEASE_MASK |
            Gtk.gdk.POINTER_MOTION_MASK |
            Gtk.gdk.POINTER_MOTION_HINT_MASK |
            Gtk.gdk.BUTTON_MOTION_MASK |
            Gtk.gdk.BUTTON_PRESS_MASK |
            Gtk.gdk.BUTTON_RELEASE_MASK
        )
        '''

        self.show_all()

    def do_motion_notify_event(self, event):
        """
        Cuando se mueve el mouse sobre el visor.
        """
        x, y = (int(event.x), int(event.y))
        rect = self.get_allocation()
        xx, yy, ww, hh = (rect.x, rect.y, rect.width, rect.height)

        if x in range(ww - 60, ww) or y in range(yy, yy + 60) \
            or y in range(hh - 60, hh):
            self.emit("ocultar_controles", False)
            return True
        else:
            self.emit("ocultar_controles", True)
            return True
            