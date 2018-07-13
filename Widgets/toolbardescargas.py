# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.jamediayoutube import JAMediaYoutube

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso


class ToolbarDescargas(Gtk.VBox):

    __gsignals__ = {
    'end': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.set_css_name('vboxdescargas')
        self.set_name('vboxdescargas')

        self.toolbar = Gtk.Toolbar()
        self.toolbar.set_css_name('toolbardescargas')
        self.toolbar.set_name('toolbardescargas')

        self.progress = 0.0
        self.estado = False
        self.actualizador = False
        self.datostemporales = None
        self.ultimosdatos = None
        self.contadortestigo = 0

        self.video_item = None
        self.url = None
        self.titulo = None

        self.jamediayoutube = JAMediaYoutube()

        self.toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label_titulo = Gtk.Label("")
        self.label_titulo.show()
        item.add(self.label_titulo)
        self.toolbar.insert(item, -1)

        self.toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label_progreso = Gtk.Label("")
        self.label_progreso.show()
        item.add(self.label_progreso)
        self.toolbar.insert(item, -1)

        self.barra_progreso = BarraProgreso()
        self.barra_progreso.show()

        self.pack_start(self.toolbar, False, False, 0)
        self.pack_start(self.barra_progreso, False, False, 0)

        self.show_all()

        self.jamediayoutube.connect("progress_download", self.__progress_download)

    def __handle(self):
        if self.ultimosdatos != self.datostemporales:
            self.ultimosdatos = self.datostemporales
            self.contadortestigo = 0
        else:
            self.contadortestigo += 1
        if self.contadortestigo > 15:
            print ("\nNo se pudo controlar la descarga de:")
            print ("%s %s\n" % (self.titulo, self.url))
            self.__cancel_download()
            return False
        return True

    def __progress_download(self, widget, progress):
        self.datostemporales = progress
        if '[youtube]' in self.datostemporales:
            dat = self.datostemporales.replace('[youtube]', '').strip()
            if self.label_progreso.get_text() != dat:
                self.label_progreso.set_text(dat)
        elif '[download]' in self.datostemporales:
            if '%' in self.datostemporales:
                lista = self.datostemporales.strip().split(" ")
                porcentaje = [item for item in lista if "%" in item]
                if porcentaje:
                    index = lista.index(porcentaje[0])
                    text = ''
                    for item in lista[index:]:
                        text = "%s %s" % (text, item)
                    if self.label_progreso.get_text() != text.strip():
                        self.label_progreso.set_text(text.strip())
                    adj = self.barra_progreso.escala.get_adjustment()
                    GLib.idle_add(adj.set_value, float(porcentaje[0].replace("%", '')))
        if "100.0%" in self.datostemporales:
            self.__cancel_download()
            return False
        return True

    def __cancel_download(self, button=None, event=None):
        # FIXME: No funciona correctamente, la descarga continúa.
        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False
        self.jamediayoutube.reset()
        self.video_item.destroy()
        self.estado = False
        self.emit("end")
        return False

    def download(self, video_item):
        self.estado = True
        self.progress = 0.0
        self.datostemporales = None
        self.ultimosdatos = None
        self.contadortestigo = 0

        self.video_item = video_item
        self.url = video_item.videodict["url"]
        self.titulo = video_item.videodict["titulo"]

        texto = self.titulo
        if len(self.titulo) > 30:
            texto = str(self.titulo[0:30]) + " . . . "

        self.label_titulo.set_text(texto)
        self.jamediayoutube.download(self.url, self.titulo)

        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False

        self.actualizador = GLib.timeout_add(1000, self.__handle)
        self.show_all()
