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

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.jamedia = get_boton(os.path.join(ICONS_PATH, "JAMedia.svg"), flip=False, pixels=35, tooltip_text="Cambiar a JAMedia")
        self.jamedia.connect("clicked", self.__emit_switch)
        self.insert(self.jamedia, -1)

        self.help = get_boton(os.path.join(ICONS_PATH, "help.svg"), flip=False, pixels=24, tooltip_text="Ayuda")
        self.help.connect("clicked", self.__show_help)
        self.insert(self.help, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.salir = get_boton(os.path.join(ICONS_PATH, "button-cancel.svg"), flip=False, pixels=12, tooltip_text="Salir")
        self.salir.connect("clicked", self.__salir)
        self.insert(self.salir, -1)

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
        