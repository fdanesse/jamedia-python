# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.derecha.BalanceWidget import BalanceWidget
from JAMediaPlayer.derecha.EqualizerWidget import EqualizerWidget
from JAMediaPlayer.derecha.JAMediaPlayerList import PlayerList
from JAMediaPlayer.derecha.PlayerControls import PlayerControls
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar


class Derecha(Gtk.VBox):
    
    def __init__(self):

        Gtk.VBox.__init__(self)

        self.balance = BalanceWidget()
        self.equalizer = EqualizerWidget()
        self.lista = PlayerList()
        self.playercontrols = PlayerControls()

        balanceFrame = Gtk.Frame()
        balanceFrame.set_label(" Balance: ")
        balanceFrame.add(self.balance)

        equalizerFrame = Gtk.Frame()
        equalizerFrame.set_label(" Ecualizador: ")
        equalizerFrame.add(self.equalizer)

        confbox = Gtk.VBox()
        confbox.pack_start(balanceFrame, False, False, 0)
        confbox.pack_start(equalizerFrame, False, False, 10)

        self.__scroll = Gtk.ScrolledWindow()
        self.__scroll.get_style_context().add_class('scrolllist')
        self.__scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.__scroll.add_with_viewport(confbox)

        self.pack_start(self.__scroll, True, True, 0)
        self.pack_start(self.lista, True, True, 0)
        self.pack_end(self.playercontrols, False, False, 0)
        self.show_all()
        self.lista.lista.connect("len_items", self.__len_items)

    def __len_items(self, widget, items):
        self.playercontrols.activar(items)

    def show_config(self, val):
        if val:
            mostrar([self.__scroll])
            ocultar([self.lista, self.playercontrols])
        else:
            ocultar([self.__scroll])
            mostrar([self.lista, self.playercontrols])
        
    def setup_init(self):
        ocultar([self.__scroll])
        self.playercontrols.activar(0)
