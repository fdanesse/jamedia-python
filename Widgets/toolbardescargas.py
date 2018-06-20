#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.jamediatube import JAMediaYoutube

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador

# from progressbar import ProgressBar


class ToolbarDescargas(Gtk.VBox):

    __gsignals__ = {
    'end': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.toolbar = Gtk.Toolbar()
        self.toolbar.modify_bg(Gtk.StateType.NORMAL,
            get_colors("download"))

        self.label_titulo = None
        self.label_progreso = None
        self.progress = 0.0
        self.barra_progreso = None
        self.estado = False

        self.actualizador = False

        self.datostemporales = None
        self.ultimosdatos = None
        self.contadortestigo = 0

        self.video_item = None
        self.url = None
        self.titulo = None

        self.jamediayoutube = JAMediaYoutube()

        self.toolbar.insert(get_separador(draw=False,
            ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label_titulo = Gtk.Label("")
        self.label_titulo.show()
        item.add(self.label_titulo)
        self.toolbar.insert(item, -1)

        self.toolbar.insert(get_separador(draw=False,
            ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        self.label_progreso = Gtk.Label("")
        self.label_progreso.show()
        item.add(self.label_progreso)
        self.toolbar.insert(item, -1)

        #self.toolbar.insert(G.get_separador(draw = False,
        #    ancho = 0, expand = True), -1)

        # FIXME: BUG. Las descargas no se cancelan.
        #archivo = os.path.join(BASE_PATH, "Iconos","stop.svg")
        #boton = G.get_boton(archivo, flip = False,
        #    pixels = G.get_pixels(1))
        #boton.set_tooltip_text("Cancelar")
        #boton.connect("clicked", self.cancel_download)
        #self.toolbar.insert(boton, -1)

        #self.toolbar.insert(G.get_separador(draw = False,
        #    ancho = 3, expand = False), -1)

        self.barra_progreso = Gtk.ProgressBar() #FIXME: Progreso_Descarga()
        self.barra_progreso.show()

        self.pack_start(self.toolbar, False, False, 0)
        self.pack_start(self.barra_progreso, False, False, 0)

        self.show_all()

        self.jamediayoutube.connect("progress_download",
            self.__progress_download)

    def __handle(self):
        """
        Verifica que se esté descargando el archivo.
        """
        if self.ultimosdatos != self.datostemporales:
            self.ultimosdatos = self.datostemporales
            self.contadortestigo = 0
        else:
            self.contadortestigo += 1
        if self.contadortestigo > 15:
            print "\nNo se pudo controlar la descarga de:"
            print ("%s %s\n") % (self.titulo, self.url)
            self.__cancel_download()
            return False
        return True

    def __progress_download(self, widget, progress):
        """
        Muestra el progreso de la descarga.
        """
        self.datostemporales = progress
        datos = progress.split(" ")

        if datos[0] == '[youtube]':
            dat = progress.split('[youtube]')[1]
            if self.label_progreso.get_text() != dat:
                self.label_progreso.set_text(dat)
        elif datos[0] == '[download]':
            dat = progress.split('[download]')[1]
            if self.label_progreso.get_text() != dat:
                self.label_progreso.set_text(dat)
        elif datos[0] == '\r[download]':
            porciento = 0.0
            if "%" in datos[2]:
                porciento = datos[2].split("%")[0]
            elif "%" in datos[3]:
                porciento = datos[3].split("%")[0]

            porciento = float(porciento)
            self.barra_progreso.set_progress(valor=int(porciento))

            if porciento >= 100.0:  # nunca llega
                self.__cancel_download()
                return False
            else:
                dat = progress.split("[download]")[1]
                if self.label_progreso.get_text() != dat:
                    self.label_progreso.set_text(dat)

        if "100.0%" in progress.split(" "):
            self.__cancel_download()
            return False
        if not self.get_visible():
            self.show()
        return True

    def __cancel_download(self, button=None, event=None):
        """
        Cancela la descarga actual.
        """
        # FIXME: No funciona correctamente, la descarga continúa.
        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False
        try:
            self.jamediayoutube.reset()
        except:
            pass
        try:
            self.video_item.destroy()
        except:
            pass
        self.estado = False
        self.emit("end")
        return False

    def download(self, video_item):
        """
        Comienza a descargar un video-item.
        """
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

'''
class Progreso_Descarga(Gtk.EventBox):
    """
    Barra de progreso para mostrar estado de descarga.
    """

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("download"))

        self.escala = ProgressBar(
            Gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

        self.valor = 0

        self.add(self.escala)
        self.show_all()

        self.set_size_request(-1, 28)
        self.set_progress(0)

    def set_progress(self, valor=0):
        """
        El reproductor modifica la escala.
        """
        if self.valor != valor:
            self.valor = valor
            self.escala.ajuste.set_value(valor)
            self.escala.queue_draw()
'''