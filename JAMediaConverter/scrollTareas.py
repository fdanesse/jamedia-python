# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaConverter.audioFrame import AudioFrame

HOME = os.environ['HOME']


class ScrollTareas(Gtk.ScrolledWindow):

    def __init__(self):

        Gtk.ScrolledWindow.__init__(self)

        self.set_css_name('scrolltareas')
        self.set_name('scrolltareas')

        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.currentDir = HOME

        vbox = Gtk.VBox()

        frame = Gtk.Frame()
        frame.set_label(" Selecciona el directorio de destino: ")
        toolbar = Gtk.Toolbar()
        toolbar.set_css_name('toolbarconverter')
        toolbar.set_name('toolbarconverter')
        
        self.dirLabel = Gtk.Label(self.currentDir)
        self.dirLabel.set_justify(Gtk.Justification.LEFT)
        item = Gtk.ToolItem()
        item.set_expand(False)
        item.add(self.dirLabel)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        self.selectFolder = get_boton(os.path.join(ICONS_PATH, "document-open.svg"), flip=False, pixels=18, tooltip_text="Seleccionar Destino")
        toolbar.insert(self.selectFolder, -1)
        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)
        toolbar.insert(item, -1)
        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        frame.add(toolbar)

        self.__info_file_in_process = Gtk.Label('No hay tareas pendientes')
        self.__info_file_in_process.get_style_context().add_class("infolabel")
        self.audioframe = AudioFrame()

        vbox.pack_start(frame, False, False, 5)
        vbox.pack_start(self.__info_file_in_process, False, False, 5)
        vbox.pack_start(self.audioframe, False, False, 5)
        # FIXME: info de archivo

        self.add(vbox)
        self.show_all()

    def set_info_file_in_process(self, path=''):
        text = 'No hay tareas pendientes'
        if path: text = "Procesando: %s" % os.path.basename(path)
        self.__info_file_in_process.set_text(text)
