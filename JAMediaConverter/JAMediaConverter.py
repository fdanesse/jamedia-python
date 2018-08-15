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
from JAMediaConverter.FileChooser import FileChooser as FileChooser2
from JAMediaConverter.scrollTareas import ScrollTareas


class JAMediaConverter(Gtk.VBox):

    __gsignals__ = {"switch": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.__directorio = ''

        self.set_css_name('converterbox')
        self.set_name('converterbox')

        self.__toolbar = Toolbar()
        self.__base_panel = Gtk.HPaned()
        self.__filechooser = FileChooser()      # Para armar la lista de arcivos a convertir
        self.__filechooser2 = FileChooser2()    # Para seleccionar directorio destino de las conversiones

        self.__playerList = PlayerList()
        self.__outBox = Gtk.VBox()
        self.__scrollTareas = ScrollTareas()
        self.__outBox.pack_start(self.__scrollTareas, True, True, 0)

        self.__base_panel.pack1(self.__outBox, resize=True, shrink=True)
        self.__base_panel.pack2(self.__playerList, resize=False, shrink=False)

        self.pack_start(self.__toolbar, False, False, 0)
        self.pack_start(self.__base_panel, True, True, 0)
        self.pack_start(self.__filechooser, True, True, 0)
        self.pack_start(self.__filechooser2, True, True, 0)

        self.show_all()

        self.__toolbar.home.connect("clicked", self.__emit_switch, 'jamediatube')
        self.__playerList.toolbar.openfiles.connect("clicked", self.__openfiles, 'load')
        self.__playerList.toolbar.appendfiles.connect("clicked", self.__openfiles, 'add')
        self.__playerList.lista.connect('len_items', self.__file_list_changed)
        self.__filechooser.open.connect("clicked", self.__load_files)
        self.__filechooser.connect("file-activated", self.__load_files)
        self.__filechooser.salir.connect("clicked", self.__setup_init)
        self.__scrollTareas.selectFolder.connect('clicked', self.__run_selectFolder)
        self.__scrollTareas.audioframe.start.connect("clicked", self.__run)
        self.__scrollTareas.audioframe.connect('end', self.__reset)
        self.__filechooser2.salir.connect("clicked", self.__setup_init)
        self.__filechooser2.open.connect("clicked", self.__folder_selected)

        # FIXME: self.__outBox.set_sensitive(False)
        GLib.idle_add(self.__setup_init)

    def __reset(self, widget):
        # FIXME: self.__outBox.set_sensitive(True)
        self.__playerList.set_sensitive(True)

    def __run(self, widget):
        # FIXME: self.__outBox.set_sensitive(False)
        self.__playerList.set_sensitive(False)
        self.__scrollTareas.audioframe.run()

    def __file_list_changed(self, widget, cantidad):
        # FIXME: self.__outBox.set_sensitive(bool(cantidad))
        self.__scrollTareas.audioframe.set_files(list(self.__playerList.lista.getItems()))

    def __folder_selected(self, widget):
        currentDir = self.__filechooser2.get_filename()
        self.__scrollTareas.currentDir = currentDir
        self.__scrollTareas.dirLabel.set_text(currentDir)
        self.__scrollTareas.audioframe._dirOut = currentDir
        self.__setup_init()
        
    def __run_selectFolder(self, widget):
        self.__filechooser.hide()
        self.__toolbar.hide()
        self.__base_panel.hide()
        self.__filechooser2.show()

    def __emit_switch(self, widget, valor):
        self.emit('switch', valor)

    def __setup_init(self, widget=False):
        self.__filechooser.hide()
        self.__filechooser2.hide()
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
        self.__setup_init(None)
        if self.__filechooser.tipo == "load": self.__playerList.lista.limpiar()
        self.__playerList.lista.agregar_items(items)

    def __openfiles(self, widget, tipo):
        self.__toolbar.hide()
        self.__base_panel.hide()
        self.__filechooser.run(self.__directorio, tipo)