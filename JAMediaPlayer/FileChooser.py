# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import YoutubeDir


class FileChooser(Gtk.FileChooserWidget):

    def __init__(self):

        Gtk.FileChooserWidget.__init__(self)

        self.get_style_context().add_class('filechooser')

        self.tipo = 'load'

        self.set_action(Gtk.FileChooserAction.OPEN)    
        filtro = Gtk.FileFilter()
        filtro.set_name("Audio y Video")
        for mi in ['audio/*', 'video/*', 'application/ogg']:
            filtro.add_mime_type(mi)
        self.add_filter(filtro)
        self.set_select_multiple(True)

        # FIXME: No funciona self.remove_shortcut_folder(APP_PATH)
        
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
        