# -*- coding: utf-8 -*-

import os
from gi.repository import GObject

from JAMediaPlayer.Globales import Reports
from JAMediaPlayer.Globales import set_dict


class InformeDescargas(GObject.Object):

    __gsignals__ = {"info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self):

        GObject.Object.__init__(self)

        self.__filename = "DESCARGAS.json"

        self.__data = {
            'cancelados en metadatos': [],
            'cancelados en descargas': []
        }

    def setInfo(self, key, val):
        if key in self.__data.keys():
            self.__data[key].append(val)
            self.emit("info", self.__data)
            try:
                filepath = os.path.join(Reports, self.__filename)
                set_dict(filepath, self.__data)
            except:
                pass
