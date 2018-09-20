# -*- coding: utf-8 -*-


class InformeTranscoderModel():

    def __init__(self, filename):

        self.__filename = filename  # codec-archivo.json
        
        self.__data = {
            'archivo': '',
            'formato inicial': '',
            'entrada de video': '',
            'entrada de sonido': '',
            'codec': '',
            'duracion': '', #
            'relacion': '',
            'tiempo de proceso': '',
            'errores': [],  #
            'alertas': []   #
        }

    def setInfo(self, key, val):
        if key in self.__data.keys():
            if key == 'errores' or key == 'alertas':
                self.__data[key].append(val)
            else:
                self.__data[key] = val
            print (self.__data, "\n")
            # FIXME: Guardar cuando todos los campos tengan datos salvo 'tiempo de proceso', 'errores' y 'alertas'