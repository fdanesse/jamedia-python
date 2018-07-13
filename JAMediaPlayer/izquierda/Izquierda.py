# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.izquierda.videovisor import VideoVisor
from JAMediaPlayer.izquierda.toolbarinfo import ToolbarInfo
from JAMediaPlayer.Widgets.ProgressPlayer import ProgressPlayer


class Izquierda(Gtk.VBox):

    def __init__(self):

        Gtk.VBox.__init__(self)

        self.video_visor = VideoVisor()
        self.toolbar_info = ToolbarInfo()
        self.progress = ProgressPlayer()

        self.pack_start(self.video_visor, True, True, 0)
        self.pack_start(self.toolbar_info, False, False, 0)
        self.pack_start(self.progress, False, False, 0)

        self.show_all()

    def setup_init(self):
        self.toolbar_info.set_video(False)
        self.progress.set_sensitive(False)
