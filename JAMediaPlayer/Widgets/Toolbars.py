# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Widgets.credits import Credits
from JAMediaPlayer.Widgets.help import Help

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import get_toggle_boton
from JAMediaPlayer.Globales import get_my_files_directory
#from JAMediaPlayer.Globales import describe_acceso_uri
#from JAMediaPlayer.Globales import copiar
#from JAMediaPlayer.Globales import borrar
#from JAMediaPlayer.Globales import mover

from JAMediaPlayer.Globales import ICONS_PATH
# FIXME: Borrar las Toolbars que no se usan


class Toolbar(Gtk.EventBox):

    __gsignals__ = {
    'show_config': (GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE, (GObject.TYPE_BOOLEAN,))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.ocultar_controles = False

        toolbar = Gtk.Toolbar()

        #self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))
        #toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        boton = get_boton(os.path.join(ICONS_PATH, "JAMedia.svg"), flip=False, pixels=35, tooltip_text="Creditos")
        #FIXME: boton.connect("clicked", self.__show_credits)
        toolbar.insert(boton, -1)

        boton = get_boton(os.path.join(ICONS_PATH, "help.svg"), flip=False, pixels=24, tooltip_text="Ayuda")
        #FIXME: boton.connect("clicked", self.__show_help)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.configurar = get_toggle_boton(os.path.join(ICONS_PATH, "control_panel.png"), flip=False, pixels=24, tooltip_text="Configuraciones")
        self.configurar.connect("toggled", self.__emit_show_config)
        toolbar.insert(self.configurar, -1)

        self.__controls = get_toggle_boton(os.path.join(ICONS_PATH, "controls.svg"), flip=True, pixels=24, tooltip_text="Ocultar/Mostrar Controles")
        self.__controls.connect("toggled", self.__set_controles_view)
        toolbar.insert(self.__controls, -1)

        self.__full = get_toggle_boton(os.path.join(ICONS_PATH, "fullscreen.png"), flip=True, pixels=24, tooltip_text="Full/UnFull Screen")
        self.__full.connect("toggled", self.__set_full)
        toolbar.insert(self.__full, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.salir = get_boton(os.path.join(ICONS_PATH, "button-cancel.svg"), flip=False, pixels=12, tooltip_text="Salir")
        toolbar.insert(self.salir, -1)

        toolbar.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        self.add(toolbar)
        self.show_all()
    
    def set_full(self, widget):
        self.__full.set_active(not self.__full.get_active())

    def __set_full(self, widget):
        win = self.get_toplevel()
        if self.__full.get_active():
            win.fullscreen()
        else:
            win.unfullscreen()

    def __set_controles_view(self, widget):
        self.ocultar_controles = widget.get_active()

    def __emit_show_config(self, widget):
        self.emit('show_config', widget.get_active())

    '''
    def __show_credits(self, widget):
        dialog = Credits(parent=self.get_toplevel())
        dialog.run()
        dialog.destroy()
    '''
    
    '''
    def __show_help(self, widget):
        dialog = Help(parent=self.get_toplevel())
        dialog.run()
        dialog.destroy()
    '''


'''
class ToolbarAccion(Gtk.EventBox):
    """
    Toolbar para que el usuario confirme las acciones que se realizan sobre
    items que se seleccionan en la lista de reproduccion.
        (Borrar, mover, copiar, quitar).
    """

    __gsignals__ = {
    "grabar": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    "accion-stream": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.EventBox.__init__(self)

        toolbar = Gtk.Toolbar()

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))
        toolbar.modify_bg(Gtk.StateType.NORMAL, get_colors("window"))

        self.lista = None
        self.accion = None
        self.iter = None

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "button-cancel.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Cancelar")
        boton.connect("clicked", self.cancelar)
        toolbar.insert(boton, -1)

        item = Gtk.ToolItem()
        self.label = Gtk.Label("")
        self.label.modify_bg(Gtk.StateType.NORMAL, get_colors("drawingplayer"))
        self.label.show()
        item.add(self.label)
        toolbar.insert(item, -1)

        archivo = os.path.join(ICONS_PATH, "dialog-ok.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Aceptar")
        boton.connect("clicked", self.__realizar_accion)
        toolbar.insert(boton, -1)

        toolbar.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.add(toolbar)
        self.show_all()

    def __realizar_accion(self, widget):
        """
        Ejecuta una accion sobre un archivo o streaming en la lista.
        """
        uri = self.lista.get_model().get_value(self.iter, 2)
        if self.accion == "Quitar":
            path = self.lista.get_model().get_path(self.iter)
            path = (path[0] - 1, )
            self.lista.get_model().remove(self.iter)
            self.__reselect(path)
        else:
            if describe_acceso_uri(uri):
                if self.accion == "Copiar":
                    if os.path.isfile(uri):
                        copiar(uri, get_my_files_directory())
                elif self.accion == "Borrar":
                    if os.path.isfile(uri):
                        if borrar(uri):
                            path = self.lista.get_model().get_path(self.iter)
                            path = (path[0] - 1, )
                            self.lista.get_model().remove(self.iter)
                            self.__reselect(path)
                elif self.accion == "Mover":
                    if os.path.isfile(uri):
                        if mover(uri, get_my_files_directory()):
                            path = self.lista.get_model().get_path(self.iter)
                            path = (path[0] - 1, )
                            self.lista.get_model().remove(self.iter)
                            self.__reselect(path)
            else:
                if self.accion == "Borrar":
                    self.emit("accion-stream", "Borrar", uri)
                    path = self.lista.get_model().get_path(self.iter)
                    path = (path[0] - 1, )
                    self.lista.get_model().remove(self.iter)
                    self.__reselect(path)
                elif self.accion == "Copiar":
                    self.emit("accion-stream", "Copiar", uri)
                elif self.accion == "Mover":
                    self.emit("accion-stream", "Mover", uri)
                    path = self.lista.get_model().get_path(self.iter)
                    path = (path[0] - 1, )
                    self.lista.get_model().remove(self.iter)
                    self.__reselect(path)
                elif self.accion == "Grabar":
                    self.emit("grabar", uri)
        self.cancelar()

    def __reselect(self, path):
        try:
            if path[0] > -1:
                self.lista.get_selection().select_iter(
                    self.lista.get_model().get_iter(path))
            else:
                self.lista.seleccionar_primero()
        except:
            self.lista.seleccionar_primero()

    def set_accion(self, lista, accion, _iter):
        """
        Configura una accion sobre un archivo o streaming y muestra
        toolbaraccion para que el usuario confirme o cancele dicha accion.
        """
        self.lista = lista
        self.accion = accion
        self.iter = _iter
        if self.lista and self.accion and self.iter:
            uri = self.lista.get_model().get_value(self.iter, 2)
            texto = uri
            if os.path.exists(uri):
                texto = os.path.basename(uri)
            if len(texto) > 30:
                texto = " . . . " + str(texto[len(texto) - 30:-1])
            self.label.set_text("¿%s?: %s" % (accion, texto))
            self.show_all()

    def cancelar(self, widget=None):
        self.label.set_text("")
        self.lista = None
        self.accion = None
        self.iter = None
        self.hide()
'''
