import os
from collections import OrderedDict

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf

#from PanelTube.jamediayoutube import getJsonAndThumbnail
#from JAMediaPlayer.Globales import get_dict

ICONS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Iconos")


def downloadthumbnail(id, url):
    if not id or not url: return False
    import requests
    filename = os.path.join("/tmp", str(id) + ".jpg")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename,'wb') as f:
            f.write(response.content)
        return True
    return False


class WidgetVideoItem(Gtk.EventBox):

    __gsignals__ = {
        "end-update": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, []),
        "error-update": (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (GObject.TYPE_PYOBJECT,)),}

    def __init__(self, _dict):

        Gtk.EventBox.__init__(self)
        
        self.set_size_request(200, 100)

        #self.__fileimage = ""
        #self.__filejson = ""

        self._dict = OrderedDict({
            'id': _dict.get('id', ''),
            'title': _dict.get('title', ''),
            #'duration': '', 
            #'ext': '',
            #'width': '',
            #'height': '',
            #'format': '',
            #'fps': '',
            'url': _dict.get('url', ''),
            'thumbnail': _dict.get('thumbnail', '')
            })

        self.get_style_context().add_class("videoitem")

        hbox = Gtk.HBox()
        hbox.get_style_context().add_class("videoitemHB")
        self.__imagen = Gtk.Image()
        hbox.pack_start(self.__imagen, False, False, 3)
        
        self.__vbox = Gtk.VBox()
        for key in self._dict.keys():
            label = Gtk.Label("%s: %s" % (key, self._dict[key]))
            label.set_alignment(0.0, 0.5)
            self.__vbox.pack_start(label, True, True, 0)

        hbox.pack_start(self.__vbox, False, False, 5)
        self.add(hbox)

        self.show_all()
    
    '''
    def __del__(self):
        if os.path.exists(self.__fileimage): os.unlink(self.__fileimage)
        if os.path.exists(self.__filejson): os.unlink(self.__filejson)
    '''
    '''
    def __setImage(self, width=200, height=150):
        try:
            if os.path.exists(self.__fileimage):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.__fileimage, width, height)
                self.__imagen.set_from_pixbuf(pixbuf)
        except:
            print("No se puede cargar la imagen:", self.__fileimage)
            
    def __setLabels(self):
        values = list(self._dict.items())
        labels = self.__vbox.get_children()
        for label in labels:
            label.set_text("%s: %s" % (values[labels.index(label)]))
    '''
    
    def update(self):
        # 5 - Busquedas. NOTA: desde PanelTube
        # getJsonAndThumbnail(self._dict["url"], self.__endUpdate)
        if downloadthumbnail(self._dict.get('id', ''), self._dict.get('thumbnail', '')):
            filename = os.path.join("/tmp", self._dict['id'] + ".jpg")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 200, 150)
            self.__imagen.set_from_pixbuf(pixbuf)
        else:
            filename = os.path.join(ICONS, "jamedia.png")
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, 200, 150)
            self.__imagen.set_from_pixbuf(pixbuf)
        self.emit("end-update")
        # FIXME: Que hacer con los datos secundarios que se obtienen con el json.
        # FIXME: Mejorar estilo

    '''
    def __endUpdate(self, _dict, tiempo):
        # 6 - Busquedas
        self.__fileimage = _dict.get("thumb", "")
        self.__filejson = _dict.get("json", "")
        # NOTA: si los archivos no existen cuelga la aplicación
        if os.path.exists(self.__fileimage) and os.path.exists(self.__filejson):
            newdict = get_dict(self.__filejson)
            for key in self._dict.keys():
                if key == "url": continue
                self._dict[key] = newdict.get(key, None)
            # Test:
            # print ("\tDatos del Video:", str(newdict).encode('utf-8'))

            self.__setImage()
            self.__setLabels()
            self.emit("end-update")
        else:
            self.emit("error-update", tiempo)
    '''
