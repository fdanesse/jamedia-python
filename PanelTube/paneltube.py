# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

#from PanelTube.minitoolbar import Mini_Toolbar
from PanelTube.toolbaraccionlistasvideos import ToolbarAccionListasVideos
from PanelTube.toolbarvideosizquierda import Toolbar_Videos_Izquierda
from PanelTube.toolbarvideosderecha import Toolbar_Videos_Derecha

from JAMediaPlayer.Globales import get_data_directory

TipDescargas = "Arrastra Hacia La Izquierda para Quitarlo de Descargas."
TipEncontrados = "Arrastra Hacia La Derecha para Agregarlo a Descargas"


class PanelTube(Gtk.HPaned):

    __gtype_name__ = 'PanelTube'

    __gsignals__ = {
    'download': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    'open_shelve_list': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT, GObject.TYPE_PYOBJECT)),
    'cancel_toolbar': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.HPaned.__init__(self)

        self.set_css_name('paneltube')
        self.set_name('paneltube')

        #self.toolbar_encontrados = Mini_Toolbar("Videos Encontrados")
        self.encontrados = Gtk.VBox()  # Contenedor de WidgetVideoItems
        self.encontrados.set_css_name('videocontainer')
        self.encontrados.set_name('videocontainer')

        self.toolbar_accion_izquierda = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_izquierda = Toolbar_Videos_Izquierda()
        
        #self.toolbar_descargar = Mini_Toolbar("Videos Para Descargar")
        self.descargar = Gtk.VBox()  # Contenedor de WidgetVideoItems
        self.descargar.set_css_name('videocontainer')
        self.descargar.set_name('videocontainer')

        self.toolbar_accion_derecha = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_derecha = Toolbar_Videos_Derecha()
        
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
        box.pack_start(self.toolbar_videos_derecha, False, False, 0)
        self.pack2(box, resize=False, shrink=False)

        self.show_all()
        
        self.toolbar_videos_izquierda.connect('mover_videos', self.__mover_videos)
        self.toolbar_videos_derecha.connect('mover_videos', self.__mover_videos)
        self.toolbar_videos_izquierda.connect('borrar', self.__set_borrar)
        self.toolbar_videos_derecha.connect('borrar', self.__set_borrar)
        self.toolbar_accion_izquierda.connect('ok', self.__ejecutar_borrar)
        self.toolbar_accion_derecha.connect('ok', self.__ejecutar_borrar)
        self.toolbar_videos_derecha.connect("comenzar_descarga", self.__comenzar_descarga)

        self.toolbars_flotantes = [self.toolbar_accion_izquierda, self.toolbar_accion_derecha]

    def __comenzar_descarga(self, widget):
        self.emit("cancel_toolbar")
        self.emit('download')

    def __mover_videos(self, widget):
        self.emit("cancel_toolbar")
        if widget == self.toolbar_videos_izquierda:
            origen = self.encontrados
            destino = self.descargar
            text = TipDescargas
        elif widget == self.toolbar_videos_derecha:
            origen = self.descargar
            destino = self.encontrados
            text = TipEncontrados
        elementos = origen.get_children()
        GLib.idle_add(self.__ejecutar_mover_videos, origen, destino, text, elementos)

    def __ejecutar_mover_videos(self, origen, destino, text, elementos):
        #FIXME: Eliminar Repetidos
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
    
    def __ejecutar_borrar(self, widget, objetos):
        self.emit("cancel_toolbar")
        for objeto in objetos:
            objeto.destroy()
        if widget == self.toolbar_accion_izquierda:
            self.toolbar_videos_izquierda.added_removed(self.encontrados)
        elif widget == self.toolbar_accion_derecha:
            self.toolbar_videos_derecha.added_removed(self.descargar)
    
    def __set_borrar(self, widget):
        self.emit("cancel_toolbar")
        if widget == self.toolbar_videos_izquierda:
            objetos = self.encontrados.get_children()
            if not objetos or objetos == None:
                return  # No se abre confirmacion.
            self.toolbar_accion_izquierda.set_accion(objetos)
        elif widget == self.toolbar_videos_derecha:
            objetos = self.descargar.get_children()
            if not objetos or objetos == None:
                return  # No se abre confirmacion.
            self.toolbar_accion_derecha.set_accion(objetos)
        else:
            print ("Caso imprevisto en run_accion de PanelTube.")

    def __get_scroll(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_css_name('scrolllist')
        scroll.set_name('scrolllist')
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        return scroll

    def __update_next(self, widget, items):
        '''Un video ha actualizado sus metadatos, lanza la actualización del siguiente.'''
        if widget:
            widget.set_sensitive(True)
        if not items:
            del(items)
            return False
        item = items[0]
        items.remove(item)
        if item:
            if item.get_parent():
                item.connect("end-update", self.__update_next, items)
                item.update()  #NOTA: en WidgetVideoItem
            else:
                self.__update_next(False, items)
        else:
            self.__update_next(False, items)

    def cancel_toolbars_flotantes(self, widget=None):
        for toolbar in self.toolbars_flotantes:
            toolbar.cancelar()

    def update_widgets_videos_encontrados(self, buscador):
        '''widgets de videos actualizan sus metadatos.'''
        items = list(self.encontrados.get_children())
        for item in items:
            item.set_sensitive(False)
        self.__update_next(False, items)
