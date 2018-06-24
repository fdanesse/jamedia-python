# -*- coding: utf-8 -*-

import os
import shelve
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from PanelTube.minitoolbar import Mini_Toolbar
from PanelTube.toolbaraccionlistasvideos import ToolbarAccionListasVideos
from PanelTube.toolbarvideosizquierda import Toolbar_Videos_Izquierda
from PanelTube.toolbarvideosderecha import Toolbar_Videos_Derecha
from PanelTube.toolbarguardar import Toolbar_Guardar

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_data_directory

TipDescargas = "Arrastra Hacia La Izquierda para Quitarlo de Descargas."
TipEncontrados = "Arrastra Hacia La Derecha para Agregarlo a Descargas"


class PanelTube(Gtk.HPaned):
    """
    Panel de JAMediaTube.
    """

    __gsignals__ = {
    'download': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, []),
    'open_shelve_list': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,
        GObject.TYPE_PYOBJECT)),
    'cancel_toolbar': (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.HPaned.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))

        self.toolbar_encontrados = None
        self.encontrados = None
        self.toolbar_guardar_encontrados = None
        self.toolbar_videos_izquierda = None
        self.toolbar_accion_izquierda = None

        self.toolbar_descargar = None
        self.descargar = None
        self.toolbar_guardar_descargar = None
        self.toolbar_videos_derecha = None
        self.toolbar_accion_derecha = None

        self.toolbars_flotantes = None

        self.__setup_init()

    def __setup_init(self):
        """
        Crea y Empaqueta todo.
        """
        self.toolbar_encontrados = Mini_Toolbar("Videos Encontrados")
        self.toolbar_guardar_encontrados = Toolbar_Guardar()
        self.encontrados = Gtk.VBox()
        
        self.toolbar_accion_izquierda = ToolbarAccionListasVideos()
        self.toolbar_videos_izquierda = Toolbar_Videos_Izquierda()
        
        self.toolbar_descargar = Mini_Toolbar("Videos Para Descargar")
        self.toolbar_guardar_descargar = Toolbar_Guardar()
        self.descargar = Gtk.VBox()
        
        self.toolbar_accion_derecha = ToolbarAccionListasVideos()
        self.toolbar_videos_derecha = Toolbar_Videos_Derecha()
        
        # Izquierda
        scroll = self.__get_scroll()
        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))
        event.add(self.encontrados)
        scroll.add_with_viewport(event)
        scroll.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))
        scroll.get_child().modify_bg(
            Gtk.StateType.NORMAL, get_colors("window1"))
        #scroll.add_with_viewport(self.encontrados)
        box = Gtk.VBox()

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_encontrados)
        box.pack_start(event, False, False, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_guardar_encontrados)
        box.pack_start(event, False, False, 0)

        box.pack_start(scroll, True, True, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_accion_izquierda)
        box.pack_start(event, False, False, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_videos_izquierda)
        box.pack_start(event, False, False, 0)

        self.pack1(box, resize=False, shrink=False)

        # Derecha
        scroll = self.__get_scroll()
        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))
        event.add(self.descargar)
        scroll.add_with_viewport(event)
        scroll.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))
        scroll.get_child().modify_bg(
            Gtk.StateType.NORMAL, get_colors("window1"))
        #scroll.add_with_viewport(self.descargar)
        box = Gtk.VBox()

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_descargar)
        box.pack_start(event, False, False, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_guardar_descargar)
        box.pack_start(event, False, False, 0)

        box.pack_start(scroll, True, True, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_accion_derecha)
        box.pack_start(event, False, False, 0)

        event = Gtk.EventBox()
        event.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))
        event.add(self.toolbar_videos_derecha)
        box.pack_start(event, False, False, 0)

        self.pack2(box, resize=False, shrink=False)

        self.show_all()
        
        self.toolbar_videos_izquierda.connect(
            'mover_videos', self.__mover_videos)
        self.toolbar_videos_derecha.connect(
            'mover_videos', self.__mover_videos)
        self.toolbar_videos_izquierda.connect(
            'borrar', self.__set_borrar)
        self.toolbar_videos_derecha.connect(
            'borrar', self.__set_borrar)
        
        self.toolbar_accion_izquierda.connect(
            'ok', self.__ejecutar_borrar)
        self.toolbar_accion_derecha.connect(
            'ok', self.__ejecutar_borrar)
        
        self.toolbar_encontrados.connect(
            'abrir', self.__abrir_lista_shelve)
        self.toolbar_encontrados.connect(
            'guardar', self.__show_toolbar_guardar)
        self.toolbar_guardar_encontrados.connect(
            'ok', self.__guardar_lista_shelve)
        
        self.toolbar_descargar.connect(
            'abrir', self.__abrir_lista_shelve)
        self.toolbar_descargar.connect(
            'guardar', self.__show_toolbar_guardar)
        
        self.toolbar_guardar_descargar.connect(
            'ok', self.__guardar_lista_shelve)
        self.toolbar_videos_derecha.connect(
            "comenzar_descarga", self.__comenzar_descarga)
        
        self.toolbar_descargar.connect(
            "menu_activo", self.__ejecutar_cancel_toolbars)
        
        self.toolbar_encontrados.connect(
            "menu_activo", self.__ejecutar_cancel_toolbars)
        
        self.toolbars_flotantes = [
            self.toolbar_guardar_encontrados,
            self.toolbar_guardar_descargar,
            self.toolbar_accion_izquierda,
            self.toolbar_accion_derecha]

        GLib.timeout_add(300, self.__update)

    def __ejecutar_cancel_toolbars(self, widget):
        map(self.__cancel_toolbars, self.toolbars_flotantes)

    def __abrir_lista_shelve(self, widget, key):
        """
        Agrega a la lista, los videos almacenados en un archivo shelve.
        """
        dict_tube = shelve.open(os.path.join(
            get_data_directory(), "List.tube"))
        _dict = dict_tube.get(key, [])
        dict_tube.close()
        videos = []
        for item in _dict.keys():
            videos.append(_dict[item])
        self.emit('open_shelve_list', videos, widget)

    def __show_toolbar_guardar(self, widget):
        """
        Muestra la toolbar para escribir nombre de archivo donde se guardarán
        los videos de la lista correspondiente.
        """
        map(self.__cancel_toolbars, self.toolbars_flotantes)
        if widget == self.toolbar_encontrados:
            self.toolbar_guardar_encontrados.show()
            self.toolbar_guardar_encontrados.entrytext.child_focus(True)
        elif widget == self.toolbar_descargar:
            self.toolbar_guardar_descargar.show()
            self.toolbar_guardar_descargar.entrytext.child_focus(True)

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
            dict_tube = shelve.open(os.path.join(get_data_directory(),
                "List.tube"))

            _dict = {}
            for elemento in videos:
                _dict[elemento["id"]] = elemento

            # Alerta de Sobre Escritura.
            if key_name in dict_tube.keys():
                dialog = Gtk.Dialog(parent=self.get_toplevel(), title="",
                buttons=(
                    "Suplantar", Gtk.ResponseType.ACCEPT,
                    "Cancelar", Gtk.ResponseType.CANCEL))

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

            dialog = Gtk.Dialog(parent=self.get_toplevel(), title="",
                buttons=("OK", Gtk.ResponseType.CANCEL))

            dialog.set_border_width(15)
            dialog.set_decorated(False)
            dialog.modify_bg(Gtk.StateType.NORMAL, get_colors("window1"))

            label = Gtk.Label("Videos Almacenados.")
            dialog.vbox.pack_start(label, True, True, 0)
            dialog.vbox.show_all()

            dialog.run()
            dialog.destroy()

    def __comenzar_descarga(self, widget):
        """
        Envia la señal descargar para comenzar la descarga de un video en la
        lista, cuando el usuario hace click en el boton descargar.
        """
        map(self.__cancel_toolbars, self.toolbars_flotantes)
        self.emit('download')

    def __mover_videos(self, widget):
        """
        Pasa todos los videos de una lista a otra.
        """
        self.set_sensitive(False)
        self.get_toplevel().toolbar_busqueda.set_sensitive(False)
        map(self.__cancel_toolbars, self.toolbars_flotantes)
        if widget == self.toolbar_videos_izquierda:
            origen = self.encontrados
            destino = self.descargar
            text = TipDescargas
        elif widget == self.toolbar_videos_derecha:
            origen = self.descargar
            destino = self.encontrados
            text = TipEncontrados
        elementos = origen.get_children()
        GLib.idle_add(self.__ejecutar_mover_videos,
            origen, destino, text, elementos)

    def __ejecutar_mover_videos(self, origen, destino, text, elementos):
        """
        Ejecuta secuencia que pasa videos desde una lista a otra.
        """
        if not elementos:
            self.set_sensitive(True)
            self.get_toplevel().toolbar_busqueda.set_sensitive(True)
            return False
        if elementos[0].get_parent() == origen:
            origen.remove(elementos[0])
            destino.pack_start(elementos[0], False, False, 1)
            elementos[0].set_tooltip_text(text)
        elementos.remove(elementos[0])
        GLib.idle_add(self.__ejecutar_mover_videos, origen, destino,
            text, elementos)

    def __ejecutar_borrar(self, widget, objetos):
        """
        Elimina una lista de videos.
        """
        self.set_sensitive(False)
        self.get_toplevel().toolbar_busqueda.set_sensitive(False)
        GLib.idle_add(self.__run_borrar, objetos)

    def __run_borrar(self, objetos):
        for objeto in objetos:
            objeto.destroy()
        self.set_sensitive(True)
        self.get_toplevel().toolbar_busqueda.set_sensitive(True)

    def __set_borrar(self, widget, objetos=None):
        """
        Llama a toolbar accion para pedir confirmacion sobre borrar un video
        o una lista de videos de la lista.
        """
        map(self.__cancel_toolbars, self.toolbars_flotantes)
        if widget == self.toolbar_videos_izquierda:
            if not objetos or objetos == None:
                objetos = self.encontrados.get_children()
            if not objetos or objetos == None:
                return  # No se abre confirmacion.
            self.toolbar_accion_izquierda.set_accion(objetos)
        elif widget == self.toolbar_videos_derecha:
            if not objetos or objetos == None:
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

    def __cancel_toolbars(self, widget):
        """
        Cuando se activa un menú o se muestra una toolbar flotante, se ocultan
        todas las demás y se envía la señal para ocultar otras toolbars
        flotantes en la raíz de la aplicación.
        """
        self.emit("cancel_toolbar")
        widget.cancelar()

    def __update_next(self, widget, items):
        """
        Un video ha actualizado sus metadatos, lanza la actualización del
        siguiente video manteniendo lo mas baja posible la actividad en la red.
        """
        if widget:
            widget.set_sensitive(True)
        if not items:
            del(items)
            self.toolbar_videos_izquierda.set_sensitive(True)
            self.toolbar_encontrados.set_sensitive(True)
            return False
        item = items[0]
        items = list(items[1:])
        if item:
            if item.get_parent():
                item.connect("end-update", self.__update_next, items)
                item.update()
            else:
                self.__update_next(False, items)
        else:
            self.__update_next(False, items)

    def cancel_toolbars_flotantes(self):
        """
        Óculta las toolbars flotantes, se llama desde la raíz de la aplicación
        cuando va a presentar una toolbar flotante allí, de este modo nunca
        habrá más de una toolbar flotante visible.
        """
        for toolbar in self.toolbars_flotantes:
            toolbar.cancelar()

    def update_widgets_videos_encontrados(self):
        """
        Luego de agregados todos los widgets de videos, cada uno actualiza sus
        previews y demás metadatos, utilizando un subproceso para no afectar a
        la interfaz gráfica.
        """
        self.toolbar_videos_izquierda.set_sensitive(False)
        self.toolbar_encontrados.set_sensitive(False)
        items = list(self.encontrados.get_children())
        for item in items:
            item.set_sensitive(False)
        self.__update_next(False, items)
