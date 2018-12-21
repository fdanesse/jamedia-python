# -*- coding: utf-8 -*-

import os
import subprocess
import time
import datetime

import gi
gi.require_version("Gst", "1.0")

from gi.repository import GObject
from gi.repository import GLib
from gi.repository import Gst

from JAMediaPlayer.Globales import MAGIC
from JAMediaConverter.Gstreamer.VideoPipelines.InformeTranscoderModel import InformeTranscoderModel
#from JAMediaConverter.Gstreamer.Globales import format_ns, getSize

GObject.threads_init()
Gst.init(None)


class Converter(GObject.Object):

    __gsignals__ = {
    "progress": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_FLOAT, GObject.TYPE_STRING)),
    "error": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_STRING,)),
    #"info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)), FIXME: Ver audioFrame
    "end": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, [])
    }

    def __init__(self, origen, codec, dirout):

        GObject.Object.__init__(self)

        self.__codec = codec
        self.__origen = origen

        # FIXME: Implementar limpieza del nombre del archivo
        location = os.path.basename(origen)
        informeName = location
        if "." in location:
            extension = ".%s" % origen.split(".")[-1]
            informeName = location.replace(extension, "")
            location = location.replace(extension, ".%s" % codec)
        else:
            location = "%s.%s" % (location, codec)
        destino = os.path.join(dirout, location.replace(" ", "_"))

        self.__tipo = MAGIC.file(origen)
        #self.__status = Gst.State.NULL
        self.__t1 = None
        self.__t2 = None
        self.__timeProcess = None
        self.__informeModel = InformeTranscoderModel(self.__codec + "-" + informeName)
        #self.__informeModel.connect("info", self.__emit_info) FIXME: Ver audioFrame

        self.__STDOUT = None #"/tmp/jamediaconverter%d" % time.time()
        self.__estructura = "gst-transcoder-1.0 %s %s %s" % (Gst.filename_to_uri(origen), Gst.filename_to_uri(destino), codec)
        self.__process = None
        self.__salida = None
        self.__controller = None
        self.__position = 0

    #def __emit_info(self, informemodel, info):
    #    self.emit("info", info) FIXME: Ver audioFrame

    def __informar(self):
        self.__informeModel.setInfo("archivo", self.__origen)
        self.__informeModel.setInfo("codec",self.__codec)
        self.__informeModel.setInfo("formato inicial", self.__tipo)
        # FIXME: Requiere otro enfoque
        '''
        pad = self.__pipe.emit('get-video-pad',0)
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('video/'):
                self.__informeModel.setInfo("entrada de video", currentcaps)           
                width, height = getSize(currentcaps)
                self.__informeModel.setInfo("relacion", float(width)/float(height))
        pad = self.__pipe.emit('get-audio-pad',0) 
        if pad:
            currentcaps = pad.get_current_caps().to_string()
            if currentcaps.startswith('audio/'):
                self.__informeModel.setInfo("entrada de sonido", currentcaps)
        '''

    def __new_handle(self, reset):
        if self.__controller:
            GLib.source_remove(self.__controller)
            self.__controller = False
        if reset:
            self.__controller = GLib.timeout_add(200, self.__handler)

    def play(self):
        self.__informar()
        self.__t1 = datetime.datetime.now()
        self.__STDOUT = "/tmp/jamediaconverter%d" % time.time()
        time.sleep(1) # Fuerza espera para que otros converters no sobreescriban esta salida.
        self.__process = subprocess.Popen(self.__estructura, shell=True, stdout=open(self.__STDOUT, "w+b"), stderr=open(self.__STDOUT, "w+b"), universal_newlines=True)
        self.__salida = open(self.__STDOUT, "r")
        self.__new_handle(True)
        
    def __handler(self):
        progress = self.__salida.readline().replace("\n", ""))
        '''if "Starting transcoding..." in progress:
            self.__informar()
            self.__t1 = datetime.datetime.now()'''
        if "DONE." in progress:
            self.stop()
            return False
        elif "FAILURE" in progress:
            self.__informeModel.setInfo('errores', progress
            self.stop()
            self.emit("error", "ERROR en: " + self.__origen + "No se pudo convertir a: " + self.__codec + ' => ' + progress)           
            return False

        # 0:00:00.0 / 0:26:14.8
        data = progress.strip().split("/")
        if len(data) == 2:
            num1, num2 = data
            if "." in num1: num1 = num1.split(".")[0]
            if "." in num2: num2 = num2.split(".")[0]

            # Tiempo a segundos usando timedelta
            vacio = datetime.datetime.strptime("0:00:00", "%H:%M:%S")
            procesado = datetime.datetime.strptime("0:00:00", "%H:%M:%S")
            duracion = datetime.datetime.strptime("0:59:00", "%H:%M:%S")
            try:
                procesado = (datetime.datetime.strptime(num1.strip(), "%H:%M:%S") - vacio).seconds
            except:
                pass
            try:
                duracion = (datetime.datetime.strptime(num2.strip(), "%H:%M:%S") - vacio).seconds
            except:
                pass
            pos = 0
            try:
                pos = int(float(procesado) * 100 / float(duracion))
            except:
                pass
            if pos != self.__position:
                self.__position = pos
                self.emit("progress", self.__position, self.__codec)

        return True

    def stop(self):
        self.__t2 = datetime.datetime.now()
        self.__timeProcess = self.__t2 - self.__t1
        self.__informeModel.setInfo('tiempo de proceso', str(self.__timeProcess))
        self.__new_handle(False)
        self.__process.kill()
        if self.__salida: self.__salida.close()
        if os.path.exists(self.__STDOUT): os.unlink(self.__STDOUT)
        self.emit("end")

    def getInfo(self):
        return self.__origen, self.__tipo, self.__codec
