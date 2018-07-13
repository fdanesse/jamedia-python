# -*- coding: utf-8 -*-

import os

import gi
gi.require_version('WebKit2', '4.0')
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import WebKit2
from gi.repository import GObject

from WebKit.Toolbar import Toolbar

BASE_PATH = os.path.dirname(__file__)


class Viewer(Gtk.VBox):

    __gsignals__ = {"salir": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.__toolbar = Toolbar()
        self.__viewer = Webview()
        
        self.pack_start(self.__toolbar, False, False, 0)
        self.pack_start(self.__viewer, True, True, 0)

        self.__toolbar.salir.connect("clicked", self.__emit_salir)

        self.show_all()

    def __emit_salir(self, widget):
        self.emit('salir')


class Webview(WebKit2.WebView):

    def __init__(self):

        WebKit2.WebView.__init__(self)

        self.show_all()

        self.set_zoom_level(1.0)
        self.settings = self.get_settings()
        self.settings.set_property("enable-plugins", True)
        #self.settings.set_property("enable-scripts", True)
        self.set_settings(self.settings)
        self.load_uri('file://' + os.path.join(BASE_PATH, "credits.html")) # "https://fdanesse-f2b2c.firebaseapp.com/jamedia_radio"

    #def load(self, url):
    #    self.load_uri(url)
