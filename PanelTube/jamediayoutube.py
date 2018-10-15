# -*- coding: utf-8 -*-

# https://github.com/rg3/youtube-dl
# http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs

import os
import time
import datetime
import urllib.parse
import urllib.request
import subprocess

from gi.repository import GLib

from JAMediaPlayer.Globales import YoutubeDir

# STDERR = "/dev/null"

# FIXME: Generar reportes al estilo del conversor

# BUSCAR Videos en Youtube
def __get_videos(consulta, limite, callback, callbackend):
    # Obtener web principal con resultado de busqueda y recorrer todas las pags de la busqueda obtenida hasta conseguir el id de los videos.
    # https://www.youtube.com/results?search_query=selena+gomez
    try:
        params = urllib.parse.urlencode({'search_query': consulta})
        urls = {}
        print ("Comezando la búsqueda de %i videos sobre %s..." % (limite, consulta))
        for pag in range(1, 10):
            f = urllib.request.urlopen("http://www.youtube.com/results?%s&filters=video&page=%i" % (params, pag))
            text = str(f.read()).replace("\n", "")
            f.close()
            for item in text.split("data-context-item-id=")[1:]:
                _id = item.split("\"")[1].strip()
                url = "http://www.youtube.com/watch?v=%s" % _id
                if not _id in urls.keys():
                    urls[_id] = {"url": url}
                    time.sleep(0.2)
                    callback(url)
                if len(urls.keys()) >= limite:
                    break
            if len(urls.keys()) >= limite:
                break
        print ("Búsqueda finalizada para:", consulta, "- Videos encontrados:", len(urls.keys()))
    except:
        print ("No tienes conexión ?")  # FIXME: implementar callback error
    return callbackend()

def buscar(palabras, cantidad, callback, callbackend):
    # Realiza la busqueda de videos en youtube
    buscar = palabras.replace(" ", "+").strip().lower()
    __get_videos(buscar, cantidad, callback, callbackend)


# DESCARGAR Metadatos del Videos encontrados
'''
[youtube] 1DhA69K3fZ4: Downloading webpage
[youtube] 1DhA69K3fZ4: Downloading video info webpage
[info] Writing video description metadata as JSON to: /tmp/1DhA69K3fZ4.info.json
[youtube] 1DhA69K3fZ4: Downloading thumbnail ...
[youtube] 1DhA69K3fZ4: Writing thumbnail to: /tmp/1DhA69K3fZ4.jpg
'''
# Descarga de info.json y thumbnail
def __get_progressThumbnail(salida, _dict, callback, youtubedl, STDOUT, t1, url):
    # Devuelve la dirección a los archivos json y thumbnail luego de descargados
    progress = salida.readline()
    if progress:
        t1 = datetime.datetime.now()
        if "Writing video description" in progress:
            _dict["json"] = progress.split(":")[-1].replace("\n", "").strip()
        elif "Writing thumbnail to" in progress:
            _dict["thumb"] = progress.split(":")[-1].replace("\n", "").strip()
    
    t2 = datetime.datetime.now()
    t3 = t2 - t1
    if all(_dict.values()) or t3.seconds >= 25:  # Más de 25 segundos no debe estar pausado
        if t3.seconds >= 25:
            print("Salteando descarga de metadatos:", url, t3)
        #t2 = datetime.datetime.now()
        #print("Time:", t2 - t1)
        youtubedl.kill()
        if salida: salida.close()
        if os.path.exists(STDOUT): os.unlink(STDOUT)
        callback(_dict)
        return False
    
    return True
    
def getJsonAndThumbnail(url, callback):
    # Descargar json y thumbnail. Genera 3 archivos, json, jpg y STDOUT
    # ./youtube-dl --write-info-json --write-thumbnail --skip-download -o /tmp/1DhA69K3fZ4 https://www.youtube.com/watch?v=1DhA69K3fZ4
    t1 = datetime.datetime.now()  # Solo para ver cuanto demora en hacer todo => 0:00:12.460755
    _dict = {"json": "", "thumb": ""}

    youtubedl = os.path.join(os.path.dirname(__file__), "youtube-dl")
    STDOUT = "/tmp/jamediatube%d" % time.time()

    destino = "/tmp/%s%d" % (url.split("=")[-1].strip(), time.time())
    estructura = "python3 %s --ignore-config --write-info-json --write-thumbnail --skip-download --no-warnings -o %s %s" % (youtubedl, destino, url)

    youtubedl = subprocess.Popen(estructura, shell=True, stdout=open(STDOUT, "w+b"), universal_newlines=True)
    salida = open(STDOUT, "r")

    GLib.timeout_add(200, __get_progressThumbnail, salida, _dict, callback, youtubedl, STDOUT, t1, url)



# DESCARGAR Videos de youtube
def __end(salida, youtubedl, STDOUT, callbackEnd):
    # FIXME: No es necesario y detiene los merge
    '''youtubedl.kill()
    if salida: salida.close()
    if os.path.exists(STDOUT): os.unlink(STDOUT)'''
    callbackEnd()
    return False

def __get_progressDownload(salida, progressCallback, callbackEnd, youtubedl, STDOUT, t1, url, informe):
    # Devuelve la dirección a los archivos json y thumbnail luego de descargados
    progress = salida.readline()
    if progress:
        t1 = datetime.datetime.now()
        if "100.0%" in progress.split():
            GLib.timeout_add(1000, __end, salida, youtubedl, STDOUT, callbackEnd)
            return False
        progressCallback(progress)
    
    t2 = datetime.datetime.now()
    t3 = t2 - t1
    if t3.seconds >= 25:  # Más de 25 segundos no debe estar pausado
        print("Salteando descarga de video:", url, t3)
        informe.setInfo('cancelados en descargas', url)
        #t2 = datetime.datetime.now()
        #print("Time:", t2 - t1)
        __end(salida, youtubedl, STDOUT, callbackEnd)
        return False
    
    return True

def runDownload(url, titulo, progressCallback, callbackEnd, informe):
    # Descargar video
    t1 = datetime.datetime.now()  # Solo para ver cuanto demora en hacer todo => 0:00:12.460755

    youtubedl = os.path.join(os.path.dirname(__file__), "youtube-dl")
    STDOUT = "/tmp/jamediatube%d" % time.time()

    #url = "http://youtu.be/" + url.split("=")[1]
    STDOUT = "/tmp/jamediatube%d" % time.time()

    archivo = "%s%s%s" % ("\"", titulo, "\"")
    destino = os.path.join(YoutubeDir, archivo)
    #python3 youtube-dl -f 'bestvideo+bestaudio' --ignore-config --ignore-errors --no-playlist -R 2 --no-part --no-warnings -o '%(title)s.%(ext)s' https://www.youtube.com/watch?v=1DhA69K3fZ4
    estructura = "python3 %s -f 'bestvideo+bestaudio' --ignore-config --ignore-errors --no-playlist -R 2 --no-part --no-warnings " % youtubedl
    estructura = estructura + "-o %s" % destino
    estructura = estructura + "'%(title)s.%(ext)s' "
    estructura = estructura + url

    youtubedl = subprocess.Popen(estructura, shell=True, stdout=open(STDOUT, "w+b"), universal_newlines=True)
    salida = open(STDOUT, "r")

    GLib.timeout_add(200, __get_progressDownload, salida, progressCallback, callbackEnd, youtubedl, STDOUT, t1, url, informe)

'''
para 100 videos de inna:
Descargados 93
3 en carpetas
Se informa de 65 que no se pudieron descargar
'''