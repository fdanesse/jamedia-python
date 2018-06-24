# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

import urllib
import base64
import subprocess

from PanelTube.jamediayoutube import JAMediaYoutube

from JAMediaPlayer.Globales import get_colors

BASE_PATH = os.path.dirname(os.path.dirname(__file__))
youtubedl = os.path.join(BASE_PATH, "youtube-dl")  #"/usr/bin/youtube-dl"


class WidgetVideoItem(Gtk.EventBox):

    __gsignals__ = {
    #"clicked": (GObject.SIGNAL_RUN_FIRST,
    #    GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),
    "end-update": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, []),
    "click_derecho": (GObject.SIGNAL_RUN_FIRST,
        GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self, videodict):

        Gtk.EventBox.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("widgetvideoitem1"))
        self.set_border_width(2)

        self._temp_dat = []
        self.videodict = videodict

        hbox = Gtk.HBox()
        vbox = Gtk.VBox()

        self.imagen = Gtk.Image()
        hbox.pack_start(self.imagen, False, False, 3)

        if self.videodict.get("previews", False):
            if type(self.videodict["previews"]) == list:
                # 1 lista con 1 url, o base64 en un archivo de busquedas.
                url = self.videodict["previews"][0]
                archivo = "/tmp/preview%s" % self.videodict["id"]
                try:
                    # FIXME: Porque Falla si no hay Conexión.
                    fileimage, headers = urllib.urlretrieve(url, archivo)
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                        fileimage, 200, 150)
                    self.imagen.set_from_pixbuf(pixbuf)
                    # Convertir imagen a string por si se quiere guardar.
                    pixbuf_file = open(fileimage, 'rb')
                    image_string = base64.b64encode(pixbuf_file.read())
                    pixbuf_file.close()
                    self.videodict["previews"] = image_string
                except:
                    print ("ERROR: Quizas no hay conexión", self.__init__)
                if os.path.exists(archivo):
                    os.remove(archivo)
            else:
                loader = Gtk.gdk.PixbufLoader()
                loader.set_size(200, 150)
                image_string = base64.b64decode(self.videodict["previews"])
                loader.write(image_string)
                loader.close()
                pixbuf = loader.get_pixbuf()
                self.imagen.set_from_pixbuf(pixbuf)

        self.id_label = Gtk.Label("%s: %s" % ("id", self.videodict["id"]))
        self.id_titulo = Gtk.Label("%s: %s" % ("Título",
            self.videodict["titulo"]))
        self.id_categoria = Gtk.Label("%s: %s" % ("Categoría",
            self.videodict["categoria"]))
        self.id_duracion = Gtk.Label("%s: %s %s" % ("Duración",
            self.videodict["duracion"], "Minutos"))
        self.id_url = Gtk.Label("%s: %s" % ("url", self.videodict["url"]))

        vbox.pack_start(self.id_label, True, True, 0)
        vbox.pack_start(self.id_titulo, True, True, 0)
        vbox.pack_start(self.id_categoria, True, True, 0)
        vbox.pack_start(self.id_duracion, True, True, 0)
        vbox.pack_start(self.id_url, True, True, 0)

        for label in vbox.get_children():
            label.set_alignment(0.0, 0.5)

        hbox.pack_start(vbox, False, False, 5)
        self.add(hbox)

        self.show_all()
        self.connect("button_press_event", self.__button_press)

    def __button_press(self, widget, event):
        #self.modify_bg(Gtk.StateType.NORMAL, self.colorclicked)
        #if event.button == 1:
        #   self.emit("clicked", event)
        #elif event.button == 3:
        self.emit("click_derecho", event)

    def __get_progress(self, salida, STDOUT, process, error, STERR):
        """
        Lectura del subproceso que obtiene los metadatos del video.
        """

        progress = salida.readline().strip()
        err = error.readline().strip()
        # FIXME: Signature extraction failed: Traceback (most recent call last)
        if err:
            print ("Error al actualizar metadatos de:", self.videodict["url"], err)
            process.kill()
            for arch in [salida, error]:
                arch.close()
            for arch in [STDOUT, STERR]:
                if os.path.exists(arch):
                    os.unlink(arch)
            del(self._temp_dat)
            self.emit("end-update")
            return False
        if progress:
            self._temp_dat.append(progress)
        if len(self._temp_dat) == 3:
            self.videodict["titulo"] = self._temp_dat[0]
            self.videodict["previews"] = [self._temp_dat[1]]
            self.videodict["duracion"] = self._temp_dat[2]
            process.kill()
            for arch in [salida, error]:
                arch.close()
            for arch in [STDOUT, STERR]:
                if os.path.exists(arch):
                    os.unlink(arch)
            del(self._temp_dat)
            self.emit("end-update")
            return False
        return True

    def __run_update(self, widget):
        """
        Obtenidos todos los metadatos del video, se actualizan los widgets.
        """
        GLib.timeout_add(100, self.__update)

    def __update(self):
        """
        Obtenidos todos los metadatos del video, se actualizan los widgets.
        """
        while Gtk.events_pending():
            Gtk.main_iteration()
        if self.videodict.get("previews", False):
            # 1 lista con 1 url
            url = self.videodict["previews"][0]
            archivo = "/tmp/preview%s" % self.videodict["id"]
            try:
                # FIXME: Porque Falla si no hay Conexión.
                fileimage, headers = urllib.urlretrieve(url, archivo)
                while Gtk.events_pending():
                    Gtk.main_iteration()
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(
                    fileimage, 200, 150)
                self.imagen.set_from_pixbuf(pixbuf)
                while Gtk.events_pending():
                    Gtk.main_iteration()
                # Convertir imagen a string por si se quiere guardar.
                pixbuf_file = open(fileimage, 'rb')
                image_string = base64.b64encode(pixbuf_file.read())
                pixbuf_file.close()
                self.videodict["previews"] = image_string
            except:
                print ("ERROR: Quizas no hay conexión", self.update)
            if os.path.exists(archivo):
                os.remove(archivo)
        self.id_label.set_text("%s: %s" % ("id", self.videodict["id"]))
        self.id_titulo.set_text("%s: %s" % ("Título",
            self.videodict["titulo"]))
        self.id_categoria.set_text("%s: %s" % ("Categoría",
            self.videodict["categoria"]))
        self.id_duracion.set_text("%s: %s %s" % ("Duración",
            self.videodict["duracion"], "Minutos"))
        self.id_url.set_text("%s: %s" % ("url", self.videodict["url"]))
        while Gtk.events_pending():
            Gtk.main_iteration()
        return False

    def update(self):
        """
        Luego de agregados todos los widgets de videos, cada uno actualiza sus
        previews y demás metadatos, utilizando un subproceso para no afectar a
        la interfaz gráfica.
        """
        _url = self.videodict["url"]
        STDOUT = "/tmp/jamediatube-dl%s" % self.videodict["id"]
        STERR = "/tmp/jamediatube-dlERR%s" % self.videodict["id"]
        estructura = "python %s -s -e --get-thumbnail --get-duration %s" % (youtubedl, _url)
        process = subprocess.Popen(estructura, shell=True,
            stdout=open(STDOUT, "w+b"), stderr=open(STERR, "w+b"),
            universal_newlines=True)
        salida = open(STDOUT, "r")
        error = open(STERR, "r")
        self.connect("end-update", self.__run_update)
        GLib.timeout_add(100, self.__get_progress, salida, STDOUT,
            process, error, STERR)
