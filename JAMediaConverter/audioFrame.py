# -*- coding: utf-8 -*-

import os

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GObject

#from Gstreamer.Converter import Converter

HOME = os.environ['HOME']


class AudioFrame(Gtk.Frame):

    __gsignals__ = {"end": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, [])}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self._codecs = []
        self._files = []
        self._converters = [None, None, None]
        self._dirOut = HOME
        self._initialFilesCount = 0
        self._progressbar = Gtk.ProgressBar()
        self._checks = []

        self._progress = {"ogg":None, "mp3":None, "wav":None}

        self.set_label(" Elige los formatos de extracción: ")
        self.set_border_width(5)

        table = Gtk.Table(rows=5, columns=5, homogeneous=False)
        table.set_col_spacings(0)
        table.set_row_spacing(row=2, spacing=5)
        table.set_row_spacing(row=3, spacing=10)
        row = 0
        for formato in sorted(self._progress.keys()):
            # http://python-gtk-3-tutorial.readthedocs.io/en/latest/button_widgets.html
            check = Gtk.CheckButton(formato)
            self._checks.append(check)
            progress = Gtk.ProgressBar()
            # http://www.mono-project.com/docs/gui/gtksharp/widgets/packing-with-tables/
            table.attach(check, 0, 1, row, row+1,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
                Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)
            table.attach(progress, 1, 4, row, row+1,
                Gtk.AttachOptions.FILL | Gtk.AttachOptions.EXPAND,
                Gtk.AttachOptions.EXPAND, 0, 0)
            row += 1
            check.connect("toggled", self.__toggledButton)
            self._progress[formato] = progress

        frame = Gtk.Frame()
        frame.set_label(' Total: ')
        frame.set_border_width(5)
        event = Gtk.EventBox()
        event.set_border_width(5)
        event.add(self._progressbar)
        frame.add(event)
        table.attach(frame, 0, 4, 3, 4)

        self.start = Gtk.Button('Comenzar Extracción')
        self.start.set_sensitive(False)
        table.attach(self.start, 3, 4, 4, 5)
        event = Gtk.EventBox()
        event.set_border_width(5)
        event.add(table)

        self.add(event)
        self.show_all()

    '''def set_files(self, _files):
        self._files = _files
        self._initialFilesCount = len(self._files)
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))'''

    def __toggledButton(self, widget):
        if widget.get_active():
            if not widget.get_label() in self._codecs:
                self._codecs.append(widget.get_label())
        else:
            self._codecs.remove(widget.get_label())
        self.start.set_sensitive(bool(self._files) and bool(self._codecs))

    '''def run(self, widget=None):
        for check in self._checks:
            check.set_sensitive(False)
        _file = self._files[0]
        # FIXME: Informar de archivo en proceso
        for codec in self._codecs:
            index = self._codecs.index(codec)
            convert = Converter(_file, codec, self._dirOut)
            convert.connect('progress', self.__progress)
            convert.connect('error', self.__error)
            convert.connect('info', self.__info)
            convert.connect('end', self.__end)
            self._converters[index] = convert
        for convert in self._converters:
            if convert:
                convert.play()'''

    '''def __progress(self, convert, val, codec):
        self._progress[codec].set_fraction(val/100.0)
        # FIXME: Actualizar progress general
        # duration = self._initialFilesCount * codecs * 100.0
        # self._files * codecs * 100.0 = position
        dif = self._initialFilesCount - len(self._files)
        total = (dif) * 100 / self._initialFilesCount 
        self._progressbar.set_fraction(total/100.0)'''

    '''def __error(self, convert, error):
        dialog = Gtk.MessageDialog(self.get_toplevel(), 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "ERROR")
        dialog.format_secondary_text(error)
        dialog.run()
        dialog.destroy()
        self.__next(convert)'''

    '''def __info(self, convert, info):
        # FIXME: 'INFO', convert, info
        pass'''

    '''def __end(self, convert):
        self.__next(convert)'''

    '''def __next(self, convert):
        convert.disconnect_by_func(self.__progress)
        convert.disconnect_by_func(self.__error)
        convert.disconnect_by_func(self.__info)
        convert.disconnect_by_func(self.__end)
        index = self._converters.index(convert)
        self._converters[index] = None
        convert.free()
        convert.destroy()
        for convert in self._converters:
            if convert:
                # Esperamos que terminen todas
                # las conversiones para este archivo
                return
        if self._files:
            _file = self._files[0]
            self._files.remove(_file)
            if self._files:
                self.run()
            else:
                self.__dialogEnd()
        else:
            self.__dialogEnd()'''

    '''def __dialogEnd(self):
        # http://python-gtk-3-tutorial.readthedocs.io/en/latest/dialogs.html
        dialog = Gtk.MessageDialog(
            self.get_toplevel(), 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Tareas culminadas")
        dialog.format_secondary_text("Han culminado todas las tareas")
        dialog.set_border_width(15)
        dialog.run()
        dialog.destroy() # FIXME Warning: g_array_remove_range: assertion 'index_ + length <= array->len' failed
        self._progressbar.set_fraction(0.0)
        for progress in self._progress.values():
            progress.set_fraction(0.0)
        for check in self._checks:
            check.set_sensitive(True)
        self.emit('end')'''
        