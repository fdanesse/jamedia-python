# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

from PanelTube.jamediayoutube import getJsonAndThumbnail
from JAMediaPlayer.Globales import json_file


class WidgetVideoItem(Gtk.EventBox):

    __gsignals__ = {
        "end-update": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
        "error-update": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),}

    def __init__(self, url):

        Gtk.EventBox.__init__(self)
        
        self.set_size_request(200, 100)

        self.__fileimage = ""
        self.__filejson = ""

        self._dict = OrderedDict({
            'id': '',
            'title': '',
            'duration': '', 
            'ext': '',
            'width': '',
            'height': '',
            'format': '',
            'fps': '',
            'url': url,
            'thumbnail': ''
            })

        self.get_style_context().add_class("videoitem")

        hbox = Gtk.HBox()
        hbox.get_style_context().add_class("videoitemHB")
        self.__imagen = Gtk.Image()
        hbox.pack_start(self.__imagen, False, False, 3)
        
        self.__vbox = Gtk.VBox()
        for key in self._dict.keys():
            label = Gtk.Label("%s: %s" % (key, self._dict[key]))
            label.set_alignment(0.0, 0.5)
            self.__vbox.pack_start(label, True, True, 0)

        hbox.pack_start(self.__vbox, False, False, 5)
        self.add(hbox)

        self.show_all()
    
    def __del__(self):
        if os.path.exists(self.__fileimage): os.unlink(self.__fileimage)
        if os.path.exists(self.__filejson): os.unlink(self.__filejson)

    def __setImage(self, width=200, height=150):
        if os.path.exists(self.__fileimage):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.__fileimage, width, height)
            self.__imagen.set_from_pixbuf(pixbuf)

    def __setLabels(self):
        values = list(self._dict.items())
        labels = self.__vbox.get_children()
        for label in labels:
            label.set_text("%s: %s" % (values[labels.index(label)]))

    def update(self):
        # 5 - Busquedas. NOTA: desde PanelTube
        getJsonAndThumbnail(self._dict["url"], self.__endUpdate)

    def __endUpdate(self, _dict):
        # 7 - Busquedas
        self.__fileimage = _dict.get("thumb", "")
        self.__filejson = _dict["json"]
        # NOTA: si los archivos no existen cuelga la aplicación
        if os.path.exists(self.__fileimage) and os.path.exists(self.__fileimage):
            newdict = json_file(self.__filejson)
            for key in self._dict.keys():
                if key == "url": continue
                self._dict[key] = newdict.get(key, None)
            self.__setImage()
            self.__setLabels()
            self.emit("end-update")
        else:
            self.emit("error-update")
