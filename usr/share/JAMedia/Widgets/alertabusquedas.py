# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_separador


class AlertaBusqueda(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.get_style_context().add_class('alertabusquedas')

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(True)
        self.__label = Gtk.Label("")
        self.__label.set_justify(Gtk.Justification.LEFT)
        self.__label.show()
        item.add(self.__label)
        self.insert(item, -1)

        self.show_all()
        
    def set_data(self, text):
        self.__label.set_text(text)
        self.show()
