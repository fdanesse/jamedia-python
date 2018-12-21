# -*- coding: utf-8 -*-

import os
import time
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from JAMediaConverter.Gstreamer.Converter1 import Converter
from JAMediaPlayer.Globales import MAGIC

HOME = os.environ['HOME']


class AudioFrame(Gtk.Frame):

    __gsignals__ = {
        "end": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, []),
        "running": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
        "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
        "warning": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "error": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self._converters = {}       # Codecs activos {"ogg":None, "mp3":None, "wav":None}
        self._codecsprogress = {}   # Progreso de cada codec

        self._inicial_files = []
        self._files = []
        self._dirOut = HOME
        self._initialFilesCount = 0
        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_show_text(True)
        self._progressbar.get_style_context().add_class("convertprogress")
        self._checks = []

        self.__videoCodecs = ["ogv", "webm", "mp4", "avi", "mpg", "png"]
        self._progress = {"ogg":None, "mp3":None, "wav":None, "webm":None, "ogv":None, "mp4":None, "avi":None, "mpg":None, "png":None}

        self.set_label(" Elige los formatos de extracción: ")
        self.get_label_widget().get_style_context().add_class("labelcodecs")

        table = Gtk.Table(rows=14, columns=9, homogeneous=True)
        table.set_col_spacings(0)

        row = 0
        label = Gtk.Label("Solo Audio")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0.0)
        label.get_style_context().add_class("labelcodecs")
        table.attach(label, 0, 9, row, row+1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
        row = self.__packProgress(table, ["mp3", "ogg", "wav"], row+1)

        label = Gtk.Label("Audio y Video")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0.0)
        label.get_style_context().add_class("labelcodecs")
        table.attach(label, 0, 9, row, row+1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
        row = self.__packProgress(table, ["avi", "ogv", "mp4", "mpg", "webm"], row+1)

        label = Gtk.Label("Solo Imágenes")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0.0)
        label.get_style_context().add_class("labelcodecs")
        table.attach(label, 0, 9, row, row+1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
        row = self.__packProgress(table, ["png"], row+1)

        table.set_row_spacing(row=11, spacing=15)
        label = Gtk.Label("Total:")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_xalign(0.0)
        label.get_style_context().add_class("labelcodecs")
        table.attach(label, 0, 2, row, row+1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
        table.attach(self._progressbar, 2, 9, row, row+1, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        table.set_row_spacing(row=12, spacing=15)
        row += 1
        self.start = Gtk.Button('Convertir')
        self.start.set_css_name('startbutton')
        self.start.set_name('startbutton')
        self.start.set_sensitive(False)
        table.attach(self.start, 0, 4, row, row+3, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.cancelar = Gtk.Button('Cancelar')
        self.cancelar.set_css_name('startbutton')
        self.cancelar.set_name('startbutton')
        self.cancelar.set_sensitive(False)
        table.attach(self.cancelar, 5, 9, row, row+3, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.add(table)
        self.show_all()

        self.cancelar.connect("clicked", self.__cancel_all)

    def __packProgress(self, table, _codecs, row=0):
        for formato in _codecs:
            # http://python-gtk-3-tutorial.readthedocs.io/en/latest/button_widgets.html
            check = Gtk.CheckButton(formato)
            check.get_style_context().add_class("convertcheck")
            self._checks.append(check)
            progress = Gtk.ProgressBar()
            progress.set_show_text(True)
            progress.get_style_context().add_class("convertprogress")
            # http://www.mono-project.com/docs/gui/gtksharp/widgets/packing-with-tables/
            table.attach(check, 0, 2, row, row+1,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
            table.attach(progress, 2, 9, row, row+1,
                Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                Gtk.AttachOptions.EXPAND, 0, 0)
            row += 1
            check.connect("toggled", self.__toggledButton)
            self._progress[formato] = progress
        return row

    def __cancel_all(self, widget):
        self._files = []
        for codec in self._converters.keys():
            if self._converters[codec] != None:
                self._converters[codec].stop()
                self._converters[codec] = None
        self.__end_all()
        
    def set_files(self, _files):
        self._files = []
        for f in _files:
            self._files.append(f[1])
        self._inicial_files = self._files.copy()
        self._initialFilesCount = len(self._files)
        self.start.set_sensitive(bool(self._files) and bool(self._converters.keys()))
        # FIXME: Que los check se activen según los tipos de archivos que se carguen ?

    def __toggledButton(self, widget):
        if widget.get_active():
            self._converters[widget.get_label()] = None
        else:
            del(self._converters[widget.get_label()])
        self.start.set_sensitive(bool(self._files) and bool(self._converters.keys()))

    def run(self, widget=None):
        # Se ejecuta para iniciar todas las conversiones de cada archivo
        self.emit("running", self._files[0])
        tipo = MAGIC.file(self._files[0])
        self.cancelar.set_sensitive(True)
        self._codecsprogress = {}
        for check in self._checks:
            check.set_sensitive(False)
        self.start.set_sensitive(False)
        for codec in self._converters.keys():
            self._codecsprogress[codec] = 0.0

            # Evitar sobreescritura de archivo origen. Directorios de origen y destino deben ser distintos
            if os.path.dirname(self._files[0]) == self._dirOut:
                warning = "%s => Directorios de origen y destino son el mismo.\n" % (self._files[0])
                self.emit('warning', warning)
                continue

            if "audio" in tipo and codec in self.__videoCodecs:
                warning = "Codec: %s Formato: %s %s => El origen no tiene video.\n" % (codec, tipo, self._files[0])
                self.emit('warning', warning)
                continue

            if not "audio" in tipo and not "video" in tipo:
                warning = "Codec: %s Formato: %s %s => El origen no tiene ni audio ni video.\n" % (codec, tipo, self._files[0])
                self.emit('warning', warning)
                continue

            self._converters[codec] = Converter(self._files[0], codec, self._dirOut)
            # Cada instancia de Converter estará conectada a estas funciones
            self._converters[codec].connect('progress', self.__updateProgress)
            self._converters[codec].connect('error', self.__error)
            #self._converters[codec].connect('info', self.__info) FIXME: Distinto a lo que se emite al comenzar a correr el pipe
            self._converters[codec].connect('end', self.__next)

        # si no hay converts no hay tareas pendientes porque ahora se pueden saltear los codecs configurados
        if not any(self._converters.values()):
            self.__next(None)
        else:
            info = "Contenido del Archivo: %s" % tipo
            self.emit('info', info)
            for convert in self._converters.values():
                if convert:
                    convert.play()
        
    def __updateProgress(self, convert, val1, codec):
        self._codecsprogress[codec] = val1
        progreso = 0
        for _val in self._codecsprogress.values():
            progreso += _val
        progreso = progreso / len(self._converters.keys())
        totalesperado = self._initialFilesCount * 100.0
        totalterminado = ((self._initialFilesCount - len(self._files))) * 100.0 + progreso
        val2 = (totalterminado * 100.0 / totalesperado ) / 100.0
        self._progress[codec].set_fraction(float(val1/100.0))
        self._progressbar.set_fraction(val2)

    def __error(self, convert, error):
        self.emit("error", error)  # FIXME: Agregar codec ?
        self.__next(convert)

    #def __info(self, convert, info):
    #    self.emit('info', info) FIXME: Distinto a lo que se emite al comenzar a correr el pipe

    def __next(self, convert):
        # Va quitando los converters a medida que terminan y cuando no quedan más pasa el siguiente archivo
        if convert:
            origen, tipo, codec = convert.getInfo()
            del(self._converters[codec])
            self._converters[codec] = None
            if any(self._converters.values()): return False  # Esperamos que terminen todos los procesos de este archivo

        # Todas las tareas de este archivo terminaron o fallaron
        if self._files: self._files.remove(self._files[0])
        # Continuar con siguiente archivo o terminar
        if self._files:
            self.run()
        else:
            self.__end_all()

    def __end_all(self):
        self._progressbar.set_fraction(0.0)
        for progress in self._progress.values():
            progress.set_fraction(0.0)
        for check in self._checks:
            check.set_sensitive(True)
        self.start.set_sensitive(True)
        self.cancelar.set_sensitive(False)
        self._files = self._inicial_files.copy()
        self.emit('end')
        