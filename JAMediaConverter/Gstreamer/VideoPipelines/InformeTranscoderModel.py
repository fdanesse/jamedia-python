# -*- coding: utf-8 -*-

import os
from gi.repository import GObject

from JAMediaPlayer.Globales import Reports
from JAMediaPlayer.Globales import set_dict


class InformeTranscoderModel(GObject.Object):

    __gsignals__ = {"info": (GObject.SIGNAL_RUN_LAST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,))}

    def __init__(self, filename):

        GObject.Object.__init__(self)

        self.__filename = filename + ".json"

        self.__data = {
            'archivo': '',
            'formato inicial': '',
            'entrada de video': '',
            'entrada de sonido': '',
            'codec': '',
            'duracion': '',
            'relacion': '',
            'tiempo de proceso': '',
            'errores': ""
        }

    def setInfo(self, key, val):
        if key in self.__data.keys():
            self.__data[key] = val
            self.emit("info", self.__data)
            if self.__data.get("errores", False):
                try:
                    filepath = os.path.join(Reports, self.__filename)
                    set_dict(filepath, self.__data)
                except:
                    pass
                