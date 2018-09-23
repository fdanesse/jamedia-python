# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Widgets.ProgressPlayer import BarraProgreso


class EqualizerWidget(Gtk.Table):

    __gsignals__ = {
    'equalizer-valor': (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE,(GObject.TYPE_FLOAT, GObject.TYPE_STRING))}

    def __init__(self):

        Gtk.Table.__init__(self, rows=10, columns=1, homogeneous=True)

        self.__banda0 = ToolbarcontrolValores("Banda 0")
        self.__banda1 = ToolbarcontrolValores("Banda 1")
        self.__banda2 = ToolbarcontrolValores("Banda 2")
        self.__banda3 = ToolbarcontrolValores("Banda 3")
        self.__banda4 = ToolbarcontrolValores("Banda 4")
        self.__banda5 = ToolbarcontrolValores("Banda 5")
        self.__banda6 = ToolbarcontrolValores("Banda 6")
        self.__banda7 = ToolbarcontrolValores("Banda 7")
        self.__banda8 = ToolbarcontrolValores("Banda 8")
        self.__banda9 = ToolbarcontrolValores("Banda 9")

        self.attach(self.__banda0, 0, 1, 0, 1)
        self.attach(self.__banda1, 0, 1, 1, 2)
        self.attach(self.__banda2, 0, 1, 2, 3)
        self.attach(self.__banda3, 0, 1, 3, 4)
        self.attach(self.__banda4, 0, 1, 4, 5)
        self.attach(self.__banda5, 0, 1, 5, 6)
        self.attach(self.__banda6, 0, 1, 6, 7)
        self.attach(self.__banda7, 0, 1, 7, 8)
        self.attach(self.__banda8, 0, 1, 8, 9)
        self.attach(self.__banda9, 0, 1, 9, 10)

        self.show_all()

        self.set_size_request(150, -1)

        '''self.__banda1.connect('valor',self.__emit_senial, 'brillo')
        self.__banda2.connect('valor',self.__emit_senial, 'contraste')
        self.__banda3.connect('valor',self.__emit_senial, 'saturacion')
        self.__banda4.connect('valor',self.__emit_senial, 'hue')
        self.__banda5.connect('valor',self.__emit_senial, 'gamma')'''

        #self.set_equalizer()

    def __emit_senial(self, widget, valor, tipo):
        self.emit('equalizer-valor', valor, tipo)

    '''def set_equalizer(self, brillo=50.0, contraste=50.0, saturacion=50.0, hue=50.0):
        if saturacion != None: self.__banda3.set_progress(saturacion)
        if contraste != None: self.__banda2.set_progress(contraste)
        if brillo != None: self.__banda1.set_progress(brillo)
        if hue != None: self.__banda4.set_progress(hue)
        if gamma != None: self.__banda5.set_progress(gamma)'''


class ToolbarcontrolValores(Gtk.Toolbar):

    __gsignals__ = {
    'valor': (GObject.SIGNAL_RUN_LAST,GObject.TYPE_NONE, (GObject.TYPE_FLOAT,))}

    def __init__(self, label):

        Gtk.Toolbar.__init__(self)

        self.__titulo = label
        self.__escala = BarraProgreso()

        self.__frame = Gtk.Frame()
        self.__frame.set_label(self.__titulo)
        self.__frame.set_label_align(0.5, 1.0)

        event = Gtk.EventBox()
        event.add(self.__escala)
        self.__frame.add(event)
        self.__frame.show_all()

        item = Gtk.ToolItem()
        item.set_expand(True)
        item.add(self.__frame)
        self.insert(item, -1)

        self.show_all()

        self.__escala.escala.connect("motion-notify-event", self.__user_set_value)

    def __user_set_value(self, widget, event):
        valor = self.__escala.escala.get_adjustment().get_value()
        self.emit("valor", valor)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(valor), "%"))

    def set_progress(self, valor):
        GLib.idle_add(self.__escala.escala.get_adjustment().set_value, valor)
        self.__frame.set_label("%s: %s%s" % (self.__titulo, int(valor), "%"))
