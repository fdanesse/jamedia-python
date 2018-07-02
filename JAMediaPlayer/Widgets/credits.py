# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ICONS_PATH


class Credits(Gtk.Dialog):

    def __init__(self, parent=None):

        Gtk.Dialog.__init__(self, parent=parent, buttons=("Cerrar", Gtk.ResponseType.ACCEPT))

        self.set_decorated(False)
        self.modify_bg(Gtk.StateType.NORMAL, get_colors("widgetvideoitem"))
        self.set_border_width(15)

        imagen = Gtk.Image()
        imagen.set_from_file(os.path.join(ICONS_PATH, "JAMediaCredits.svg"))

        self.vbox.pack_start(imagen, True, True, 0)
        self.vbox.show_all()
