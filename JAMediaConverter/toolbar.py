# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        self.home = get_boton(os.path.join(ICONS_PATH, "home.svg"), flip=False, pixels=24, tooltip_text="JAMediaTube")
        self.insert(self.home, -1)
        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        self.show_all()
        