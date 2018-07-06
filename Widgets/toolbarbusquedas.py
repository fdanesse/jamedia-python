# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import ICONS_PATH


class ToolbarBusquedas(Gtk.Toolbar):

    __gsignals__ = {
    "comenzar_busqueda": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_INT))}

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.set_css_name('toolbarbusquedas')
        self.set_name('toolbarbusquedas')

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        label = Gtk.Label("Buscar")
        label.show()
        item.add(label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.entrycantidad = Gtk.Entry()
        self.entrycantidad.props.placeholder_text = "50"
        self.entrycantidad.set_width_chars(3)
        self.entrycantidad.set_max_length(3)
        self.entrycantidad.set_tooltip_text("Escribe la cantidad de videos que deseas")
        self.entrycantidad.show()
        self.entrycantidad.connect('changed', self.__changed_entrycantidad)
        item.add(self.entrycantidad)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        label = Gtk.Label("Videos Sobre")
        label.show()
        item.add(label)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(False)
        self.entrytext = Gtk.Entry()
        self.entrytext.props.placeholder_text = "Artista, Título o ambos."
        self.entrytext.set_width_chars(20)
        self.entrytext.set_max_length(50)
        self.entrytext.set_tooltip_text("Escribe lo que Buscas")
        self.entrytext.show()
        self.entrytext.connect('activate', self.__emit_buscar)
        item.add(self.entrytext)
        self.insert(item, -1)

        self.insert(get_separador(draw=False, ancho=3, expand=False), -1)

        boton =  Gtk.ToolButton()
        boton.set_label("Run")
        boton.set_tooltip_text("Comenzar Búsqueda")
        boton.connect("clicked", self.__emit_buscar)
        self.insert(boton, -1)

        self.insert(get_separador(draw=False, ancho=0, expand=True), -1)

        self.show_all()

    def __emit_buscar(self, widget=None):
        try:
            texto = self.entrytext.get_text().strip()
            cantidad = int(self.entrycantidad.get_text())
            if texto and cantidad in range(1, 1000):
                self.entrytext.set_text("")
                self.emit("comenzar_busqueda", texto, cantidad)
            else:
                self.__alerta_busqueda_invalida()
        except:
            self.__alerta_busqueda_invalida()

    def __alerta_busqueda_invalida(self):
        # FIXME: Recordar dar estilo a este dialog
        dialog = Gtk.Dialog(parent=self.get_toplevel(), flags=Gtk.DialogFlags.MODAL, buttons=["OK", Gtk.ResponseType.OK])
        t = "No se puede realizar esta búsqueda.\n"
        t = "%s%s" % (t, "Revisa la cantidad y el texto para la búsqueda.")
        label = Gtk.Label(t)
        label.show()
        dialog.vbox.pack_start(label, True, True, 5)
        dialog.run()
        dialog.destroy()

    def __changed_entrycantidad(self, widget):
        text = widget.get_text()
        try:
            if text and not int(text) in range(1, 1000):
                widget.set_text("1")
        except:
            widget.set_text("")
