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

        self.ocultar_controles = False

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.salir = get_boton(os.path.join(ICONS_PATH, "JAMedia.svg"), flip=False, pixels=35, tooltip_text="Cambiar JAMediaTube")
        self.insert(self.salir, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.show_all()
