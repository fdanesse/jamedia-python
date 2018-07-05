# -*- coding: utf-8 -*-
# FIXME: Borrar si no se usa
'''
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import download_streamings
from JAMediaPlayer.Globales import set_listas_default
from JAMediaPlayer.Globales import get_ip


class DialogoDescarga(Gtk.Dialog):

    def __init__(self, parent=None, force=True):

        Gtk.Dialog.__init__(self, parent=parent)

        self.set_decorated(False)
        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        self.set_border_width(15)

        self.force = force

        label = Gtk.Label("*** Descargando Streamings de JAMedia ***")
        label.show()

        self.vbox.pack_start(label, True, True, 5)
        self.connect("realize", self.__do_realize)

    def __do_realize(self, widget):
        GLib.timeout_add(500, self.__descargar)

    def __descargar(self):
        if self.force:
            if get_ip():
                download_streamings()
            else:
                print "No estás conectado a Internet"
        else:
            set_listas_default()
        self.destroy()
        return False
'''