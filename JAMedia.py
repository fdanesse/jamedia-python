#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
gstreamer1.0 gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-tools gstreamer1.0-libav
'''

import os
import sys

os.putenv('GDK_BACKEND', 'x11')

import gi
gi.require_version('Gst', '1.0')
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gst

from Widgets.toolbar import Toolbar
from Widgets.toolbarbusquedas import ToolbarBusquedas
from Widgets.alertabusquedas import AlertaBusqueda
from Widgets.toolbardescargas import ToolbarDescargas
from Widgets.toolbarsalir import ToolbarSalir

from PanelTube.widgetvideoitem import WidgetVideoItem
from PanelTube.paneltube import PanelTube
from PanelTube.buscar import Buscar, FEED

from JAMediaPlayer.JAMediaPlayer import JAMediaPlayer

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import ocultar

BASE_PATH = os.path.dirname(__file__)

TipDescargas = "Arrastra Hacia La Izquierda para Quitarlo de Descargas."
TipEncontrados = "Arrastra Hacia La Derecha para Agregarlo a Descargas"

target = [Gtk.TargetEntry.new('Mover', Gtk.TargetFlags.SAME_APP, 0)]


class JAMedia(Gtk.Window):

    __gtype_name__ = 'JAMediaWindow'

    def __init__(self):

        Gtk.Window.__init__(self)

        self.set_style()

        self.set_title("JAMedia")
        self.set_icon_from_file(os.path.join(BASE_PATH,"Iconos", "JAMedia.svg"))
        self.set_resizable(True)
        #FIXME: self.set_border_width(2)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.archivos = []
        self.buscador = Buscar()

        boxbase = Gtk.VBox()

        self.box_tube = Gtk.VBox()
        self.toolbar = Toolbar()
        self.toolbar_busqueda = ToolbarBusquedas()
        self.toolbar_descarga = ToolbarDescargas()
        self.toolbar_salir = ToolbarSalir()
        self.alerta_busqueda = AlertaBusqueda()
        self.paneltube = PanelTube()

        self.box_tube.pack_start(self.toolbar, False, False, 0)
        self.box_tube.pack_start(self.toolbar_salir, False, False, 0)
        self.box_tube.pack_start(self.toolbar_busqueda, False, False, 0)
        self.box_tube.pack_start(self.toolbar_descarga, False, False, 0)

        self.box_tube.pack_start(self.alerta_busqueda, False, False, 0)
        self.box_tube.pack_start(self.paneltube, True, True, 0)

        self.jamediaplayer = JAMediaPlayer()

        boxbase.pack_start(self.box_tube, True, True, 0)
        boxbase.pack_start(self.jamediaplayer, True, True, 0)
        self.add(boxbase)

        self.connect('realize', self.__realized)
        self.show_all()
        self.realize()

        print ("JAMedia process:", os.getpid())

    def set_style(self):
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        style_path = os.path.join(BASE_PATH, "Estilo.css")
        css_provider.load_from_path(style_path)
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)

    def __realized(self, widget):
        self.toolbar_salir.cancelar()
        self.paneltube.cancel_toolbars_flotantes()
        ocultar([self.toolbar_descarga, self.alerta_busqueda])
        if self.archivos:
            self.__switch(None, 'jamedia')
            ''' FIXME: No Implementado
            self.jamediaplayer.base_panel.derecha.lista.set_nueva_lista(self.archivos)
            self.archivos = []
            '''
        else:
            self.__switch(None, 'jamediatube')

        self.paneltube.encontrados.drag_dest_set(Gtk.DestDefaults.ALL, target, Gdk.DragAction.MOVE)
        self.paneltube.encontrados.connect("drag-drop", self.__drag_drop)
        self.paneltube.encontrados.drag_dest_add_uri_targets()

        self.paneltube.descargar.drag_dest_set(Gtk.DestDefaults.ALL, target, Gdk.DragAction.MOVE)
        self.paneltube.descargar.connect("drag-drop", self.__drag_drop)
        self.paneltube.descargar.drag_dest_add_uri_targets()

        self.connect("delete-event", self.__salir)
        self.toolbar.connect('salir', self.__confirmar_salir)
        self.toolbar_salir.connect('salir', self.__salir)
        self.toolbar.connect('switch', self.__switch, 'jamedia')
        self.jamediaplayer.connect('salir', self.__switch, 'jamediatube')
        self.toolbar_busqueda.connect("comenzar_busqueda", self.__comenzar_busqueda)
        self.paneltube.connect('download', self.__run_download)
        #self.paneltube.connect('open_shelve_list', self.__open_shelve_list)
        self.toolbar_descarga.connect('end', self.__run_download)
        self.paneltube.connect("cancel_toolbar", self.toolbar_salir.cancelar)
        self.buscador.connect("encontrado", self.__add_video_encontrado)
        self.buscador.connect("end", self.paneltube.update_widgets_videos_encontrados)
        
        self.resize(640, 480)

    '''
    def __open_shelve_list(self, widget, shelve_list, toolbarwidget):
        """
        Carga una lista de videos almacenada en un archivo en el area del
        panel correspondiente según que toolbarwidget haya lanzado la señal.
        """
        self.paneltube.set_sensitive(False)
        self.toolbar_busqueda.set_sensitive(False)
        destino = False
        if toolbarwidget == self.paneltube.toolbar_encontrados:
            destino = self.paneltube.encontrados
        elif toolbarwidget == self.paneltube.toolbar_descargar:
            destino = self.paneltube.descargar
        objetos = destino.get_children()
        for objeto in objetos:
            objeto.get_parent().remove(objeto)
            objeto.destroy()
        GLib.idle_add(self.__add_videos, shelve_list, destino)
    '''
    def __run_download(self, widget):
        if self.toolbar_descarga.estado:
            return
        videos = self.paneltube.descargar.get_children()
        if videos:
            videos[0].get_parent().remove(videos[0])
            self.toolbar_descarga.download(videos[0])
        else:
            self.toolbar_descarga.hide()
    
    def __drag_drop(self, destino, drag_context, x, y, n):
        videoitem = Gtk.drag_get_source_widget(drag_context)
        if videoitem.get_parent() == destino:
            return
        else:
            # El try siguiente es para evitar problemas cuando:
            # El drag termina luego de que el origen se ha
            # comenzado a descargar y por lo tanto, no tiene padre.
            try:
                videoitem.get_parent().remove(videoitem)
                destino.pack_start(videoitem, False, False, 1)
            except:
                return
            if destino == self.paneltube.descargar:
                text = TipDescargas
            elif destino == self.paneltube.encontrados:
                text = TipEncontrados
            videoitem.set_tooltip_text(text)

    def __comenzar_busqueda(self, widget, palabras, cantidad):
        self.paneltube.set_sensitive(False)
        self.toolbar_busqueda.set_sensitive(False)
        self.toolbar_salir.cancelar()
        self.paneltube.cancel_toolbars_flotantes()
        self.alerta_busqueda.show()
        self.alerta_busqueda.label.set_text("Buscando: %s" % (palabras))
        objetos = self.paneltube.encontrados.get_children()
        for objeto in objetos:
            objeto.get_parent().remove(objeto)
            objeto.destroy()
        # FIXME: Reparar (Si no hay conexión)
        GLib.idle_add(self.buscador.buscar, palabras, cantidad)

    def __add_video_encontrado(self, buscador, _id, url):
        video = FEED.copy()
        video["id"] = _id
        video["url"] = url
        self.__add_videos([video], self.paneltube.encontrados, sensitive=False)

    def __add_videos(self, videos, destino, sensitive=True):
        if not videos:
            ocultar([self.alerta_busqueda])
            if sensitive:
                self.paneltube.set_sensitive(True)
            self.toolbar_busqueda.set_sensitive(True)
            return False

        texto = "Encontrado: %s" % (videos[0]["titulo"])
        if len(texto) > 50:
            texto = str(texto[0:50]) + " . . . "

        videowidget = WidgetVideoItem(videos[0])
        if destino == self.paneltube.encontrados:
            videowidget.set_tooltip_text(TipEncontrados)
        elif destino == self.paneltube.descargar:
            videowidget.set_tooltip_text(TipDescargas)
        videowidget.show_all()
        videowidget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, target, Gdk.DragAction.MOVE)
        videos.remove(videos[0])
        destino.pack_start(videowidget, False, False, 1)

        self.alerta_busqueda.label.set_text(texto)
        GLib.idle_add(self.__add_videos, videos, destino, sensitive)
        return False

    def __switch(self, widget, valor):
        if valor == 'jamediatube':
            self.jamediaplayer.hide()
            self.box_tube.show()
        elif valor == 'jamedia':
            self.box_tube.hide()
            self.jamediaplayer.show()

    def __confirmar_salir(self, widget=None, senial=None):
        self.paneltube.cancel_toolbars_flotantes()
        self.toolbar_salir.run("JAMediaTube")

    def __salir(self, widget=None, senial=None):
        Gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    GObject.threads_init()
    Gdk.threads_init()
    Gst.init([])
    jamedia = JAMedia()
    Gtk.main()
