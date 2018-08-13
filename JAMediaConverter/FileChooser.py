# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_tube_directory


class FileChooser(Gtk.FileChooserWidget):

    def __init__(self):

        Gtk.FileChooserWidget.__init__(self)

        self.set_css_name('filechooser')
        self.set_name('filechooser')

        self.set_action(Gtk.FileChooserAction.SELECT_FOLDER)
        
        hbox = Gtk.HBox()
        self.open = Gtk.Button("Aceptar")
        self.salir = Gtk.Button("Cancelar")
        hbox.pack_end(self.salir, True, True, 5)
        hbox.pack_end(self.open, True, True, 5)

        self.set_extra_widget(hbox)
        self.show_all()

    def run(self, path=get_tube_directory()):
        self.set_current_folder_uri("file://%s" % path)
        self.show_all()
        