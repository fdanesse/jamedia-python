# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar


class ToolbarInfo(Gtk.Toolbar):

    __gsignals__ = {'rotar': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING,))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.boton_izquierda = get_boton(os.path.join(ICONS_PATH, "rotar.svg"), flip=False, pixels=24, tooltip_text="Izquierda")
        self.boton_izquierda.connect("clicked", self.__emit_rotar)
        self.insert(self.boton_izquierda, -1)

        self.boton_derecha = get_boton(os.path.join(ICONS_PATH, "rotar.svg"), flip=True, pixels=24, tooltip_text="Derecha")
        self.boton_derecha.connect("clicked", self.__emit_rotar)
        self.insert(self.boton_derecha, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)
        
        self.show_all()
    
    def __emit_rotar(self, widget):
        if widget == self.boton_derecha:
            self.emit('rotar', "Derecha")
        elif widget == self.boton_izquierda:
            self.emit('rotar', "Izquierda")

    def set_video(self, valor):
        if valor:
            sensibilizar([self.boton_izquierda, self.boton_derecha])
        else:
            insensibilizar([self.boton_izquierda, self.boton_derecha])
