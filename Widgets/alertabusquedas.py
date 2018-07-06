# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_separador


class AlertaBusqueda(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('alertabusquedas')
        self.set_name('alertabusquedas')

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(True)
        self.label = Gtk.Label("")
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)

        self.show_all()
