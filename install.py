#!/usr/bin/env python
# -*- coding: utf-8 -*-

# JAMedia.py (path relativo)
# /Iconos/JAMedia.svg (path relativo)
# GTK;GNOME;AudioVideo;Player;Video; (GTK;GNOME;Juegos;)
# application/mxf;application/ogg;application/ram;application/sdp;application/smil;application/smil+xml;application/vnd.ms-wpl;application/vnd.rn-realmedia;application/x-extension-m4a;application/x-extension-mp4;application/x-flac;application/x-flash-video;application/x-matroska;application/x-netshow-channel;application/x-ogg;application/x-quicktime-media-link;application/x-quicktimeplayer;application/x-shorten;application/x-smil;application/xspf+xml;audio/3gpp;audio/ac3;audio/AMR;audio/AMR-WB;audio/basic;audio/midi;audio/mp2;audio/mp4;audio/mpeg;audio/mpegurl;audio/ogg;audio/prs.sid;audio/vnd.rn-realaudio;audio/x-aiff;audio/x-ape;audio/x-flac;audio/x-gsm;audio/x-it;audio/x-m4a;audio/x-matroska;audio/x-mod;audio/x-mp3;audio/x-mpeg;audio/x-mpegurl;audio/x-ms-asf;audio/x-ms-asx;audio/x-ms-wax;audio/x-ms-wma;audio/x-musepack;audio/x-pn-aiff;audio/x-pn-au;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;audio/x-pn-wav;audio/x-pn-windows-acm;audio/x-realaudio;audio/x-real-audio;audio/x-sbc;audio/x-scpls;audio/x-speex;audio/x-tta;audio/x-wav;audio/x-wavpack;audio/x-vorbis;audio/x-vorbis+ogg;audio/x-xm;image/vnd.rn-realpix;image/x-pict;misc/ultravox;text/google-video-pointer;text/x-google-video-pointer;video/3gpp;video/dv;video/fli;video/flv;video/mp2t;video/mp4;video/mp4v-es;video/mpeg;video/msvideo;video/ogg;video/quicktime;video/vivo;video/vnd.divx;video/vnd.rn-realvideo;video/vnd.vivo;video/webm;video/x-anim;video/x-avi;video/x-flc;video/x-fli;video/x-flic;video/x-flv;video/x-m4v;video/x-matroska;video/x-mpeg;video/x-ms-asf;video/x-ms-asx;video/x-msvideo;video/x-ms-wm;video/x-ms-wmv;video/x-ms-wmx;video/x-ms-wvx;video/x-nsv;video/x-ogm+ogg;video/x-theora+ogg;video/x-totem-stream;x-content/video-dvd;x-content/video-vcd;x-content/video-svcd;x-scheme-handler/pnm;x-scheme-handler/mms;x-scheme-handler/net;x-scheme-handler/rtp;x-scheme-handler/rtsp;x-scheme-handler/mmsh;x-scheme-handler/uvox;x-scheme-handler/icy;x-scheme-handler/icyx;

import os
import commands

self_path = os.path.abspath(os.path.dirname(__file__))

NAME = self_path.split("/")[-1]

final_path = os.path.join(os.environ["HOME"], '.local/share', NAME)

# borrar anterior.
if os.path.exists(final_path):
    print "Eliminando Version Anterior."
    commands.getoutput('rm -r %s' % (final_path))

# Crear Directorios.
if not os.path.exists(os.path.join(os.environ["HOME"], '.local')):
    print "Creando Directorio %s" % os.path.join(os.environ["HOME"], '.local')
    os.mkdir(os.path.join(os.environ["HOME"], '.local'))

if not os.path.exists(os.path.join(os.environ["HOME"], '.local/bin')):
    print "Creando Directorio %s" % os.path.join(os.environ["HOME"], '.local/bin')
    os.mkdir(os.path.join(os.environ["HOME"], '.local/bin'))

if not os.path.exists(os.path.join(os.environ["HOME"], '.local/share')):
    print "Creando Directorio %s" % os.path.join(os.environ["HOME"], '.local/share')
    os.mkdir(os.path.join(os.environ["HOME"], '.local/share'))

if not os.path.exists(os.path.join(os.environ["HOME"], '.local/share/applications')):
    print "Creando Directorio %s" % os.path.join(os.environ["HOME"], '.local/share/applications')
    os.mkdir(os.path.join(os.environ["HOME"], '.local/share/applications'))

# Copiar proyecto a destino final.
print "Copiando proyecto a %s" % os.path.join(os.environ["HOME"], '.local/share')
commands.getoutput('cp -r %s %s' % (self_path, os.path.join(os.environ["HOME"], '.local/share')))
commands.getoutput('chmod 755 -R %s' % final_path)

# Crear Archivo .desktop
print "Generando Archivo .desktop . . ."
main_path = os.path.join(final_path, "JAMedia.py")
icon_path = final_path + "/Iconos/JAMedia.svg"

desktoptext = """[Desktop Entry]
Encoding=UTF-8
Name=%s
GenericName=%s
Exec=%s
Terminal=false
Type=Application
Icon=%s
Categories=%s
MimeType=%s
StartupNotify=true""" % (NAME, NAME, main_path, icon_path, "GTK;GNOME;AudioVideo;Player;Video;", "application/mxf;application/ogg;application/ram;application/sdp;application/smil;application/smil+xml;application/vnd.ms-wpl;application/vnd.rn-realmedia;application/x-extension-m4a;application/x-extension-mp4;application/x-flac;application/x-flash-video;application/x-matroska;application/x-netshow-channel;application/x-ogg;application/x-quicktime-media-link;application/x-quicktimeplayer;application/x-shorten;application/x-smil;application/xspf+xml;audio/3gpp;audio/ac3;audio/AMR;audio/AMR-WB;audio/basic;audio/midi;audio/mp2;audio/mp4;audio/mpeg;audio/mpegurl;audio/ogg;audio/prs.sid;audio/vnd.rn-realaudio;audio/x-aiff;audio/x-ape;audio/x-flac;audio/x-gsm;audio/x-it;audio/x-m4a;audio/x-matroska;audio/x-mod;audio/x-mp3;audio/x-mpeg;audio/x-mpegurl;audio/x-ms-asf;audio/x-ms-asx;audio/x-ms-wax;audio/x-ms-wma;audio/x-musepack;audio/x-pn-aiff;audio/x-pn-au;audio/x-pn-realaudio;audio/x-pn-realaudio-plugin;audio/x-pn-wav;audio/x-pn-windows-acm;audio/x-realaudio;audio/x-real-audio;audio/x-sbc;audio/x-scpls;audio/x-speex;audio/x-tta;audio/x-wav;audio/x-wavpack;audio/x-vorbis;audio/x-vorbis+ogg;audio/x-xm;image/vnd.rn-realpix;image/x-pict;misc/ultravox;text/google-video-pointer;text/x-google-video-pointer;video/3gpp;video/dv;video/fli;video/flv;video/mp2t;video/mp4;video/mp4v-es;video/mpeg;video/msvideo;video/ogg;video/quicktime;video/vivo;video/vnd.divx;video/vnd.rn-realvideo;video/vnd.vivo;video/webm;video/x-anim;video/x-avi;video/x-flc;video/x-fli;video/x-flic;video/x-flv;video/x-m4v;video/x-matroska;video/x-mpeg;video/x-ms-asf;video/x-ms-asx;video/x-msvideo;video/x-ms-wm;video/x-ms-wmv;video/x-ms-wmx;video/x-ms-wvx;video/x-nsv;video/x-ogm+ogg;video/x-theora+ogg;video/x-totem-stream;x-content/video-dvd;x-content/video-vcd;x-content/video-svcd;x-scheme-handler/pnm;x-scheme-handler/mms;x-scheme-handler/net;x-scheme-handler/rtp;x-scheme-handler/rtsp;x-scheme-handler/mmsh;x-scheme-handler/uvox;x-scheme-handler/icy;x-scheme-handler/icyx;")

print desktoptext

desktop = open(os.path.join(os.environ["HOME"], ".local/share/applications/%s.desktop" % NAME), "w")
desktop.write(desktoptext)
desktop.close()

commands.getoutput('chmod 755 %s' % os.path.join(os.environ["HOME"], ".local/share/applications/%s.desktop" % NAME))
commands.getoutput("update-desktop-database %s" % os.path.join(os.environ["HOME"], ".local/share/applications/"))

print "Instalacion Finalizada."
