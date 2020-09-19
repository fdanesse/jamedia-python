# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.jamediayoutube import runDownload

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso


class ToolbarDescargas(Gtk.Toolbar):

    __gsignals__ = {'end': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Toolbar.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.get_style_context().add_class("toolbardescargas")

        self.estado = False
        self.__video_item = None

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

    def __progress_download(self, progress):
        if '[youtube]' in progress:
            dat = progress.replace('[youtube]', '').strip()
            if self.__label_progreso.get_text() != dat:
                self.__label_progreso.set_text(dat)
        elif '[download]' in progress:
            if '%' in progress:
                lista = progress.strip().split(" ")
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
        if "100.0%" in progress:
            GLib.idle_add(self.__cancel_download)
            return False
        return True

    def __cancel_download(self, button=None, event=None):
        self.__video_item.destroy()
        self.estado = False
        self.emit("end")
        return False

    def download(self, video_item, informe, errorDownload):
        self.estado = True
        self.__video_item = video_item
        self.__itemWidgetVideoItem.add(self.__video_item)

        texto = self.__video_item._dict["title"]
        if len(self.__video_item._dict["title"]) > 30:
            texto = str(self.__video_item._dict["title"][0:30]) + " . . . "

        self.__label_titulo.set_text(texto)
        runDownload(self.__video_item._dict["url"], self.__video_item._dict["title"], self.__progress_download, self.__cancel_download, informe, errorDownload)

        self.show_all()
