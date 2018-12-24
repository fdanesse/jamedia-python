# -*- coding: utf-8 -*-

import os
import json
from time import sleep
from random import random

from libs import magic
MAGIC = magic.open(magic.MAGIC_MIME)  #MAGIC_NONE
MAGIC.load()

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GdkPixbuf

ICONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Iconos")
JAMediaDatos = os.path.join(os.environ["HOME"], "JAMediaDatos")
Reports = os.path.join(JAMediaDatos, "Reports")
YoutubeDir = os.path.join(JAMediaDatos, "YoutubeVideos")

if not os.path.exists(JAMediaDatos):
    os.mkdir(JAMediaDatos)
if not os.path.exists(Reports):
    os.mkdir(Reports)
if not os.path.exists(YoutubeDir):
    os.mkdir(YoutubeDir)
    # os.chmod(YoutubeDir, stat.S_IXOTH)
for _file in os.listdir(Reports):
    arch = os.path.join(Reports, _file)
    os.remove(arch)


def json_file(path, data=None, delay=0.1):
    while True:
        try:
            if data == None:
                with open(path, "r") as f:  #, encoding="utf-8"
                    return json.loads(f)
            else:
                with open(path, "w") as f:  #, encoding="utf-8"
                    return json.dump(data, f)  #sort_keys=True, separators=(',', ':'), indent=4, skipkeys=False, ensure_ascii=False
        except:
            sleep(random()*delay) # concurrency

def ocultar(objetos):
    for objeto in objetos:
        if objeto.get_visible():
            objeto.hide()

def mostrar(objetos):
    for objeto in objetos:
        if not objeto.get_visible():
            objeto.show()

def sensibilizar(objetos):
    for objeto in objetos:
        if not objeto.get_sensitive():
            objeto.set_sensitive(True)

def insensibilizar(objetos):
    for objeto in objetos:
        if objeto.get_sensitive():
            objeto.set_sensitive(False)

def get_dict(path):
    import json
    if not os.path.exists(path): return {}
    archivo = open(path, "r")
    _dict = json.loads(archivo.read())
    archivo.close()
    return _dict

def get_separador(draw=False, ancho=0, expand=False):
    separador = Gtk.SeparatorToolItem()
    separador.props.draw = draw
    separador.set_size_request(ancho, -1)
    separador.set_expand(expand)
    return separador

def get_boton(archivo, flip=False, rotacion=None, pixels=24, tooltip_text=None):
    boton = Gtk.ToolButton()
    imagen = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(archivo, pixels, pixels)
    if flip: pixbuf = pixbuf.flip(True)
    if rotacion: pixbuf = pixbuf.rotate_simple(rotacion)
    imagen.set_from_pixbuf(pixbuf)
    boton.set_icon_widget(imagen)
    imagen.show()
    boton.show()
    if tooltip_text:
        boton.set_tooltip_text(tooltip_text)
        boton.TOOLTIP = tooltip_text
    return boton

def get_toggle_boton(archivo, flip=False, rotacion=None, pixels=24, tooltip_text=None):
    boton = Gtk.ToggleToolButton()
    imagen = Gtk.Image()
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(archivo, pixels, pixels)
    if flip: pixbuf = pixbuf.flip(True)
    if rotacion: pixbuf = pixbuf.rotate_simple(rotacion)
    imagen.set_from_pixbuf(pixbuf)
    boton.set_icon_widget(imagen)
    imagen.show()
    boton.show()
    if tooltip_text:
        boton.set_tooltip_text(tooltip_text)
        boton.TOOLTIP = tooltip_text
    return boton
    
def clear_Dir(_dir, removedirs):
    _dirs = []
    for (archiveDirPath, dirNames, fileNames) in os.walk(_dir):
        # Directorio padre, directorios hijos, archivos en Directorio padre
        if removedirs:
            for _d in dirNames:
                n = os.path.realpath(os.path.join(archiveDirPath, _d))
                if not n in _dirs and n != _dir and n != os.path.realpath(os.environ["HOME"]): _dirs.append(n)
        # Borrando archivos vacíos
        for fileName in fileNames:
            file_path = os.path.realpath(os.path.join(archiveDirPath, fileName))
            try:
                if not os.stat(file_path).st_size: os.unlink(file_path)
            except:
                pass
    # Borrando directorios vacíos
    for _d in reversed(_dirs):
        try:             
            if _dir != _d and not os.listdir(_d): os.rmdir(_d)
        except:
            pass
