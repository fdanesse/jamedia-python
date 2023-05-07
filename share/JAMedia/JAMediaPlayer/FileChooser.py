# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import YoutubeDir

APP_PATH = os.path.dirname(os.path.dirname(__file__))


class FileChooser(Gtk.FileChooserWidget):

    def __init__(self):

        Gtk.FileChooserWidget.__init__(self)

        self.get_style_context().add_class('filechooser')

        self.tipo = 'load'

        self.set_action(Gtk.FileChooserAction.OPEN)    
        self.__filtro = Gtk.FileFilter()
        self.__filtro.set_name("Audio y Video")
        for mi in ['audio/*', 'video/*', 'application/ogg']:
            self.__filtro.add_mime_type(mi)
        self.add_filter(self.__filtro)
        
        hbox = Gtk.HBox()
        self.open = Gtk.Button("Abrir")
        self.select_btn = Gtk.Button("Seleccionar Todos")
        self.salir = Gtk.Button("Salir")

        hbox.pack_end(self.salir, True, True, 5)
        hbox.pack_end(self.select_btn, True, True, 5)
        hbox.pack_end(self.open, True, True, 5)

        self.select_btn.connect("clicked", self.__select_all)

        self.set_extra_widget(hbox)
        self.show_all()

    def __select_all(self, widget):
        self.select_all()

    def run(self, path, tipo):
        self.tipo = tipo
        if not path: path = YoutubeDir
        self.set_current_folder_uri("file://%s" % path)
        self.show_all()
        self.remove_shortcut_folder(APP_PATH)
        if self.tipo == 'suburi':
            if self.__filtro.get_name() != "Subtítulos":
                self.remove_filter(self.__filtro)
                self.__filtro = Gtk.FileFilter()
                self.__filtro.set_name("Subtítulos")
                self.__filtro.add_pattern('*.srt')
                self.add_filter(self.__filtro)
            self.set_select_multiple(False)
            self.select_btn.hide()
        else:
            if self.__filtro.get_name() != "Audio y Video":
                self.remove_filter(self.__filtro)
                self.__filtro = Gtk.FileFilter()
                self.__filtro.set_name("Audio y Video")
                for mi in ['audio/*', 'video/*', 'application/ogg']:
                    self.__filtro.add_mime_type(mi)
                self.add_filter(self.__filtro)
            self.set_select_multiple(True)
            self.select_btn.show()
        
