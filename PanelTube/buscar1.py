# -*- coding: utf-8 -*-

import os
import urllib.parse
import urllib.request

from gi.repository import GObject

'''FEED = {
    "id": "",
    "titulo": "",
    "descripcion": "",
    "url": "",
    "duracion": 0,
    "previews": ""
    }'''


class Buscar(GObject.Object):

    __gsignals__ = {
    'encontrado': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, )),
    'end': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self, ):

        GObject.Object.__init__(self)

    def __get_videos(self, consulta, limite):
        # Obtener web principal con resultado de busqueda y recorrer todas las pags de la busqueda obtenida hasta conseguir el id de los videos.
        # https://www.youtube.com/results?search_query=selena+gomez
        params = urllib.parse.urlencode({'search_query': consulta})
        urls = {}
        print ("Comenzando la búsqueda de %i videos sobre: %s ..." % (limite, consulta.replace("+", " ").strip()))
        for pag in range(1, 10):
            f = urllib.request.urlopen("http://www.youtube.com/results?%s&filters=video&page=%i" % (params, pag))
            text = str(f.read()).replace("\n", "")
            f.close()
            for item in text.split("data-context-item-id=")[1:]:
                _id = item.split("\"")[1].strip()
                url = "http://www.youtube.com/watch?v=%s" % _id
                if not _id in urls.keys():
                    urls[_id] = {"url": url}
                    self.emit("encontrado", url)
                if len(urls.keys()) >= limite:
                    break
            if len(urls.keys()) >= limite:
                break
        print ("Búsqueda finalizada para:", consulta.replace("+", " ").strip(), ". Videos encontrados:", len(urls.keys()))
        self.emit("end")

    def buscar(self, palabras, cantidad):
        texto = palabras.strip().replace(" ", "+")
        try:  # FIXME: Porque falla si no hay Conexión.
            if texto:
                # FIXME: Hacer asincrono ?
                self.__get_videos(texto, cantidad)
        except:
            # FIXME: La interfaz queda insensitive
            print ("No tienes conexión ?")
            self.emit("end")  # FIXME: Implementar señal para errores
