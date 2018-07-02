# -*- coding: utf-8 -*-

# http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs

import os
import urllib.parse
import urllib.request

from gi.repository import GObject

FEED = {
    "id": "",
    "titulo": "",
    "descripcion": "",
    "categoria": "",
    "url": "",
    "duracion": 0,
    "previews": ""
    }


class Buscar(GObject.GObject):

    __gsignals__ = {
    'encontrado': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_STRING, GObject.TYPE_STRING)),
    'end': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [])}

    def __init__(self, ):

        GObject.GObject.__init__(self)

    def __get_videos(self, consulta, limite):
        # Obtener web principal con resultado de busqueda y recorrer todas
        # las pags de la busqueda obtenida hasta conseguir el id de los videos.
        params = urllib.parse.urlencode({'search_query': consulta})
        urls = {}
        print ("Comezando la búsqueda de %i videos sobre %s" % (limite, consulta))
        for pag in range(1, 10):
            f = urllib.request.urlopen("http://www.youtube.com/results?%s&filters=video&page=%i" % (params, pag))
            text = str(f.read()).replace("\n", "")
            f.close()
            for item in text.split("data-context-item-id=")[1:]:
                _id = item.split("\"")[1].strip()
                url = "http://www.youtube.com/watch?v=%s" % _id
                if not _id in urls.keys():
                    urls[_id] = {"url": url}
                    self.emit("encontrado", _id, url)
                if len(urls.keys()) >= limite:
                    break
            if len(urls.keys()) >= limite:
                break
        print ("Búsqueda finalizada para:", consulta, "Videos encontrados:", len(urls.keys()))
        self.emit("end")

    def buscar(self, palabras, cantidad):
        buscar = ""
        for palabra in palabras.split(" "):
            buscar = "%s%s+" % (buscar, palabra.lower())
        if buscar.endswith("+"):
            buscar = str(buscar[:-1])
        try:  # FIXME: Porque falla si no hay Conexión.
            if buscar:
                self.__get_videos(buscar, cantidad)
        except:
            #FIXME: La interfaz queda insensitive
            print ("No tienes conexión ?")
