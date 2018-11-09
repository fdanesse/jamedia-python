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

youtubedllauncher = os.path.join(os.path.dirname(__file__), "youtube-dl")  #'/usr/bin/youtube-dl'
# STDERR = "/dev/null"

# BUSCAR Videos en Youtube
def __get_videos(consulta, limite, callback, callbackend, errorConection):
    # Obtener web principal con resultado de busqueda y recorrer todas las pags de la busqueda obtenida hasta conseguir el id de los videos.
    # https://www.youtube.com/results?search_query=selena+gomez
    try:
        params = urllib.parse.urlencode({'search_query': consulta})
        urls = {}
        print ("Comenzando la búsqueda de %i videos sobre %s..." % (limite, consulta))
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
                    callback(url, limite - len(urls.keys()))
                if len(urls.keys()) >= limite:
                    break
            if len(urls.keys()) >= limite:
                break
        print ("Búsqueda finalizada para:", consulta, "- Videos encontrados:", len(urls.keys()))
    except:
        errorConection()
    return callbackend()

def buscar(palabras, cantidad, callback, callbackend, errorConection):
    # Realiza la busqueda de videos en youtube
    buscar = palabras.replace(" ", "+").strip().lower()
    __get_videos(buscar, cantidad, callback, callbackend, errorConection)



T1 = datetime.datetime.now()
T2 = datetime.datetime.now()
# DESCARGAR Metadatos del Videos encontrados
def __timeCalc(youtubedl, salida, STDOUT, limite, url, text, callback):
    global T1
    t2 = datetime.datetime.now()
    t3 = t2 - T1
    if t3.seconds >= limite:
        youtubedl.kill()
        if salida: salida.close()
        if os.path.exists(STDOUT): os.unlink(STDOUT)
        callback({}, t3.seconds)
        print("TIEMPO => Salteando descarga de metadatos:", url, text, t3)
        return False, T1
    else:
        #print(url, text, t3)
        return True, datetime.datetime.now()

'''
[youtube] 1DhA69K3fZ4: Downloading webpage
[youtube] 1DhA69K3fZ4: Downloading video info webpage
[info] Writing video description metadata as JSON to: /tmp/1DhA69K3fZ4.info.json
[youtube] 1DhA69K3fZ4: Downloading thumbnail ...
[youtube] 1DhA69K3fZ4: Writing thumbnail to: /tmp/1DhA69K3fZ4.jpg
'''
# Descarga de info.json y thumbnail
def __get_progressThumbnail(salida, _dict, callback, youtubedl, STDOUT, url):
    # Devuelve la dirección a los archivos json y thumbnail luego de descargados
    progress = salida.readline()
    global T1
    if progress:
        if "Downloading webpage" in progress:
            ret, T1 = __timeCalc(youtubedl, salida, STDOUT, 13, url, "Downloading webpage", callback)  # Normalmente demora entre 7 y 8 segundos
            return ret
        elif "Downloading video info webpage" in progress:
            ret, T1 = __timeCalc(youtubedl, salida, STDOUT, 5, url, "Downloading video info webpage", callback)  # Normalmente demora menos de 1 segundo
            return ret
        elif "Writing video description" in progress:
            _dict["json"] = progress.split(":")[-1].replace("\n", "").strip()
        elif "Downloading thumbnail" in progress:
            ret, T1 = __timeCalc(youtubedl, salida, STDOUT, 5, url, "Downloading thumbnail", callback)  # Normalmente demora casi 2 segundos
            return ret
        elif "Writing thumbnail to" in progress:
            _dict["thumb"] = progress.split(":")[-1].replace("\n", "").strip()

    t2 = datetime.datetime.now()
    t3 = t2 - T1
    if all(_dict.values()) or t3.seconds >= 20:  # NOTA: Es necesario un límite de espera para que no bloquee todo el proceso
        if t3.seconds >= 20:
            print("TIEMPO => Salteando descarga de metadatos:", url)
        #else:
        #    global T2
        #    print("END:", t2 - T2, url)  #NOTA: Normalmente se demora entre 10 y segundos en todo el proceso
        youtubedl.kill()
        if salida: salida.close()
        if os.path.exists(STDOUT): os.unlink(STDOUT)
        callback(_dict, t3.seconds)
        return False

    return True
    
def getJsonAndThumbnail(url, callback):
    # Descargar json y thumbnail. Genera 3 archivos, json, jpg y STDOUT
    # ./youtube-dl --write-info-json --write-thumbnail --skip-download -o /tmp/1DhA69K3fZ4 https://www.youtube.com/watch?v=1DhA69K3fZ4
    global T2
    T2 = datetime.datetime.now()
    global T1
    T1 = datetime.datetime.now()
    _dict = {"json": "", "thumb": ""}

    STDOUT = "/tmp/jamediatube%d" % time.time()

    destino = "/tmp/%s%d" % (url.split("=")[-1].strip(), time.time())
    estructura = "python3 %s --ignore-config --write-info-json --write-thumbnail --skip-download --no-warnings -o %s %s" % (youtubedllauncher, destino, url)

    youtubedl = subprocess.Popen(estructura, shell=True, stdout=open(STDOUT, "w+b"), universal_newlines=True)
    salida = open(STDOUT, "r")

    GLib.timeout_add(200, __get_progressThumbnail, salida, _dict, callback, youtubedl, STDOUT, url)


# DESCARGAR Videos de youtube
def __end(salida, youtubedl, STDOUT, callbackEnd):
    # NOTA: No es necesario y detiene los merge
    '''youtubedl.kill()
    if salida: salida.close()
    if os.path.exists(STDOUT): os.unlink(STDOUT)'''
    callbackEnd()
    return False

def __get_progressDownload(salida, progressCallback, callbackEnd, youtubedl, STDOUT, url, informe, errorDownload):
    progress = salida.readline()
    global T1
    if progress:
        T1 = datetime.datetime.now()
        # Downloading webpage
        # Downloading video info webpage
        # Destination
        # download
        if "100.0%" in progress.split():
            GLib.timeout_add(1000, __end, salida, youtubedl, STDOUT, callbackEnd)
            #print("END:", datetime.datetime.now() - T2, url)
            return False
        elif "error" in progress or "ERROR" in progress:
            print("CONEXION ? => Salteando descarga de video:", url)
            errorDownload("Arror en descarga de: %s" % url)
            informe.setInfo('cancelados en descargas', url)
            __end(salida, youtubedl, STDOUT, callbackEnd)
            return False
        progressCallback(progress)
    
    t2 = datetime.datetime.now()
    t3 = t2 - T1
    if t3.seconds >= 50:
        print("TIEMPO => Salteando descarga de video:", url, t3.seconds)
        errorDownload("Salteando descarga de: %s T=%s" % (url, t3.seconds))
        informe.setInfo('cancelados en descargas', url)
        __end(salida, youtubedl, STDOUT, callbackEnd)
        return False
    
    return True

def runDownload(url, titulo, progressCallback, callbackEnd, informe, errorDownload):
    # Descargar video
    global T2
    T2 = datetime.datetime.now()
    global T1
    T1 = datetime.datetime.now()  # Solo para ver cuanto demora en hacer todo => 0:00:12.460755

    #url = "http://youtu.be/" + url.split("=")[1]
    STDOUT = "/tmp/jamediatube%d" % time.time()

    #archivo = "%s%s%s" % ("\"", titulo, "\"")
    destino = "%s/" % YoutubeDir #os.path.join(YoutubeDir, archivo)
    #python3 youtube-dl -f 'bestvideo+bestaudio' --ignore-config --ignore-errors --no-playlist -R 2 --no-part --no-warnings -o '%(title)s.%(ext)s' https://www.youtube.com/watch?v=1DhA69K3fZ4
    estructura = "python3 %s -f 'bestvideo+bestaudio' --ignore-config --ignore-errors --no-playlist -R 2 --no-part --no-warnings " % youtubedllauncher
    estructura = estructura + "-o %s" % destino
    estructura = estructura + "'%(title)s.%(ext)s' "
    estructura = estructura + url

    youtubedl = subprocess.Popen(estructura, shell=True, stdout=open(STDOUT, "w+b"), universal_newlines=True)
    salida = open(STDOUT, "r")

    GLib.timeout_add(200, __get_progressDownload, salida, progressCallback, callbackEnd, youtubedl, STDOUT, url, informe, errorDownload)
