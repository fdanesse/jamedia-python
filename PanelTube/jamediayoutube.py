# -*- coding: utf-8 -*-

# http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs

import os
import time
import subprocess

from gi.repository import GLib
from gi.repository import GObject

from JAMediaPlayer.Globales import get_tube_directory

BASE_PATH = os.path.dirname(__file__)
#STDERR = "/dev/null"
youtubedl = "/usr/bin/youtube-dl" #os.path.join(BASE_PATH, "youtube-dl") #"/usr/bin/youtube-dl"

CODECS = [
    [43, "WebM", "360p VP8 N/A 0.5 Vorbis 128"],
    [5, "FLV", "240p Sorenson H.263    N/A    0.25 MP3 64"],
    [18, "MP4", "270p/360p H.264 Baseline 0.5 AAC 96"],
    [82, "MP4", "360p H.264 3D 0.5 AAC 96"],
    ]


class JAMediaYoutube(GObject.GObject):

    __gsignals__ = {
    'progress_download': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, ))}

    def __init__(self):

        GObject.GObject.__init__(self)

        self.ultimosdatos = False
        self.contador = 0
        self.datos_originales = [False, False]

        self.url = False
        self.titulo = False
        self.estado = False

        self.youtubedl = False
        self.salida = False
        self.actualizador = False
        self.STDOUT = False

        self.codec = 0

    def __get_titulo(self, titulo):
        texto = ""
        excluir = ["\\", "/", ",", ".", "&",
        "¿", "?", "@", "#", "$", "\'", ":", ";", "|",
        "!", "¡", "%", "+", "*", "ª", "º", "~", "{",
        "}", "Ç", "[", "]", "^", "`", "=", "¬", "\""]
        for l in titulo:
            if not l in excluir:
                texto += l
        return str(texto).replace(" ", "_")

    def __get_progress(self):
        progress = self.salida.readline()
        if progress:
            if "100.0%" in progress.split():
                self.estado = False
            self.emit("progress_download", progress)

        # control switch codec.
        if self.ultimosdatos != progress:
            self.ultimosdatos = progress
            self.contador = 0
        else:
            self.contador += 1

        if self.contador > 15:
            if self.codec + 1 < len(CODECS):
                self.end()
                self.codec += 1
                url, titulo = self.datos_originales
                self.download(url, titulo)
        return self.estado

    def download(self, url, titulo):
        self.datos_originales = [url, titulo]

        self.ultimosdatos = False
        self.contador = 0

        #print "Intentando Descargar:", titulo
        #print "\t En Formato:", CODECS[self.codec]

        self.estado = True
        # http://youtu.be/XWDZMMMbvhA => codigo compartir
        # url del video => 'http://www.youtube.com/watch?v=XWDZMMMbvhA'
        # FIXME: HACK: 5 de octubre 2012
        #self.url = url # https://youtu.be/wgdbZhnFD5g #https://www.youtube.com/watch?t=187&v=wgdbZhnFD5g
        #self.url = "http://youtu.be/" + url.split(
        #    "http://www.youtube.com/watch?v=")[1]
        self.url = "http://youtu.be/" + url.split("=")[1]
        self.titulo = self.__get_titulo(titulo)
        self.STDOUT = "/tmp/jamediatube%d" % time.time()

        archivo = "%s%s%s" % ("\"", self.titulo, "\"")
        destino = os.path.join(get_tube_directory(), archivo)

        estructura = "python %s %s -i -R %s -f %s --no-part -o %s" % (youtubedl, self.url, 1, CODECS[self.codec][0], destino)

        self.youtubedl = subprocess.Popen(estructura, shell=True,stdout=open(self.STDOUT, "w+b"), universal_newlines=True)  #=open(self.STDOUT, "r+b"), 

        self.salida = open(self.STDOUT, "r")

        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False

        self.actualizador = GLib.timeout_add(500, self.__get_progress)

    def reset(self):
        self.end()
        self.codec = 0

    def end(self):
        if self.actualizador:
            GLib.source_remove(self.actualizador)
            self.actualizador = False
        self.youtubedl.kill()
        if self.salida:
            self.salida.close()
        if os.path.exists(self.STDOUT):
            os.unlink(self.STDOUT)
        self.estado = False
