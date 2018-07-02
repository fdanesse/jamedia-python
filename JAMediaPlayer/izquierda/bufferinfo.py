# -*- coding: utf-8 -*-

# FIXME: Borrar si no se usa
'''
import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GdkPixbuf

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador
from JAMediaPlayer.Globales import get_boton
from JAMediaPlayer.Globales import ICONS_PATH
from JAMediaPlayer.Globales import sensibilizar
from JAMediaPlayer.Globales import insensibilizar


class BufferInfo(Gtk.EventBox):

    def __init__(self):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("windows"))
        self.set_border_width(4)

        self.escala = ProgressBar(
            Gtk.Adjustment(0.0, 0.0, 101.0, 0.1, 1.0, 1.0))

        self.valor = 0

        box = Gtk.EventBox()
        box.modify_bg(Gtk.StateType.NORMAL, get_colors("windows"))
        box.set_border_width(4)
        box.add(self.escala)

        frame = Gtk.Frame()
        frame.set_border_width(4)
        frame.set_label(" Cargando Buffer ... ")
        frame.set_label_align(0.0, 0.5)

        frame.add(box)
        self.add(frame)
        self.show_all()

    def set_progress(self, valor=0.0):
        if self.valor != valor:
            self.valor = valor
            self.escala.ajuste.set_value(valor)
            self.escala.queue_draw()
        if self.valor == 100.0:
            self.hide()
        else:
            self.show()
'''

'''
class ProgressBar(Gtk.HScale):

    def __init__(self, ajuste):

        Gtk.HScale.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL, get_colors("toolbars"))

        self.ajuste = ajuste
        self.set_digits(0)
        self.set_draw_value(False)


        self.show_all()
        self.set_sensitive(False)
'''