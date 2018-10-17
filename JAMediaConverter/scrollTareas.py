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
        self.__info_file_in_process.set_line_wrap(True)
        self.__info_file_in_process.get_style_context().add_class("infolabel")
        self.audioframe = AudioFrame()

        vbox.pack_start(frame, False, False, 5)
        vbox.pack_start(self.__info_file_in_process, False, False, 5)
        vbox.pack_start(self.audioframe, False, False, 5)
        
        self.__infoFrame = Gtk.Frame()
        self.__infoFrame.set_label(" Formato de Entrada: ")
        self.__infoLabel= Gtk.Label()
        self.__infoLabel.set_line_wrap(True)
        self.__infoLabel.set_justify(Gtk.Justification.LEFT)
        self.__infoLabel.get_style_context().add_class("formatlabel")
        self.__infoFrame.add(self.__infoLabel)
        vbox.pack_start(self.__infoFrame, False, False, 5)

        self.__warningFrame = Gtk.Frame()
        self.__warningFrame.set_label(" Salteos: ")
        self.__warning_box = Gtk.VBox()
        self.__warning_box.get_style_context().add_class("errorbox")
        self.__warningFrame.add(self.__warning_box)
        vbox.pack_start(self.__warningFrame, False, False, 5)

        self.__errorsFrame = Gtk.Frame()
        self.__errorsFrame.set_label(" Errores: ")
        self.__error_box = Gtk.VBox()
        self.__error_box.get_style_context().add_class("errorbox")
        self.__errorsFrame.add(self.__error_box)
        vbox.pack_start(self.__errorsFrame, False, False, 5)
    
        self.add(vbox)
        self.connect('realize', self.setup_init)
        self.show_all()

        self.audioframe.connect("running", self.set_info_file_in_process)
        self.audioframe.connect('error', self.set_errors)
        self.audioframe.connect('info', self.set_info)
        self.audioframe.connect('warning', self.set_warning)

    def setup_init(self, widget=None):
        self.__errorsFrame.hide()
        self.__infoFrame.hide()
        self.__warningFrame.hide()

    def set_info(self, widget, info):
        pass
        '''
        if info:
            if info != self.__infoLabel.get_text():
                self.__infoLabel.set_text(info)
            self.__infoFrame.show_all()
        else:
            self.__infoLabel.set_text("")
            self.__infoFrame.hide()
        '''
        
    def set_info_file_in_process(self, widget, path):
        text = 'No hay tareas pendientes'
        if path: text = "Procesando: %s" % os.path.basename(path)
        self.__info_file_in_process.set_text(text)

    def set_errors(self, widget, text):
        if text:
            label = Gtk.Label(text)
            label.set_line_wrap(True)
            label.set_justify(Gtk.Justification.LEFT)
            label.get_style_context().add_class("errorlabel")
            self.__error_box.pack_start(label, False, False, 2)
            self.__errorsFrame.show_all()
        else:
            for widget in self.__error_box.get_children():
                self.__error_box.remove(widget)
                widget.destroy()
            self.__errorsFrame.hide()

    def set_warning(self, widget, warning):
        if warning:
            label = Gtk.Label(warning)
            label.set_line_wrap(True)
            label.set_justify(Gtk.Justification.LEFT)
            label.get_style_context().add_class("errorlabel")
            self.__warning_box.pack_start(label, False, False, 2)
            self.__warningFrame.show_all()
        else:
            for widget in self.__warning_box.get_children():
                self.__warning_box.remove(widget)
                widget.destroy()
            self.__warningFrame.hide()
