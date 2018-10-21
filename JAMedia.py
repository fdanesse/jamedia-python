#!/usr/bin/python3
# -*- coding: utf-8 -*-

# API: https://lazka.github.io/pgi-docs
# gstreamer1.0 gstreamer1.0-libav gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly
# python3-magic
# gir1.2-webkit2-4.0

import os
import sys
import time
import threading
import signal

import gi
gi.require_version('Gst', '1.0')
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import Gst
from gi.repository import Gio

from Widgets.headerBar import HeaderBar
from Widgets.toolbarbusquedas import ToolbarBusquedas
from Widgets.toolbardescargas import ToolbarDescargas
from Widgets.alertabusquedas import AlertaBusqueda
from Widgets.toolbarsalir import ToolbarSalir
from PanelTube.widgetvideoitem import WidgetVideoItem
from PanelTube.paneltube import PanelTube
from PanelTube.jamediayoutube import buscar
from JAMediaPlayer.JAMediaPlayer import JAMediaPlayer
from JAMediaPlayer.Globales import ocultar
from JAMediaPlayer.Globales import get_dict
from WebKit.WebViewer import WebViewer
from WebKit.WebViewer import WebViewer
from JAMediaConverter.JAMediaConverter import JAMediaConverter
from PanelTube.InformeDescargas import InformeDescargas

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

screen = Gdk.Screen.get_default()
css_provider = Gtk.CssProvider()
style_path = os.path.join(BASE_PATH, "Estilos", "Estilo.css")
css_provider.load_from_path(style_path)
context = Gtk.StyleContext()
context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_SETTINGS)


class JAMedia(Gtk.Application):

    def __init__(self):

        Gtk.Application.__init__(self)

        self.set_flags(Gio.ApplicationFlags.NON_UNIQUE | Gio.ApplicationFlags.HANDLES_OPEN)

    def do_activate(self):
        self.win = JAMediaWindow(self)
        self.win.show()

    def do_open(self, files, i, hint):
        print(files, i, hint)
        '''
        if len(files) > 1:
            print("Multiple files not supported, using %s" % files[0].get_path())
        if not files[0].query_exists(None):
        print("%s doesn't exist" % files[0].get_path())
            return
        '''
        self.do_activate ()

    def do_startup (self):
        Gtk.Application.do_startup(self)


class JAMediaWindow(Gtk.ApplicationWindow):

    __gtype_name__ = 'JAMediaWindow'

    def __init__(self, app):

        Gtk.Window.__init__(self, title="JAMedia", application=app)

        self.version = get_dict(os.path.join(BASE_PATH, 'proyecto.ide')).get('version', 18)

        self.__informe = InformeDescargas()

        self.set_default_size(640, 480)
        self.set_size_request(640, 480)

        self.set_title("JAMedia")
        self.set_icon_from_file(os.path.join(BASE_PATH, "Iconos", "JAMedia.svg"))
        self.set_resizable(True)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.archivos = []
        self.__videosEncontrados = []

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
        self.connect("delete-event", self.__salir)
        self.show_all()
        
        print ("JAMedia process:", os.getpid())

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
        if self.toolbar_descarga.estado: return
        videos = self.paneltube.descargar.get_children()
        if videos:
            videos[0].get_parent().remove(videos[0])
            self.toolbar_descarga.download(videos[0], self.__informe) # FIXME: Agregar opciones para cancelados en descargas
            self.paneltube.toolbar_videos_derecha.added_removed(self.paneltube.descargar)
        else:
            self.toolbar_descarga.hide()
    
    def __drag_drop(self, destino, drag_context, x, y, n):
        # FIXME: Agregar imagen al drag
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

    def __filterItems(self, item, url):
        return item._dict["url"].split(":")[-1] == url.split(":")[-1]

    def __user_add_video(self, widget, url):
        # El usuario agrega manualmene un video
        items = self.paneltube.descargar.get_children()
        items.extend(self.paneltube.encontrados.get_children())
        if not [item for item in items if self.__filterItems(item, url)]:
            videowidget = WidgetVideoItem(url)
            videowidget.set_tooltip_text(TipDescargas)
            videowidget.show_all()
            videowidget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, target, Gdk.DragAction.MOVE)
            self.paneltube.descargar.pack_start(videowidget, False, False, 3)
            self.paneltube.toolbar_videos_derecha.added_removed(self.paneltube.descargar)
            #videowidget.connect("end-update", self.__make_append_update_video, urls)
            videowidget.update()
        else:
            print("FIXME: El video ya está listado")

    def __comenzar_busqueda(self, widget, palabras, cantidad):
        # 1 - Busquedas
        self.toolbar_busqueda.set_sensitive(False)
        self.__cancel_toolbars()
        self.alerta_busqueda.set_data("Buscando: %s..." % (palabras))
        # Que se puedan sumar búsquedas
        #objetos = self.paneltube.encontrados.get_children()
        #for objeto in objetos:
        #    self.paneltube.remove(objeto)
        #for objeto in objetos:
        #    GLib.idle_add(objeto.destroy)
        self.__videosEncontrados = []        
        self.paneltube.toolbar_videos_izquierda.added_removed(self.paneltube.encontrados)
        # FIXME: Verificar si es necesario matar los hilos al terminar la busqueda
        threading.Thread(target=buscar, args=(palabras, cantidad, self.__add_video_encontrado, self.__busquedasEnd)).start()
        
    def __add_video_encontrado(self, url):
        # 2 - Busquedas
        items = self.paneltube.descargar.get_children()
        items.extend(self.paneltube.encontrados.get_children())
        if not [item for item in items if self.__filterItems(item, url)]:
            if not str(url).strip() in self.__videosEncontrados:
                self.__videosEncontrados.append(str(url).strip())
                self.alerta_busqueda.set_data("Encontrado: %s..." % (url))
        else:
            self.alerta_busqueda.set_data("Ya se encuentra listado: %s..." % (url))

    def __busquedasEnd(self):
        # 3 - Busquedas
        self.toolbar_busqueda.set_sensitive(True)
        self.__make_append_update_video(None, list(self.__videosEncontrados))
        self.__videosEncontrados = []

    def __make_append_update_video(self, item, urls):
        # 4 - Busquedas. crear, agregar, actualizar
        if item:
            self.paneltube.encontrados.pack_start(item, False, False, 3)
            self.paneltube.toolbar_videos_izquierda.added_removed(self.paneltube.encontrados)
        if urls:
            self.alerta_busqueda.set_data("Actualizando: %s..." % (urls[0]))
            # FIXME: agregar barra de progreso y cantidad de videos encontrados
            videowidget = WidgetVideoItem(urls[0])
            videowidget.set_tooltip_text(TipEncontrados)
            videowidget.show_all()
            videowidget.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, target, Gdk.DragAction.MOVE)
            urls.remove(urls[0])
            videowidget.connect("end-update", self.__make_append_update_video, urls)
            videowidget.connect("error-update", self.__cancel_append_video, urls)
            videowidget.update() # 5 - Busquedas
        else:
            ocultar([self.alerta_busqueda])

    def __cancel_append_video(self, item, urls):
        # FIXME: Agregar opciones para cancelados en metadatos
        self.__informe.setInfo('cancelados en metadatos', item._dict["url"])
        item.destroy()
        self.__make_append_update_video(None, urls)

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
        #Gtk.main_quit()
        sys.exit(0)


if __name__ == "__main__":
    GObject.threads_init()
    Gdk.threads_init()
    Gst.init("--opengl-hwdec-interop=vaapi-glx")
    jamedia = JAMedia()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    exit_status = jamedia.run(sys.argv)
    sys.exit(exit_status)
    #Gtk.main()
