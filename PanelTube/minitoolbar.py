# -*- coding: utf-8 -*-

import os
import shelve
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GObject

from PanelTube.tubelistdialog import TubeListDialog

from JAMediaPlayer.Globales import get_data_directory
from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH


class Mini_Toolbar(Gtk.Toolbar):
    """
    Mini toolbars Superior izquierda y derecha.
    """

    __gsignals__ = {
    "guardar": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, []),
    "abrir": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    "menu_activo": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, [])}

    def __init__(self, text):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("drawingplayer1"))

        self.label = None
        self.texto = text
        self.numero = 0

        item = Gtk.ToolItem()
        self.label = Gtk.Label("%s: %s" % (text, self.numero))
        #self.label.modify_fg(Gtk.StateType.NORMAL, get_colors("window1"))
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)

        self.insert(get_separador(
            draw=False, ancho=0, expand=True), -1)

        archivo = os.path.join(ICONS_PATH, "lista.svg")
        boton = get_boton(archivo, flip=False, pixels=24)
        boton.set_tooltip_text("Lista de Búsquedas")
        boton.connect("clicked", self.__get_menu)
        self.insert(boton, -1)

        archivo = os.path.join(ICONS_PATH, "play.svg")
        boton = get_boton(archivo, flip=False, pixels=24,
            rotacion=GdkPixbuf.PixbufRotation.CLOCKWISE)
        boton.set_tooltip_text("Guardar Lista")
        boton.connect("clicked", self.__emit_guardar)
        self.insert(boton, -1)

        self.show_all()

    def __emit_guardar(self, widget):
        """
        Para que se guarden todos los videos en un archivo shelve.
        """
        # FIXME:
        # (JAMedia.py:8928): Gtk-WARNING **: Negative content height -10
        # (allocation 1, extents 5x6) while allocating gadget
        #  (node button, owner GtkToggleButton)
        self.emit('guardar')

    def __emit_abrir(self, key):
        """
        Para que se carguen todos los videos desde un archivo shelve.
        """
        self.emit('abrir', key)

    def __get_menu(self, widget):
        """
        El menu con las listas de videos almacenadas en archivos shelve.
        """
        print ('FIXME:', self.__get_menu)
        '''
        dict_tube = shelve.open(os.path.join(get_data_directory(), "List.tube"))
        keys = dict_tube.keys()
        dict_tube.close()
        if keys:
            self.emit("menu_activo")
            menu = Gtk.Menu()
            administrar = Gtk.MenuItem('Administrar')
            administrar.connect_object("activate", self.__administrar, None)
            cargar = Gtk.MenuItem('Cargar')
            menu.append(administrar)
            menu.append(cargar)
            menu_listas = Gtk.Menu()
            cargar.set_submenu(menu_listas)
            for key in keys:
                item = Gtk.MenuItem(key)
                menu_listas.append(item)
                item.connect_object("activate", self.__emit_abrir, key)
            menu.show_all()
            menu.attach_to_widget(widget, self.__null)
            menu.popup(None, None, None, None, 1, 0)
        '''

    ''' 
    def __administrar(self, widget):
        dialogo = TubeListDialog(parent=self.get_toplevel())
        dialogo.run()
        dialogo.destroy()

    def __null(self):
        pass
    '''
    
    def set_info(self, valor):
        """
        Recibe un entero y actualiza la información.
        """
        if valor != self.numero:
            self.numero = valor
            text = "%s: %s" % (self.texto, str(self.numero))
            self.label.set_text(text)
            