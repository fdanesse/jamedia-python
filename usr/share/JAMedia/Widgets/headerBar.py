# https://gist.github.com/cristian99garcia/fb3b29094ecdee5a028735f9cd606773
# https://developer.gnome.org/gtk3/stable/GtkHeaderBar.html

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class HeaderBar(Gtk.HeaderBar):

    __gsignals__ = {
    'salir': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'switch': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.HeaderBar.__init__(self)

        self.get_style_context().add_class("header")
        self.set_show_close_button(False)

        btnbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.home = get_boton(os.path.join(ICONS_PATH, "home.svg"), flip=False, pixels=24, tooltip_text="JAMediaTube")
        self.home.connect("clicked", self.__emit_switch, 'jamediatube')

        self.reload = get_boton(os.path.join(ICONS_PATH, "reload.png"), flip=False, pixels=24, tooltip_text="Recargar")

        self.jamedia = get_boton(os.path.join(ICONS_PATH, "jamedia.png"), flip=False, pixels=35, tooltip_text="JAMedia")
        self.jamedia.connect("clicked", self.__emit_switch, 'jamedia')
        
        self.radio = get_boton(os.path.join(ICONS_PATH, "Music-Radio-1-icon.png"), flip=False, pixels=24, tooltip_text="JAMediaRadio")
        self.radio.connect("clicked", self.__emit_switch, 'jamediaradio')

        self.converter = get_boton(os.path.join(ICONS_PATH, "convert.svg"), flip=False, pixels=24, tooltip_text="JAMediaConverter")
        self.converter.connect("clicked", self.__emit_switch, 'jamediaconverter')

        self.help = get_boton(os.path.join(ICONS_PATH, "help.svg"), flip=False, pixels=24, tooltip_text="Ayuda")
        self.help.connect("clicked", self.__emit_switch, 'creditos')

        btnbox.pack_start(self.home, False, False, 0)
        btnbox.pack_start(self.reload, False, False, 0)
        btnbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 3)
        btnbox.pack_start(self.jamedia, False, False, 0)
        btnbox.pack_start(self.radio, False, False, 0)
        btnbox.pack_start(self.converter, False, False, 0)
        btnbox.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 3)
        btnbox.pack_start(self.help, False, False, 0)

        self.pack_start(btnbox)

        btnbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        imageClose = Gtk.Image.new_from_icon_name('window-close-symbolic', Gtk.IconSize.LARGE_TOOLBAR)
        btnClose = Gtk.Button()
        btnClose.add(imageClose)
        btnClose.connect('clicked', self.__emit_salir)
        self.version = Gtk.Label("")
        self.version.get_style_context().add_class("versionlabel")
        btnbox.pack_start(self.version, False, False, 3)
        btnbox.pack_start(btnClose, False, False, 3)
        self.pack_end(btnbox)

        self.show_all()

    def __emit_switch(self, widget, valor):
        self.emit('switch', valor)

    def __emit_salir(self, widget):
        self.emit('salir')
        