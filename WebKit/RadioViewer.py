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


class RadioViewer(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.set_css_name('radio')
        self.set_name('radio')

        self.__viewer = Webview()
        
        self.pack_start(self.__viewer, True, True, 0)

        self.__viewer.connect('load_failed', self.__error_load)

        self.show_all()
        self.run('jamediaradio')
        self.hide()

    def __error_load(self, web_view, load_event, failing_uri, error):
        self.run('error')
        return True

    def run(self, valor):
        self.__viewer.try_close()
        uri = "https://fdanesse-f2b2c.firebaseapp.com/jamedia_radio"
        if valor == 'jamediaradio':
            pass
        elif valor == 'error':
            uri = 'file://' + os.path.join(BASE_PATH, "onerror/onerror.html")
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
