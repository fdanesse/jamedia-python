# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')

from gi.repository import Gst
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject


class VideoVisor(Gtk.EventBox):

    __gsignals__ = {"ocultar_controles": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_BOOLEAN,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.add_events(
            Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.KEY_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.POINTER_MOTION_HINT_MASK |
            Gdk.EventMask.BUTTON_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        self.gtkSink = Gst.ElementFactory.make("gtksink", None)  # glsinkbin
        
        self.add(self.gtkSink.props.widget)

        self.show_all()

    def do_motion_notify_event(self, event):
        # Cuando se mueve el mouse sobre el visor
        x, y = (int(event.x), int(event.y))
        rect = self.get_allocation()
        xx, yy, ww, hh = (rect.x, rect.y, rect.width, rect.height)
        if x in range(ww - 60, ww) or y in range(yy, yy + 60) or y in range(hh - 60, hh):
            self.emit("ocultar_controles", False)
        else:
            self.emit("ocultar_controles", True)
        return True
