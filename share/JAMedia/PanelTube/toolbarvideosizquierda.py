# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Toolbar_Videos_Izquierda(Gtk.Toolbar):

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.get_style_context().add_class("toolbarvideos")

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        self.__label = Gtk.Label('Encontrados: 0')
        item = Gtk.ToolItem()
        item.set_expand(False)
        item.add(self.__label)
        self.insert(item, -1)
        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.borrar = get_boton(os.path.join(ICONS_PATH, "Industry-Trash-2-icon.png"), flip=False, pixels=24, tooltip_text="Borrar Lista")
        self.insert(self.borrar, -1)

        self.mover = get_boton(os.path.join(ICONS_PATH, "play.svg"), flip=False, pixels=24, tooltip_text="Enviar a Descargas")
        self.insert(self.mover, -1)

        self.borrar.set_sensitive(False)
        self.mover.set_sensitive(False)

        self.show_all()

    def added_removed(self, widget):
        videos = len(widget.get_children())
        self.__label.set_text("Encontrados: %s" % videos)
        self.borrar.set_sensitive(bool(videos))
        self.mover.set_sensitive(bool(videos))
        