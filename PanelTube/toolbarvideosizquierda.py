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

    __gsignals__ = {
    "borrar": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    "mover_videos": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarvideos')
        self.set_name('toolbarvideos')

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        self.__label = Gtk.Label('Encontrados: 0')
        self.__label.get_style_context().add_class("infotext")
        item = Gtk.ToolItem()
        item.set_expand(False)
        item.add(self.__label)
        self.insert(item, -1)
        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.__boton1 = get_boton(os.path.join(ICONS_PATH, "Industry-Trash-2-icon.png"), flip=False, pixels=24, tooltip_text="Borrar Lista")
        self.__boton1.connect("clicked", self.__emit_borrar)
        self.insert(self.__boton1, -1)

        self.__boton2 = get_boton(os.path.join(ICONS_PATH, "play.svg"), flip=False, pixels=24, tooltip_text="Enviar a Descargas")
        self.__boton2.connect("clicked", self.__emit_descargas)
        self.insert(self.__boton2, -1)

        self.__boton1.set_sensitive(False)
        self.__boton2.set_sensitive(False)

        self.show_all()

    def __emit_descargas(self, widget):
        self.emit('mover_videos')

    def __emit_borrar(self, widget):
        self.emit('borrar')

    def added_removed(self, widget):
        videos = len(widget.get_children())
        self.__label.set_text("Encontrados: %s" % videos)
        self.__boton1.set_sensitive(bool(videos))
        self.__boton2.set_sensitive(bool(videos))