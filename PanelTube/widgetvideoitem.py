# -*- coding: utf-8 -*-

import os
import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

import urllib
#import base64
import subprocess

youtubedl = os.path.join(os.path.dirname(__file__), "youtube-dl")  #"/usr/bin/youtube-dl"


class WidgetVideoItem(Gtk.EventBox):

    __gsignals__ = {
    "end-update": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
    }

    def __init__(self, videodict):

        Gtk.EventBox.__init__(self)

        self.set_css_name('videoitem')
        self.set_name('videoitem')
        
        self._temp_dat = []
        self.videodict = videodict

        hbox = Gtk.HBox()
        hbox.set_css_name('videoitemHB')
        hbox.set_name('videoitemHB')
        self.imagen = Gtk.Image()
        hbox.pack_start(self.imagen, False, False, 3)
        
        self.id_label = Gtk.Label("%s: %s" % ("id", self.videodict["id"]))
        self.id_titulo = Gtk.Label("%s: %s" % ("Título", self.videodict["titulo"]))
        self.id_duracion = Gtk.Label("%s: %s" % ("Duración", self.videodict["duracion"]))
        self.id_url = Gtk.Label("%s: %s" % ("url", self.videodict["url"]))

        vbox = Gtk.VBox()
        vbox.pack_start(self.id_label, True, True, 0)
        vbox.pack_start(self.id_titulo, True, True, 0)
        vbox.pack_start(self.id_duracion, True, True, 0)
        vbox.pack_start(self.id_url, True, True, 0)

        for label in vbox.get_children():
            label.set_alignment(0.0, 0.5)

        hbox.pack_start(vbox, False, False, 5)
        self.add(hbox)

        self.show_all()

    def __get_progress(self, salida, STDOUT, process, error, STERR):
        progress = salida.readline().strip()
        err = error.readline().strip()
        if err:
            print ("Error al actualizar metadatos de:", self.videodict["url"], err)
            # FIXME: Cuando el usuario ingresa mal una dirección: en err viene: is not a valid URL
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
        GLib.timeout_add(100, self.__update)

    def __update(self):
        if self.videodict.get("previews", False):
            # 1 lista con 1 url
            if self.videodict["previews"]:
                url = self.videodict["previews"][0]
            archivo = "/tmp/preview%s" % self.videodict["id"]
            try:
                # FIXME: Porque Falla si no hay Conexión.
                fileimage, headers = urllib.request.urlretrieve(url, archivo)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(fileimage, 200, 150)
                self.imagen.set_from_pixbuf(pixbuf)
                # NOTA: Convertir imagen a string por si se quiere guardar.
                '''pixbuf_file = open(fileimage, 'rb')
                image_string = base64.b64encode(pixbuf_file.read())
                pixbuf_file.close()
                self.videodict["previews"] = image_string'''
                self.videodict["previews"] = pixbuf
            except:
                #FIXME: Verificar que sucede si no hay conexión
                print ("ERROR: Quizas no hay conexión", self.__update)
            if os.path.exists(archivo):
                os.remove(archivo)
        self.id_label.set_text("%s: %s" % ("id", self.videodict["id"]))
        self.id_titulo.set_text("%s: %s" % ("Título", self.videodict["titulo"]))
        self.id_duracion.set_text("%s: %s" % ("Duración", self.videodict["duracion"]))
        self.id_url.set_text("%s: %s" % ("url", self.videodict["url"]))
        return False

    def update(self):
        # NOTA: desde PanelTube
        _url = self.videodict["url"]
        STDOUT = "/tmp/jamediatube-dl%s" % self.videodict["id"]
        STERR = "/tmp/jamediatube-dlERR%s" % self.videodict["id"]
        estructura = "python %s -s -e --get-thumbnail --get-duration %s" % (youtubedl, _url)
        process = subprocess.Popen(estructura, shell=True, stdout=open(STDOUT, "w+b"), stderr=open(STERR, "w+b"), universal_newlines=True)
        salida = open(STDOUT, "r")
        error = open(STERR, "r")
        self.connect("end-update", self.__run_update)
        GLib.timeout_add(100, self.__get_progress, salida, STDOUT, process, error, STERR)
