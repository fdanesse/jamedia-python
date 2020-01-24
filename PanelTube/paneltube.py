# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.toolbaraccionlistasvideos import ToolbarAccionListasVideos
from PanelTube.toolbarvideosizquierda import Toolbar_Videos_Izquierda
from PanelTube.toolbarvideosderecha import Toolbar_Videos_Derecha
from PanelTube.toolbaraddvideo import ToolbarAddVideo

TipDescargas = "Arrastra Hacia La Izquierda para Quitarlo de Descargas."
TipEncontrados = "Arrastra Hacia La Derecha para Agregarlo a Descargas"


class PanelTube(Gtk.HPaned):

    __gtype_name__ = 'PanelTube'

    __gsignals__ = {
    'download': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'cancel_toolbar': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.HPaned.__init__(self)

        self.set_css_name('paneltube')
        self.set_name('paneltube')

        self.encontrados = Gtk.VBox()  # Contenedor de WidgetVideoItems
        self.encontrados.get_style_context().add_class("videocontainer")

        self.toolbar_accion_izquierda = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_izquierda = Toolbar_Videos_Izquierda()
        
        self.descargar = Gtk.VBox()  # Contenedor de WidgetVideoItems
        self.descargar.get_style_context().add_class("videocontainer")

        self.toolbar_accion_derecha = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_derecha = Toolbar_Videos_Derecha()
        
        self.toolbar_add_video = ToolbarAddVideo()

        # Izquierda       
        box = Gtk.VBox()
        scroll = self.__get_scroll()
        scroll.add_with_viewport(self.encontrados)
        box.pack_start(scroll, True, True, 0)
        box.pack_start(self.toolbar_accion_izquierda, False, False, 0)
        box.pack_start(self.toolbar_videos_izquierda, False, False, 0)
        self.pack1(box, resize=False, shrink=False)

        # Derecha
        box = Gtk.VBox()
        scroll = self.__get_scroll()
        scroll.add_with_viewport(self.descargar)
        box.pack_start(scroll, True, True, 0)
        box.pack_start(self.toolbar_accion_derecha, False, False, 0)
        box.pack_start(self.toolbar_add_video, False, False, 0)
        box.pack_start(self.toolbar_videos_derecha, False, False, 0)
        self.pack2(box, resize=False, shrink=False)

        self.show_all()
        
        self.toolbar_videos_izquierda.mover.connect('clicked', self.__mover_videos)
        self.toolbar_videos_izquierda.borrar.connect('clicked', self.__set_borrar)
        self.toolbar_videos_derecha.mover.connect('clicked', self.__mover_videos)
        self.toolbar_videos_derecha.borrar.connect('clicked', self.__set_borrar)
        self.toolbar_videos_derecha.descargar.connect("clicked", self.__comenzar_descarga)
        self.toolbar_videos_derecha.addvideo.connect('clicked', self.__run_add_video)
        self.toolbar_accion_izquierda.connect('ok', self.__ejecutar_borrar)
        self.toolbar_accion_derecha.connect('ok', self.__ejecutar_borrar)
        
        self.toolbars_flotantes = [self.toolbar_accion_izquierda, self.toolbar_add_video, self.toolbar_accion_derecha]

    def __run_add_video(self, widget):
        self.emit("cancel_toolbar")
        self.toolbar_add_video.run()

    def __comenzar_descarga(self, widget):
        self.emit("cancel_toolbar")
        self.emit('download')

    def __filter2Items(self, item, items):
        for i in items:
            if i._dict["url"].split(":")[-1] == item._dict["url"].split(":")[-1]:
                item.destroy()
                return False
        return True

    def __mover_videos(self, widget):
        self.emit("cancel_toolbar")
        if widget == self.toolbar_videos_izquierda.mover:
            origen = self.encontrados
            destino = self.descargar
            text = TipDescargas
        elif widget == self.toolbar_videos_derecha.mover:
            origen = self.descargar
            destino = self.encontrados
            text = TipEncontrados
        elementos = [item for item in origen.get_children() if self.__filter2Items(item, destino.get_children())]
        GLib.idle_add(self.__ejecutar_mover_videos, origen, destino, text, elementos)

    def __ejecutar_mover_videos(self, origen, destino, text, elementos):
        if not elementos:
            self.toolbar_videos_izquierda.added_removed(self.encontrados)
            self.toolbar_videos_derecha.added_removed(self.descargar)
            return False
        if elementos[0].get_parent() == origen:
            origen.remove(elementos[0])
            destino.pack_start(elementos[0], False, False, 3)
            elementos[0].set_tooltip_text(text)
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_mover_videos, origen, destino, text, elementos)
    
    def __ejecutar_borrar(self, widget, box):
        self.emit("cancel_toolbar")
        for objeto in box.get_children():
            objeto.destroy()
        if widget == self.toolbar_accion_izquierda:
            self.toolbar_videos_izquierda.added_removed(self.encontrados)
        elif widget == self.toolbar_accion_derecha:
            self.toolbar_videos_derecha.added_removed(self.descargar)
    
    def __set_borrar(self, widget):
        self.emit("cancel_toolbar")
        if widget == self.toolbar_videos_izquierda.borrar:
            self.toolbar_accion_izquierda.set_clear(self.encontrados)
        elif widget == self.toolbar_videos_derecha.borrar:
            self.toolbar_accion_derecha.set_clear(self.descargar)
        else:
            print ("Caso imprevisto en run_accion de PanelTube.")

    def __get_scroll(self):
        scroll = Gtk.ScrolledWindow()
        scroll.get_style_context().add_class("scrolllist")
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        return scroll

    def cancel_toolbars_flotantes(self, widget=None):
        for toolbar in self.toolbars_flotantes:
            toolbar.cancelar()
