# -*- coding: utf-8 -*-

import os
#import shelve
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.minitoolbar import Mini_Toolbar
from PanelTube.toolbaraccionlistasvideos import ToolbarAccionListasVideos
from PanelTube.toolbarvideosizquierda import Toolbar_Videos_Izquierda
from PanelTube.toolbarvideosderecha import Toolbar_Videos_Derecha
#from PanelTube.toolbarguardar import Toolbar_Guardar

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

        self.toolbar_encontrados = Mini_Toolbar("Videos Encontrados")
        #self.toolbar_guardar_encontrados = Toolbar_Guardar()
        self.encontrados = Gtk.VBox()  # Contenedor de WidgetVideoItems
        
        self.toolbar_accion_izquierda = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_izquierda = Toolbar_Videos_Izquierda()
        
        self.toolbar_descargar = Mini_Toolbar("Videos Para Descargar")
        #self.toolbar_guardar_descargar = Toolbar_Guardar()
        self.descargar = Gtk.VBox()  # Contenedor de WidgetVideoItems
        
        self.toolbar_accion_derecha = ToolbarAccionListasVideos()  # Confirmar borrar lista de videos
        self.toolbar_videos_derecha = Toolbar_Videos_Derecha()
        
        # Izquierda       
        box = Gtk.VBox()
        box.pack_start(self.toolbar_encontrados, False, False, 0)
        #box.pack_start(self.toolbar_guardar_encontrados, False, False, 0)
        scroll = self.__get_scroll()
        scroll.add_with_viewport(self.encontrados)
        box.pack_start(scroll, True, True, 0)
        box.pack_start(self.toolbar_accion_izquierda, False, False, 0)
        box.pack_start(self.toolbar_videos_izquierda, False, False, 0)
        self.pack1(box, resize=False, shrink=False)

        # Derecha
        box = Gtk.VBox()
        box.pack_start(self.toolbar_descargar, False, False, 0)
        #box.pack_start(self.toolbar_guardar_descargar, False, False, 0)
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
        
        #self.toolbar_encontrados.connect('abrir', self.__abrir_lista_shelve)
        #self.toolbar_encontrados.connect('guardar', self.__show_toolbar_guardar)
        #self.toolbar_guardar_encontrados.connect('ok', self.__guardar_lista_shelve)
        
        #self.toolbar_descargar.connect('abrir', self.__abrir_lista_shelve)
        #self.toolbar_descargar.connect('guardar', self.__show_toolbar_guardar)
        #self.toolbar_guardar_descargar.connect('ok', self.__guardar_lista_shelve)

        self.toolbar_videos_derecha.connect("comenzar_descarga", self.__comenzar_descarga)
        
        #self.toolbar_descargar.connect("menu_activo", self.cancel_toolbars_flotantes)
        #self.toolbar_encontrados.connect("menu_activo", self.cancel_toolbars_flotantes)
        
        self.toolbars_flotantes = [
            #self.toolbar_guardar_encontrados,
            #self.toolbar_guardar_descargar,
            self.toolbar_accion_izquierda,
            self.toolbar_accion_derecha]

        GLib.timeout_add(300, self.__update)

    '''
    def __abrir_lista_shelve(self, widget, key):
        """
        Agrega a la lista, los videos almacenados en un archivo shelve.
        """
        dict_tube = shelve.open(os.path.join(get_data_directory(), "List.tube"))
        _dict = dict_tube.get(key, [])
        dict_tube.close()
        videos = []
        for item in _dict.keys():
            videos.append(_dict[item])
        self.emit('open_shelve_list', videos, widget)
    '''

    '''
    def __show_toolbar_guardar(self, widget):
        """
        Muestra la toolbar para escribir nombre de archivo donde se guardarán
        los videos de la lista correspondiente.
        """
        #map(self.__cancel_toolbars, self.toolbars_flotantes)
        if widget == self.toolbar_encontrados:
            self.toolbar_guardar_encontrados.show()
            self.toolbar_guardar_encontrados.entrytext.child_focus(True)
        elif widget == self.toolbar_descargar:
            self.toolbar_guardar_descargar.show()
            self.toolbar_guardar_descargar.entrytext.child_focus(True)
    '''
    '''
    def __guardar_lista_shelve(self, widget, key_name):
        """
        Guarda todos los videos de la lista bajo la key según key_name.
        """
        origen = False
        if widget == self.toolbar_guardar_encontrados:
            origen = self.encontrados
        elif widget == self.toolbar_guardar_descargar:
            origen = self.descargar

        videos = []
        if origen:
            video_items = origen.get_children()
            if video_items:
                for video in video_items:
                    videos.append(video.videodict)

        if videos:
            dict_tube = shelve.open(os.path.join(get_data_directory(), "List.tube"))

            _dict = {}
            for elemento in videos:
                _dict[elemento["id"]] = elemento

            # Alerta de Sobre Escritura.
            if key_name in dict_tube.keys():
                dialog = Gtk.Dialog(parent=self.get_toplevel(), title="",
                buttons=("Suplantar", Gtk.ResponseType.ACCEPT, "Cancelar", Gtk.ResponseType.CANCEL))

                dialog.set_border_width(15)
                dialog.set_decorated(False)
                dialog.modify_bg(Gtk.StateType.NORMAL, get_colors("window1"))

                text = "Ya Existe un Album de Búsquedas con Este Nombre.\n"
                text = "%s%s" % (text, "¿Deseas Suplantarlo?")
                label = Gtk.Label(text)
                dialog.vbox.pack_start(label, True, True, 0)
                dialog.vbox.show_all()

                response = dialog.run()
                dialog.destroy()

                if response == Gtk.ResponseType.CANCEL:
                    dict_tube.close()
                    return

            dict_tube[key_name] = _dict
            dict_tube.close()

            dialog = Gtk.Dialog(parent=self.get_toplevel(), title="", buttons=("OK", Gtk.ResponseType.CANCEL))

            dialog.set_border_width(15)
            dialog.set_decorated(False)
            dialog.modify_bg(Gtk.StateType.NORMAL, get_colors("window1"))

            label = Gtk.Label("Videos Almacenados.")
            dialog.vbox.pack_start(label, True, True, 0)
            dialog.vbox.show_all()

            dialog.run()
            dialog.destroy()
    '''

    def __comenzar_descarga(self, widget):
        """
        Comenzar la descarga.
        """
        #FIXME: map(self.__cancel_toolbars, self.toolbars_flotantes)
        self.emit('download')

    def __mover_videos(self, widget):
        """
        Pasa todos los videos de una lista a otra.
        """
        #FIXME: Eliminar Repetidos
        #self.set_sensitive(False)
        #self.get_toplevel().toolbar_busqueda.set_sensitive(False)
        #map(self.__cancel_toolbars, self.toolbars_flotantes)
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
        if not elementos:
            #self.set_sensitive(True)
            #self.get_toplevel().toolbar_busqueda.set_sensitive(True)
            return False
        if elementos[0].get_parent() == origen:
            origen.remove(elementos[0])
            destino.pack_start(elementos[0], False, False, 1)
            elementos[0].set_tooltip_text(text)
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_mover_videos, origen, destino, text, elementos)
    
    def __ejecutar_borrar(self, widget, objetos):
        #self.set_sensitive(False)
        #self.get_toplevel().toolbar_busqueda.set_sensitive(False)
        for objeto in objetos:
            objeto.destroy()
        #self.set_sensitive(True)
        #self.get_toplevel().toolbar_busqueda.set_sensitive(True)
    
    def __set_borrar(self, widget):
        """
        Llama a toolbar accion para pedir confirmacion sobre borrar una lista de videos de la lista.
        """
        self.cancel_toolbars_flotantes()
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
    
    def __update(self):
        """
        Actualiza información en toolbars de videos encontrados y en descaga.
        """
        encontrados = len(self.encontrados.get_children())
        endescargas = len(self.descargar.get_children())
        self.toolbar_encontrados.set_info(encontrados)
        self.toolbar_descargar.set_info(endescargas)
        return True

    def __get_scroll(self):
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        return scroll

    '''
    def __cancel_toolbars(self, widget):
        """
        Cuando se activa un menú o se muestra una toolbar flotante, se ocultan
        todas las demás y se envía la señal para ocultar otras toolbars
        flotantes en la raíz de la aplicación.
        """
        self.emit("cancel_toolbar")
        widget.cancelar()
    '''

    def __update_next(self, widget, items):
        """
        Un video ha actualizado sus metadatos, lanza la actualización del siguiente.
        """
        if widget:
            widget.set_sensitive(True)
        if not items:
            del(items)
            self.toolbar_videos_izquierda.set_sensitive(True)
            self.toolbar_encontrados.set_sensitive(True)
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
        """
        widgets de videos actualizan sus metadatos.
        """
        self.toolbar_videos_izquierda.set_sensitive(False)
        self.toolbar_encontrados.set_sensitive(False)
        items = list(self.encontrados.get_children())
        for item in items:
            item.set_sensitive(False)
        self.__update_next(False, items)
        self.set_sensitive(True)  #NOTA: Desde JAMedia.__comenzar_busqueda esta insensitive
