# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaConverter.toolbar import Toolbar
from JAMediaPlayer.FileChooser import FileChooser
from JAMediaPlayer.derecha.JAMediaPlayerList import PlayerList
from JAMediaConverter.OutPanel import OutPanel


class JAMediaConverter(Gtk.VBox):

    __gsignals__ = {"switch": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.__directorio = ''

        self.set_css_name('converterbox')
        self.set_name('converterbox')

        self.__toolbar = Toolbar()
        self.__base_panel = Gtk.HPaned()
        self.__filechooser = FileChooser()

        self.__playerList = PlayerList()
        self.__outpanel = OutPanel()

        self.__base_panel.pack1(self.__outpanel, resize=True, shrink=True)
        self.__base_panel.pack2(self.__playerList, resize=False, shrink=False)

        self.pack_start(self.__toolbar, False, False, 0)
        self.pack_start(self.__base_panel, True, True, 0)
        self.pack_start(self.__filechooser, True, True, 0)

        self.show_all()

        self.__toolbar.home.connect("clicked", self.__emit_switch, 'jamediatube')
        # FIXME: self.outpanel.connect('end', self.__reLoad)

        self.__playerList.toolbar.openfiles.connect("clicked", self.__openfiles, 'load')
        self.__playerList.toolbar.appendfiles.connect("clicked", self.__openfiles, 'add')
        self.__filechooser.open.connect("clicked", self.__load_files)
        self.__filechooser.connect("file-activated", self.__load_files)
        self.__filechooser.salir.connect("clicked", self.__return_to_convert)

        GLib.idle_add(self.__setup_init)

    def __emit_switch(self, widget, valor):
        self.emit('switch', valor)

    def __setup_init(self):
        self.__filechooser.hide()
        self.__toolbar.show()
        self.__base_panel.show()
        return False

    def __load_files(self, widget):
        archivos = self.__filechooser.get_filenames()
        items = []
        archivos.sort()
        for path in archivos:
            if not os.path.isfile(path):continue
            archivo = os.path.basename(path)
            items.append([archivo, path])
            self.__directorio = os.path.dirname(path)
        self.__return_to_convert(None)
        if self.__filechooser.tipo == "load": self.__playerList.lista.limpiar()
        self.__playerList.lista.agregar_items(items)

    def __return_to_convert(self, widget):
        self.__filechooser.hide()
        self.__toolbar.show()
        self.__base_panel.show()

    def __openfiles(self, widget, tipo):
        self.__toolbar.hide()
        self.__base_panel.hide()
        self.__filechooser.run(self.__directorio, tipo)