# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.derecha.BalanceWidget import BalanceWidget
from JAMediaPlayer.derecha.JAMediaPlayerList import PlayerList
from JAMediaPlayer.derecha.PlayerControls import PlayerControls
from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar


class Derecha(Gtk.EventBox):
    
    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        vbox = Gtk.VBox()
        confbox = Gtk.VBox()

        self.balance = BalanceWidget()
        self.lista = PlayerList()
        self.playercontrols = PlayerControls()

        confbox.pack_start(self.balance, False, False, 0)

        self.__scroll = Gtk.ScrolledWindow()
        self.__scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.__scroll.add_with_viewport(confbox)
        self.__scroll.get_child().modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        vbox.pack_start(self.__scroll, True, True, 0)
        vbox.pack_start(self.lista, True, True, 0)
        vbox.pack_end(self.playercontrols, False, False, 0)
        self.add(vbox)
        self.show_all()
        self.lista.lista.connect("len_items", self.__len_items)
        self.set_size_request(150, -1)

    def __len_items(self, widget, items):
        self.playercontrols.activar(items)

    def show_config(self):
        valor = self.__scroll.get_visible()
        if valor:
            ocultar([self.__scroll])
            mostrar([self.lista, self.playercontrols])
        else:
            mostrar([self.__scroll])
            ocultar([self.lista, self.playercontrols])
        
    def setup_init(self):
        #FIXME: activar y desactivar los iconos de la toolbar en la lista de reproducción
        ocultar([self.__scroll])
        self.playercontrols.activar(0)
