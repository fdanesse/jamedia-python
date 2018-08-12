# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
#from gi.repository import GObject

from JAMediaConverter.scrollTareas import ScrollTareas

HOME = os.environ['HOME']


class OutPanel(Gtk.VBox):

    #__gsignals__ = {"end": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.__scrollTareas = ScrollTareas()
        self.pack_start(self.__scrollTareas, True, True, 0)
        # FIXME: Agregar FileChoooser al estilo de JAMediaPlayer
        self.show_all()
        #self.__scrollTareas.audioframe.connect('end', self.__reset)
        #self.__scrollTareas.audioframe.start.connect("clicked", self.__run)

    '''def __run(self, widget):
        self.__scrollTareas.audioframe.start.set_sensitive(False)
        self.__scrollTareas.open.set_sensitive(False)
        self.__scrollTareas.audioframe.run()'''

    '''def __reset(self, widget):
        self.emit('end')
        self.__scrollTareas.audioframe.start.set_sensitive(True)
        self.__scrollTareas.open.set_sensitive(True)'''
