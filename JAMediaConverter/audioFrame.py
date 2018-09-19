# -*- coding: utf-8 -*-

import os
import time
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GObject

from JAMediaConverter.Gstreamer.Converter import Converter
from JAMediaPlayer.Globales import MAGIC

HOME = os.environ['HOME']


class AudioFrame(Gtk.Frame):

    __gsignals__ = {
        "end": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, []),
        "running": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
        "info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "warning": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
        "error": (GObject.SIGNAL_RUN_FIRST,GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        Gtk.Frame.__init__(self)

        self._codecs = []
        self._codecsprogress = {}  # Progreso de cada codec
        self._inicial_files = []
        self._files = []
        self._converters = [None, None, None, None, None, None, None, None, None]
        self._dirOut = HOME
        self._initialFilesCount = 0
        self._progressbar = Gtk.ProgressBar()
        self._progressbar.set_show_text(True)
        self._progressbar.get_style_context().add_class("convertprogress")
        self._checks = []

        self.__videoCodecs = ["ogv", "webm", "mp4", "avi", "mpg", "png"]
        self._progress = {"ogg":None, "mp3":None, "wav":None, "ogv":None, "webm":None, "mp4":None, "avi":None, "mpg":None, "png":None}

        self.set_label(" Elige los formatos de extracción: ")

        table = Gtk.Table(rows=11, columns=12, homogeneous=False)
        table.set_col_spacings(0)
        table.set_row_spacing(row=8, spacing=15)
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
        table.attach(frame, 0, 12, 9, 10,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL,
            Gtk.AttachOptions.SHRINK | Gtk.AttachOptions.FILL, 0, 0)

        self.start = Gtk.Button('Convertir')
        self.start.set_css_name('startbutton')
        self.start.set_name('startbutton')
        self.start.set_sensitive(False)
        table.attach(self.start, 0, 5, 10, 11,
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

            tipo = MAGIC.file(self._files[0])
            info = "Contenido del Archivo: %s" % tipo
            print("Codeando:", codec, tipo, self._files[0])
            self.emit('info', info)

            # Evitar sobreescritura de archivo origen. Directorios de origen y destino deben ser distintos
            if os.path.dirname(self._files[0]) == self._dirOut:
                self._converters[index] = None
                warning = "%s => Salteado porque directorios de origen y destino son el mismo.\n" % (self._files[0])
                self.emit('warning', warning)
                continue
            # Si el archivo sólo contiene audio, no se crearán converts de video o imágenes
            if "audio" in tipo and codec in self.__videoCodecs:
                self._converters[index] = None
                warning = "%s => Salteando porque el origen no tiene video.\n" % (self._files[0])
                self.emit('warning', warning)
                continue
            # FIXME: Implementar continue para archivos que no tienen ni video ni audio

            # FIXME: Parece necesarios armar un Convert único, es demasiado reproducir el archivo para cada conversión al mismo tiempo
            self._converters[index] = Converter(self._files[0], codec, self._dirOut)
            # Cada instancia de Converter estará conectada a estas funciones
            self._converters[index].connect('progress', self.__updateProgress)
            self._converters[index].connect('error', self.__error)
            self._converters[index].connect('info', self.__info)
            self._converters[index].connect('end', self.__next)

        # si no hay converts no hay tareas pendientes porque ahora se pueden saltear los codecs configurados
        if not any(self._converters):
            self.__next(None)
        else:
            for convert in self._converters:
                if convert:
                    # Esto no debiera ser necesario
                    time.sleep(0.5)
                    convert.play()
        
    def __updateProgress(self, convert, val1, codec):
        Gdk.threads_enter()
        self._codecsprogress[codec] = val1
        progreso = 0
        for _val in self._codecsprogress.values():
            progreso += _val
        progreso = progreso / len(self._codecs)
        totalesperado = self._initialFilesCount * 100.0
        totalterminado = ((self._initialFilesCount - len(self._files))) * 100.0 + progreso
        val2 = (totalterminado * 100.0 / totalesperado ) / 100.0
        self._progress[codec].set_fraction(float(val1/100.0))
        self._progressbar.set_fraction(val2)
        Gdk.threads_leave()

    def __error(self, convert, error):
        if os.path.exists(convert._newpath):
            statinfo = os.stat(convert._newpath)
            if not statinfo.st_size:
                os.remove(convert._newpath)
        self.emit("error", error)  # FIXME: Agregar codec ?
        self.__next(convert)

    def __info(self, convert, info):
        # Recordar que esta señal se recibe mas de una vez por archivo con diferentes datos
        self.emit('info', info)

    def __next(self, convert):
        # Va quitando los converters a medida que terminan y cuando no quedan más pasa el siguiente archivo
        if convert:
            index = self._converters.index(convert)
            # Esto no debiera ser necesario
            convert.disconnect_by_func(self.__updateProgress)
            convert.disconnect_by_func(self.__error)
            convert.disconnect_by_func(self.__info)
            convert.disconnect_by_func(self.__next)
            convert.stop()
            # convert = None
            # Esto no debiera ser necesario
            del(convert)
            self._converters[index] = None
            if any(self._converters): return False  # Esperamos que terminen todos los procesos de este archivo
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
        self._files = self._inicial_files.copy()
        self.emit('end')
        