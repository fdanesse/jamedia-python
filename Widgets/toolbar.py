# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar(Gtk.Toolbar):

    __gsignals__ = {
    'salir': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'switch': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.__jamedia = get_boton(os.path.join(ICONS_PATH, "jamedia.png"), flip=False, pixels=35, tooltip_text="JAMedia")
        self.__jamedia.connect("clicked", self.__emit_switch, 'jamedia')
        self.insert(self.__jamedia, -1)

        # self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.radio = get_boton(os.path.join(ICONS_PATH, "Music-Radio-1-icon.png"), flip=False, pixels=24, tooltip_text="JAMediaRadio")
        self.radio.connect("clicked", self.__emit_switch, 'jamediaradio')
        self.insert(self.radio, -1)

        #self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.converter = get_boton(os.path.join(ICONS_PATH, "convert.svg"), flip=False, pixels=24, tooltip_text="JAMediaConverter")
        self.converter.connect("clicked", self.__emit_switch, 'jamediaconverter')
        self.insert(self.converter, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.__help = get_boton(os.path.join(ICONS_PATH, "help.svg"), flip=False, pixels=24, tooltip_text="Ayuda")
        self.__help.connect("clicked", self.__emit_switch, 'creditos')
        self.insert(self.__help, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.__salir = get_boton(os.path.join(ICONS_PATH, "button-cancel.svg"), flip=False, pixels=12, tooltip_text="Salir")
        self.__salir.connect("clicked", self.__emit_salir)
        self.insert(self.__salir, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.show_all()
        
    def __emit_switch(self, widget, valor):
        self.emit('switch', valor)

    def __emit_salir(self, widget):
        self.emit('salir')
        