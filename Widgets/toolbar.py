# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

# FIXME: from Widgets.help import Help

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton

from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar(Gtk.Toolbar):

    __gsignals__ = {
    'salir': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'switch': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer1"))

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        archivo = os.path.join(ICONS_PATH, "JAMedia.svg")
        self.jamedia = get_boton(archivo, flip=False, pixels=35)
        self.jamedia.set_tooltip_text("Cambiar a JAMedia")
        self.jamedia.connect("clicked", self.__emit_switch)
        self.insert(self.jamedia, -1)

        archivo = os.path.join(ICONS_PATH, "help.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Ayuda")
        boton.connect("clicked", self.__show_help)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Salir")
        boton.connect("clicked", self.__salir)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.show_all()

    def __show_help(self, widget):
        print ('FIXME:', self.__show_help)
        '''
        dialog = Help(parent=self.get_toplevel())
        dialog.run()
        dialog.destroy()
        '''
        
    def __emit_switch(self, widget):
        self.emit('switch')

    def __salir(self, widget):
        self.emit('salir')
        