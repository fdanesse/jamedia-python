# -*- coding: utf-8 -*-

import os
import time
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

from JAMediaConverter.Gstreamer.Converter import Converter

HOME = os.environ['HOME']


class AudioFrame(Gtk.Frame):

    __gsignals__ = {
        "end": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, []),
        "running": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
        "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "error": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self._codecs = []
        self._codecsprogress = {}  # Progreso de cada codec
        self._inicial_files = []
        self._files = []
        self._converters = [None, None, None, None, None]
        self._dirOut = HOME
        self._initialFilesCount = 0
        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_show_text(True)
        self._progressbar.get_style_context().add_class("convertprogress")
        self._checks = []

        self._progress = {"ogg":None, "mp3":None, "wav":None, "ogv":None, "webm":None}

        self.set_label(" Elige los formatos de extracción: ")

        table = Gtk.Table(rows=7, columns=12, homogeneous=False)
        table.set_col_spacings(0)
        table.set_row_spacing(row=4, spacing=15)
        row = 0
        for formato in sorted(self._progress.keys()):
            # http://python-gtk-3-tutorial.readthedocs.io/en/latest/button_widgets.html
            check = Gtk.CheckButton(formato)
            check.get_style_context().add_class("convertcheck")
            self._checks.append(check)
            progress = Gtk.ProgressBar()
            progress.set_show_text(True)
            progress.get_style_context().add_class("convertprogress")
            # http://www.mono-project.com/docs/gui/gtksharp/widgets/packing-with-tables/
            table.attach(check, 0, 1, row, row+1,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
            table.attach(progress, 1, 12, row, row+1,
                Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                Gtk.AttachOptions.EXPAND, 0, 0)
            row += 1
            check.connect("toggled", self.__toggledButton)
            self._progress[formato] = progress

        frame = Gtk.Frame()
        frame.set_label(' Total: ')
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.add(self._progressbar)
        table.attach(frame, 0, 12, 5, 6,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.start = Gtk.Button('Convertir')
        self.start.set_css_name('startbutton')
        self.start.set_name('startbutton')
        self.start.set_sensitive(False)
        table.attach(self.start, 0, 5, 6, 7,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.add(table)
        self.show_all()

    def set_files(self, _files):
        self._files = []
        for f in _files:
            self._files.append(f[1])
        self._inicial_files = self._files.copy()
        self._initialFilesCount = len(self._files)
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))
        # FIXME: Que los check se activen según los tipos de archivos que se carguen ?

    def __toggledButton(self, widget):
        if widget.get_active():
            if not widget.get_label() in self._codecs:
                self._codecs.append(widget.get_label())
        else:
            self._codecs.remove(widget.get_label())
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))

    def run(self, widget=None):
        # Se ejecuta para iniciar todas las conversiones de cada archivo
        self.emit("running", self._files[0])
        self._codecsprogress = {}
        for check in self._checks:
            check.set_sensitive(False)
        self.start.set_sensitive(False)
        for codec in self._codecs:
            self._codecsprogress[codec] = 0.0
            index = self._codecs.index(codec)
            # FIXME: Parece necesarios armar un Convert único, es demasiado reproducir el archivo para cada conversión al mismo tiempo
            self._converters[index] = Converter(self._files[0], codec, self._dirOut)
            # NOTA: Cada instancia de Converter estará conectada a estas funciones
            self._converters[index].connect('progress', self.__progress)
            self._converters[index].connect('error', self.__error)
            self._converters[index].connect('info', self.__info)
            self._converters[index].connect('end', self.__next)
        for convert in self._converters:
            if convert:
                time.sleep(0.5)
                #GLib.idle_add(convert.play)
                convert.play()
        
    def __progress(self, convert, val, codec):
        GLib.idle_add(self._progress[codec].set_fraction, float(val/100.0))
        self._codecsprogress[codec] = val
        progreso = 0
        for val in self._codecsprogress.values():
            progreso += val
        progreso = progreso / len(self._codecs)
        totalesperado = self._initialFilesCount * 100.0
        totalterminado = ((self._initialFilesCount - len(self._files))) * 100.0 + progreso
        n = (totalterminado * 100.0 / totalesperado ) / 100.0
        GLib.idle_add(self._progressbar.set_fraction, n)

    def __error(self, convert, error):
        if os.path.exists(convert._newpath):
            statinfo = os.stat(convert._newpath)
            if not statinfo.st_size:
                os.remove(convert._newpath)
        self.emit("error", error)  # FIXME: Agregar codec ?
        self.__next(convert)

    def __info(self, convert, info):
        # NOTA: Recordar que esta señal se recibe mas de una vez por archivo con diferentes datos
        self.emit('info', info)

    def __next(self, convert):
        # Va quitando los converters a medida que terminan y cuando no quedan más pasa el siguiente archivo
        index = self._converters.index(convert)
        convert.disconnect_by_func(self.__progress)
        convert.disconnect_by_func(self.__error)
        convert.disconnect_by_func(self.__info)
        convert.disconnect_by_func(self.__next)
        self._converters[index] = None
        convert.stop()
        convert = None
        del(convert)
        for convert in self._converters:
            if convert:
                return False
        if self._files:
            self._files.remove(self._files[0])
            if self._files:
                self.run()
            else:
                self.__end_all()
        else:
            self.__end_all()

    def __end_all(self):
        self._progressbar.set_fraction(0.0)
        for progress in self._progress.values():
            progress.set_fraction(0.0)
        for check in self._checks:
            check.set_sensitive(True)
        self.start.set_sensitive(True)
        self._files = self._inicial_files.copy()
        self.emit('end')
        