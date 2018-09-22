# -*- coding: utf-8 -*-

def format_ns(ns):
    s, ns = divmod(ns, 1000000000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if not h:
        return "%02u:%02u" % (m, s)
    else:
        return "%02u:%02u:%02u" % (h, m, s)


def getSize(currentcaps):
    # video/x-raw(memory:VASurface), format=(string)NV12, width=(int)1279, height=(int)720, framerate=(fraction)30/1, interlace-mode=(string)progressive, pixel-aspect-ratio=(fraction)1/1
    items = currentcaps.split(",")
    width = 0
    height = 0
    for item in items:
        if "width" in item:
            if ")" in item:
                width = item.split(")")[-1]
        elif "height" in item:
            if ")" in item:
                height = item.split(")")[-1]
        if width and height: continue
    return width, height