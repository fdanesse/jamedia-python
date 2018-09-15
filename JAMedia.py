#!/usr/bin/python3
# -*- coding: utf-8 -*-

# API: https://lazka.github.io/pgi-docs
# gstreamer1.0 gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
# python3-magic
# gir1.2-webkit2-4.0

import os
import sys

import gi
gi.require_version('Gst', '1.0')
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gst

from Widgets.headerBar import HeaderBar
from Widgets.toolbarbusquedas import ToolbarBusquedas
from Widgets.alertabusquedas import AlertaBusqueda
from Widgets.toolbardescargas import ToolbarDescargas
from Widgets.toolbarsalir import ToolbarSalir
from PanelTube.widgetvideoitem import WidgetVideoItem
from PanelTube.paneltube import PanelTube
from PanelTube.buscar import Buscar, FEED
from JAMediaPlayer.JAMediaPlayer import JAMediaPlayer
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import get_dict
from WebKit.WebViewer import WebViewer
from WebKit.WebViewer import WebViewer
from JAMediaConverter.JAMediaConverter import JAMediaConverter

BASE_PATH = os.path.dirname(__file__)

TipDescargas = "Arrastra Hacia La Izquierda para Quitarlo de Descargas."
TipEncontrados = "Arrastra Hacia La Derecha para Agregarlo a Descargas"

target = [Gtk.TargetEntry.new('Mover', Gtk.TargetFlags.SAME_APP, 0)]

'''
NOTA: Activa este código en la función realize para ver la estructura de widgets del programa
def make_tree_widgets(widget, tab):
    try:
        children = widget.get_children()
    except:
        return
    tab = ('%s\t') % tab
    for child in children:
        print (tab, type(child))
        make_tree_widgets(child, tab)
'''


class JAMedia(Gtk.Window):

    __gtype_name__ = 'JAMediaWindow'

    def __init__(self):

        Gtk.Window.__init__(self)

        self.set_style()

        self.version = get_dict(os.path.join(BASE_PATH, 'proyecto.ide')).get('version', 18)

        self.set_title("JAMedia")
        self.set_icon_from_file(os.path.join(BASE_PATH, "Iconos", "JAMedia.svg"))
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.archivos = []
        self.buscador = Buscar()

        self.headerBar = HeaderBar()
        self.headerBar.set_title("JAMedia")
        self.headerBar.version.set_text("V. %s" % self.version)
        self.set_titlebar(self.headerBar)

        boxbase = Gtk.VBox()
        self.toolbar_salir = ToolbarSalir()
        boxbase.pack_start(self.toolbar_salir, False, False, 0)

        self.box_tube = Gtk.VBox()
        self.box_tube.set_css_name('boxtube')
        self.box_tube.set_name('boxtube')
        self.toolbar_busqueda = ToolbarBusquedas()
        self.toolbar_descarga = ToolbarDescargas()
        self.alerta_busqueda = AlertaBusqueda()
        self.paneltube = PanelTube()

        self.box_tube.pack_start(self.toolbar_busqueda, False, False, 0)
        self.box_tube.pack_start(self.toolbar_descarga, False, False, 0)
        self.box_tube.pack_start(self.alerta_busqueda, False, False, 0)
        self.box_tube.pack_start(self.paneltube, True, True, 0)

        self.jamediaplayer = JAMediaPlayer()
        self.jamediaconverter = JAMediaConverter()
        self.helpCreditsViewer = WebViewer('creditos')
        self.jamediaradioViewer = WebViewer('radio')

        boxbase.pack_start(self.box_tube, True, True, 0)
        boxbase.pack_start(self.jamediaplayer, True, True, 0)
        boxbase.pack_start(self.jamediaconverter, True, True, 0)
        boxbase.pack_start(self.helpCreditsViewer, True, True, 0)
        boxbase.pack_start(self.jamediaradioViewer, True, True, 0)
        self.add(boxbase)

        self.connect('realize', self.__realized)
        self.show_all()
        
        print ("JAMedia process:", os.getpid())

    def set_style(self):
        screen = Gdk.Screen.get_default()
        css_provider = Gtk.CssProvider()
        style_path = os.path.join(BASE_PATH, "Estilos", "Estilo.css")
        css_provider.load_from_path(style_path)
        context = Gtk.StyleContext()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)

    def __realized(self, widget):
        ocultar([self.toolbar_descarga, self.alerta_busqueda])

        self.paneltube.encontrados.drag_dest_set(Gtk.DestDefaults.ALL, target, Gdk.DragAction.MOVE)
        self.paneltube.encontrados.connect("drag-drop", self.__drag_drop)
        self.paneltube.encontrados.drag_dest_add_uri_targets()

        self.paneltube.descargar.drag_dest_set(Gtk.DestDefaults.ALL, target, Gdk.DragAction.MOVE)
        self.paneltube.descargar.connect("drag-drop", self.__drag_drop)
        self.paneltube.descargar.drag_dest_add_uri_targets()

        self.headerBar.connect('switch', self.__switch)
        self.headerBar.connect('salir', self.__confirmar_salir)
        self.headerBar.reload.connect("clicked", self.__reset_webview)

        self.toolbar_salir.connect('salir', self.__salir)
        self.toolbar_busqueda.connect("comenzar_busqueda", self.__comenzar_busqueda)
        self.paneltube.connect('download', self.__run_download)
        self.toolbar_descarga.connect('end', self.__run_download)
        self.paneltube.connect("cancel_toolbar", self.__cancel_toolbars)
        self.paneltube.toolbar_add_video.connect('ok', self.__user_add_video)
        self.buscador.connect("encontrado", self.__add_video_encontrado)
        self.buscador.connect("end", self.paneltube.update_widgets_videos_encontrados)

        if self.archivos:
            self.__switch(None, 'jamedia')
            # FIXME: Abrir la aplicación desde nautilus no está Implementado
            # self.jamediaplayer.base_panel.derecha.lista.set_nueva_lista(self.archivos)
            # self.archivos = []
        else:
            self.__switch(None, 'jamediatube')
            
        self.resize(640, 480)
        # make_tree_widgets(self)

    def __reset_webview(self, widget):
        if self.helpCreditsViewer.get_visible():
            self.helpCreditsViewer.reset()
        elif self.jamediaradioViewer.get_visible():
            self.jamediaradioViewer.reset()

    def __cancel_toolbars(self, widget=None):
        self.toolbar_salir.cancelar()
        self.paneltube.cancel_toolbars_flotantes()

    def __run_download(self, widget):
        if self.toolbar_descarga.estado:
            return
        videos = self.paneltube.descargar.get_children()
        if videos:
            videos[0].get_parent().remove(videos[0])
            self.toolbar_descarga.download(videos[0])
            self.paneltube.toolbar_videos_derecha.added_removed(self.paneltube.descargar)
        else:
            self.toolbar_descarga.hide()
    
    def __drag_drop(self, destino, drag_context, x, y, n):
        videoitem = Gtk.drag_get_source_widget(drag_context)
        if videoitem.get_parent() == destino:
            return
        else:
            # NOTA: Para evitar problemas cuando el drag termina luego de que el origen se ha comenzado a descargar y por lo tanto, no tiene padre.
            try:
                videoitem.get_parent().remove(videoitem)
                destino.pack_start(videoitem, False, False, 3)
            except:
                return
            if destino == self.paneltube.descargar:
                text = TipDescargas
            elif destino == self.paneltube.encontrados:
                text = TipEncontrados
            videoitem.set_tooltip_text(text)
            self.paneltube.toolbar_videos_izquierda.added_removed(self.paneltube.encontrados)
            self.paneltube.toolbar_videos_derecha.added_removed(self.paneltube.descargar)

    def __comenzar_busqueda(self, widget, palabras, cantidad):
        self.toolbar_busqueda.set_sensitive(False)
        self.__cancel_toolbars()
        self.alerta_busqueda.show()
        self.alerta_busqueda.label.set_text("Buscando: %s..." % (palabras))
        objetos = self.paneltube.encontrados.get_children()
        for objeto in objetos:
            objeto.get_parent().remove(objeto)
            objeto.destroy()
        self.paneltube.toolbar_videos_izquierda.added_removed(self.paneltube.encontrados)
        # FIXME: Reparar (Si no hay conexión)
        GLib.idle_add(self.buscador.buscar, palabras, cantidad)

    def __add_video_encontrado(self, buscador, _id, url):
        video = FEED.copy()
        video["id"] = _id
        video["url"] = url
        self.__add_videos([video], self.paneltube.encontrados)

    def __user_add_video(self, widget, url):
        video = FEED.copy()
        video["url"] = url
        self.__add_videos([video], self.paneltube.descargar)
        self.paneltube.update_widget_video(video)

    def __add_videos(self, videos, destino):
        if not videos:
            ocultar([self.alerta_busqueda])
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
        destino.pack_start(videowidget, False, False, 3)
        if destino == self.paneltube.encontrados:
            self.paneltube.toolbar_videos_izquierda.added_removed(self.paneltube.encontrados)
        elif destino == self.paneltube.descargar:
            self.paneltube.toolbar_videos_derecha.added_removed(self.paneltube.descargar)
        self.alerta_busqueda.label.set_text(texto)
        GLib.idle_add(self.__add_videos, videos, destino)
        return False

    def __switch(self, widget, valor):
        self.__cancel_toolbars()
        if valor == 'jamediatube':
            self.headerBar.home.hide()
            self.headerBar.reload.hide()
            self.headerBar.jamedia.show()
            self.headerBar.converter.show()
            self.headerBar.help.show()
            self.headerBar.radio.show()

            self.jamediaplayer.hide()
            self.jamediaconverter.hide()
            self.helpCreditsViewer.hide()
            self.jamediaradioViewer.hide()

            self.box_tube.show()

        elif valor == 'jamedia':
            self.headerBar.home.show()
            self.headerBar.reload.hide()
            self.headerBar.jamedia.hide()
            self.headerBar.converter.show()
            self.headerBar.help.show()
            self.headerBar.radio.show()

            self.box_tube.hide()
            self.helpCreditsViewer.hide()
            self.jamediaradioViewer.hide()
            self.jamediaconverter.hide()

            self.jamediaplayer.show()

        elif valor == 'creditos':
            self.headerBar.home.show()
            self.headerBar.reload.show()
            self.headerBar.jamedia.show()
            self.headerBar.converter.show()
            self.headerBar.help.hide()
            self.headerBar.radio.show()

            self.box_tube.hide()
            self.jamediaplayer.hide()
            self.jamediaconverter.hide()
            self.jamediaradioViewer.hide()

            self.helpCreditsViewer.show()
        
        elif valor == 'jamediaradio':
            self.headerBar.home.show()
            self.headerBar.reload.show()
            self.headerBar.jamedia.show()
            self.headerBar.converter.show()
            self.headerBar.help.show()
            self.headerBar.radio.hide()

            self.box_tube.hide()
            self.jamediaplayer.hide()
            self.jamediaconverter.hide()
            self.helpCreditsViewer.hide()

            self.jamediaradioViewer.show()

        elif valor == 'jamediaconverter':
            self.headerBar.home.show()
            self.headerBar.reload.hide()
            self.headerBar.jamedia.show()
            self.headerBar.converter.hide()
            self.headerBar.help.show()
            self.headerBar.radio.show()

            self.box_tube.hide()
            self.jamediaplayer.hide()
            self.helpCreditsViewer.hide()
            self.jamediaradioViewer.hide()

            self.jamediaconverter.show()

    def __confirmar_salir(self, widget=None, senial=None):
        self.paneltube.cancel_toolbars_flotantes()
        self.toolbar_salir.run()

    def __salir(self, widget=None, senial=None):
        Gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    GObject.threads_init()
    Gdk.threads_init()
    Gst.init(None)
    jamedia = JAMedia()
    Gtk.main()
