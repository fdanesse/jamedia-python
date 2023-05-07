# -*- coding: utf-8 -*-

import os

import gi
gi.require_version('WebKit2', '4.0')
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import WebKit2
from gi.repository import GObject
from gi.repository import GLib

BASE_PATH = os.path.dirname(__file__)


class WebViewer(Gtk.VBox):

    def __init__(self, valor):

        Gtk.VBox.__init__(self)

        self.valor = valor

        self.set_css_name('webviewer')
        self.set_name('webviewer')

        self.__viewer = Webview()
        
        self.pack_start(self.__viewer, True, True, 0)

        self.__viewer.connect('load_failed', self.__error_load)

        self.show_all()
        self.hide()

        self.connect("realize", self.__on_realize)

    def __on_realize(self, widget):
        self.reset()

    def __error_load(self, web_view, load_event, failing_uri, error):
        uri = 'file://' + os.path.join(BASE_PATH, "onerror/onerror.html")
        GLib.idle_add(self.__viewer.load_uri, uri)
        return True

    def reset(self):
        self.__viewer.try_close()
        uri = 'file://' + os.path.join(BASE_PATH, "credits/credits.html")
        if self.valor == 'creditos':
            pass
        elif self.valor == 'radio':
            uri = "https://fdanesse-f2b2c.firebaseapp.com/jamedia_radio"
        GLib.idle_add(self.__viewer.load_uri, uri)


class Webview(WebKit2.WebView):

    def __init__(self):

        WebKit2.WebView.__init__(self)

        self.show_all()

        self.set_zoom_level(1.0)
        self.settings = self.get_settings()
        self.settings.set_property("enable-plugins", True)
        #self.settings.set_property("enable-scripts", True)
        self.set_settings(self.settings)
