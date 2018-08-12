# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaConverter.audioFrame import AudioFrame

HOME = os.environ['HOME']


class ScrollTareas(Gtk.ScrolledWindow):

    def __init__(self):

        Gtk.ScrolledWindow.__init__(self)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.__currentDir = HOME
        vbox = Gtk.VBox()

        self.__widgetDirectory = Gtk.Frame()
        #self.__widgetDirectory.set_border_width(5)
        self.__widgetDirectory.set_label(" Selecciona el directorio de destino: ")

        self.__openfiles = get_boton(os.path.join(ICONS_PATH, "document-open.svg"), flip=False, pixels=18, tooltip_text="Cargar Archivos")
        self.__openfiles.connect('clicked', self.__getDir)

        self.__dirLabel = Gtk.Label(self.__currentDir)
        event = Gtk.EventBox()
        event.set_border_width(5)
        hbox = Gtk.HBox()
        hbox.pack_start(self.__openfiles, False, False, 5)
        hbox.pack_start(self.__dirLabel, False, False, 5)
        event.add(hbox)
        self.__widgetDirectory.add(event)

        self.__audioframe = AudioFrame()

        vbox.pack_start(self.__widgetDirectory, False, False, 5)
        vbox.pack_start(self.__audioframe, False, False, 5)
        # FIXME: info de archivo

        self.add(vbox)
        self.show_all()

    def __getDir(self, widget):
        # FIXME: Agregar FileChoooser al estilo de JAMediaPlayer
        '''
        # https://people.gnome.org/~gcampagna/docs/Gtk-3.0/Gtk.FileChooserAction.html
        dialog = Gtk.FileChooserDialog(
            title="Abrir Directorio",
            parent=self.get_toplevel(),
            flags=Gtk.DialogFlags.MODAL,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            buttons=[
                "Aceptar", Gtk.ResponseType.ACCEPT,
                "Cancelar", Gtk.ResponseType.CANCEL])

        dialog.set_default_size(400, 150)
        dialog.set_border_width(15)
        dialog.set_select_multiple(False)
        dialog.set_current_folder(self.__currentDir)

        result = dialog.run()

        if result == Gtk.ResponseType.ACCEPT:
            self.__currentDir = dialog.get_filename()
        dialog.destroy()
        self.__dirLabel.set_text(self.__currentDir)
        self.__audioframe._dirOut = self.__currentDir
        '''
        pass
