#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from BalanceWidget import BalanceWidget
from JAMediaPlayerList import PlayerList
from PlayerControls import PlayerControls
from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import mostrar


class Derecha(Gtk.EventBox):

    __gsignals__ = {
    "cargar-reproducir": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "accion-list": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,
        GObject.TYPE_STRING, GObject.TYPE_PYOBJECT)),
    "menu_activo": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, []),
    #"add_stream": (GObject.SIGNAL_RUN_LAST,
    #    GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "accion-controls": (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    'balance-valor': (GObject.SIGNAL_RUN_LAST,
        GObject.TYPE_NONE, (GObject.TYPE_FLOAT,
        GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window"))

        vbox = Gtk.VBox()
        conf_box = Gtk.VBox()

        self.balance = BalanceWidget()
        self.lista = PlayerList()
        self.player_controls = PlayerControls()

        conf_box.pack_start(self.balance, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER,
            Gtk.PolicyType.AUTOMATIC)
        scroll.add_with_viewport(conf_box)
        scroll.get_child().modify_bg(
            Gtk.StateType.NORMAL, get_colors("window"))

        vbox.pack_start(scroll, True, True, 0)
        vbox.pack_start(self.lista, True, True, 0)
        vbox.pack_end(self.player_controls, False, False, 0)

        self.add(vbox)

        self.show_all()

        self.balance.connect("balance-valor",
            self.__emit_balance)

        self.lista.connect("nueva-seleccion",
            self.__emit_cargar_reproducir)
        self.lista.connect("accion-list",
            self.__emit_accion_list)
        self.lista.connect("menu_activo",
            self.__emit_menu_activo)
        #self.lista.connect("add_stream", self.__emit_add_stream)
        self.lista.connect("len_items",
            self.__items_in_list)

        self.player_controls.connect("accion-controls",
            self.__emit_accion_controls)

        self.set_size_request(150, -1)

    def __items_in_list(self, widget, items):
        self.player_controls.activar(items)

    def __emit_balance(self, widget, valor, prop):
        # brillo, contraste, saturación, hue, gamma
        self.emit('balance-valor', valor, prop)

    def __emit_accion_controls(self, widget, accion):
        # anterior, siguiente, pausa, play, stop
        self.emit("accion-controls", accion)

    '''
    def __emit_add_stream(self, widget, title):
        # El usuario agregará una dirección de streaming
        self.emit("add_stream", title)
    '''

    def __emit_menu_activo(self, widget=False):
        # hay un menu contextual presente
        self.emit("menu_activo")

    def __emit_accion_list(self, widget, lista, accion, _iter):
        # borrar, copiar, mover, grabar, etc . . .
        self.emit("accion-list", lista, accion, _iter)

    def __emit_cargar_reproducir(self, widget, path):
        self.emit("cargar-reproducir", path)

    def show_config(self):
        objs = self.get_child().get_children()
        valor = objs[0].get_visible()
        if valor:
            ocultar(objs[0])
            map(mostrar, objs[1:])
        else:
            mostrar(objs[0])
            map(ocultar, objs[1:])

    def setup_init(self):
        ocultar(self.get_child().get_children()[0])
        self.lista.setup_init()
        self.player_controls.activar(0)

    '''
    def set_ip(self, valor):
        self.lista.set_ip(valor)
    '''
    
    def set_nueva_lista(self, archivos):
        self.lista.set_nueva_lista(archivos)
