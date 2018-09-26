# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.jamediayoutube import JAMediaYoutube

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso


class ToolbarDescargas(Gtk.Toolbar):

    __gsignals__ = {'end': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.get_style_context().add_class("toolbardescargas")

        self.__progress = 0.0
        self.estado = False
        self.__actualizador = False
        self.__datostemporales = None
        self.__ultimosdatos = None
        self.__contadortestigo = 0

        self.__video_item = None

        self.__jamediayoutube = JAMediaYoutube()

        self.__itemWidgetVideoItem = Gtk.ToolItem()
        self.__itemWidgetVideoItem.set_expand(False)
        self.insert(self.__itemWidgetVideoItem, -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.__label_titulo = Gtk.Label("")
        item.add(self.__label_titulo)
        self.insert(item, -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.__label_progreso = Gtk.Label("")
        item.add(self.__label_progreso)
        self.insert(item, -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.__barra_progreso = BarraProgreso()
        self.__barra_progreso.set_sensitive(False)
        item.add(self.__barra_progreso)
        self.insert(item, -1)

        self.show_all()

        self.__jamediayoutube.connect("progress_download", self.__progress_download)

    def __handle(self):
        if self.__ultimosdatos != self.__datostemporales:
            self.__ultimosdatos = self.__datostemporales
            self.__contadortestigo = 0
        else:
            self.__contadortestigo += 1
        if self.__contadortestigo > 15:
            print ("\nNo se pudo controlar la descarga de:")
            print ("%s %s\n" % (self.__video_item.videodict["titulo"], self.__video_item.videodict["url"]))
            self.__cancel_download()
            return False
        return True

    def __progress_download(self, widget, progress):
        self.__datostemporales = progress
        if '[youtube]' in self.__datostemporales:
            dat = self.__datostemporales.replace('[youtube]', '').strip()
            if self.__label_progreso.get_text() != dat:
                self.__label_progreso.set_text(dat)
        elif '[download]' in self.__datostemporales:
            if '%' in self.__datostemporales:
                lista = self.__datostemporales.strip().split(" ")
                porcentaje = [item for item in lista if "%" in item]
                if porcentaje:
                    index = lista.index(porcentaje[0])
                    text = ''
                    for item in lista[index:]:
                        text = "%s %s" % (text, item)
                    if self.__label_progreso.get_text() != text.strip():
                        self.__label_progreso.set_text(text.strip())
                    adj = self.__barra_progreso.escala.get_adjustment()
                    GLib.idle_add(adj.set_value, float(porcentaje[0].replace("%", '')))
        if "100.0%" in self.__datostemporales:
            self.__cancel_download()
            return False
        return True

    def __cancel_download(self, button=None, event=None):
        # FIXME: No funciona correctamente, la descarga continúa.
        if self.__actualizador:
            GLib.source_remove(self.__actualizador)
            self.__actualizador = False
        self.__jamediayoutube.reset()
        self.__video_item.destroy()
        self.estado = False
        self.emit("end")
        return False

    def download(self, video_item):
        self.estado = True
        self.__progress = 0.0
        self.__datostemporales = None
        self.__ultimosdatos = None
        self.__contadortestigo = 0

        self.__video_item = video_item
        self.__itemWidgetVideoItem.add(self.__video_item)

        texto = self.__video_item.videodict["titulo"]
        if len(self.__video_item.videodict["titulo"]) > 30:
            texto = str(self.__video_item.videodict["titulo"][0:30]) + " . . . "

        self.__label_titulo.set_text(texto)
        self.__jamediayoutube.download(self.__video_item.videodict["url"], self.__video_item.videodict["titulo"])

        if self.__actualizador:
            GLib.source_remove(self.__actualizador)
            self.__actualizador = False

        self.__actualizador = GLib.timeout_add(1000, self.__handle)
        self.show_all()
