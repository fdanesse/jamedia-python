#!/usr/bin/env python
# -*- coding: utf-8 -*-

#   Widgets.py por:
#   Flavio Danesse <fdanesse@gmail.com>
#   Uruguay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version("Gtk", "3.0")

from gi.repository import Gtk

from JAMediaPlayer.Globales import get_colors
from JAMediaPlayer.Globales import get_separador


class AlertaBusqueda(Gtk.Toolbar):
    """
    Para informar que se está buscando con JAMediaTube.
    """

    def __init__(self):

        Gtk.Toolbar.__init__(self)

        self.modify_bg(Gtk.StateType.NORMAL,
            get_colors("window1"))

        self.insert(get_separador(
            draw=False, ancho=3, expand=False), -1)

        item = Gtk.ToolItem()
        item.set_expand(True)
        self.label = Gtk.Label("")
        self.label.set_justify(Gtk.Justification.LEFT)
        #self.label.set_line_wrap(True)
        self.label.show()
        item.add(self.label)
        self.insert(item, -1)

        self.show_all()
