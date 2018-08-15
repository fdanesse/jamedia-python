# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

from JAMediaConverter.Gstreamer.Converter import Converter

HOME = os.environ['HOME']


class AudioFrame(Gtk.Frame):

    __gsignals__ = {"end": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self._codecs = []
        self._codecsprogress = {}  # Progreso de cada codec
        self._files = []
        self._converters = [None, None, None]
        self._dirOut = HOME
        self._initialFilesCount = 0
        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_show_text(True)
        self._progressbar.get_style_context().add_class("convertprogress")
        self._checks = []

        self._progress = {"ogg":None, "mp3":None, "wav":None}

        self.set_label(" Elige los formatos de extracción: ")

        table = Gtk.Table(rows=5, columns=12, homogeneous=False)
        table.set_col_spacings(0)
        table.set_row_spacing(row=2, spacing=15)
        row = 0
        for formato in sorted(self._progress.keys()):
            # http://python-gtk-3-tutorial.readthedocs.io/en/latest/button_widgets.html
            check = Gtk.CheckButton(formato)
            check.get_style_context().add_class("convertcheck")
            if formato != "mp3": check.set_sensitive(False)
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
        table.attach(frame, 0, 12, 3, 4,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.start = Gtk.Button('Convertir')
        self.start.set_css_name('startbutton')
        self.start.set_name('startbutton')
        self.start.set_sensitive(False)
        table.attach(self.start, 0, 5, 4, 5,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.add(table)
        self.show_all()

    def set_files(self, _files):
        self._files = []
        for f in _files:
            self._files.append(f[1])
        self._initialFilesCount = len(self._files)
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))
        # FIXME: Que los check se activen según los tipos de archivos que se carguen

    def __toggledButton(self, widget):
        if widget.get_active():
            if not widget.get_label() in self._codecs:
                self._codecs.append(widget.get_label())
        else:
            self._codecs.remove(widget.get_label())
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))

    def run(self, widget=None):
        # Se ejecuta para iniciar todas las conversiones de cada archivo
        # FIXME: Informar de archivo en proceso
        self._codecsprogress = {}
        for check in self._checks:
            check.set_sensitive(False)
        self.start.set_sensitive(False)
        for codec in self._codecs:
            self._codecsprogress[codec] = 0.0
            index = self._codecs.index(codec)
            self._converters[index] = Converter(self._files[0], codec, self._dirOut)
            self._converters[index].connect('progress', self.__progress)
            self._converters[index].connect('error', self.__error)
            self._converters[index].connect('info', self.__info)
            self._converters[index].connect('end', self.__end)
        for convert in self._converters:
            if convert:
                GLib.idle_add(convert.play)

    def __progress(self, convert, val, codec):
        # NOTA: Cada instancia de Converter está conectada a esta función
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
        # NOTA: Cada instancia de Converter está conectada a esta función
        print("FIXME: ERROR: ", self.__error, error)
        self.__next(convert)

    def __info(self, convert, info):
        # NOTA: Cada instancia de Converter está conectada a esta función
        # FIXME: 'INFO', convert, info
        pass

    def __end(self, convert):
        # NOTA: Cada instancia de Converter está conectada a esta función
        self.__next(convert)

    def __next(self, convert):
        # Va quitando los converters a medida que terminan y cuando no quedan más pasa el siguiente archivo
        index = self._converters.index(convert)
        self._converters[index].disconnect_by_func(self.__progress)
        self._converters[index].disconnect_by_func(self.__error)
        self._converters[index].disconnect_by_func(self.__info)
        self._converters[index].disconnect_by_func(self.__end)
        GLib.idle_add(self._converters[index].free)
        self._converters[index] = None
        #convert.destroy()
        for convert in self._converters:
            if convert:
                # Para esperar a que terminen todas las conversiones de este archivo
                return
        if self._files:
            self._files.remove(self._files[0])
            if self._files:
                self.run()
            else:
                self.__end_all()
        else:
            self.__end_all()

    def __end_all(self):
        # http://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html
        self._progressbar.set_fraction(0.0)
        for progress in self._progress.values():
            progress.set_fraction(0.0)
        for check in self._checks:
            check.set_sensitive(True)
        self.start.set_sensitive(False)
        self.emit('end')
        