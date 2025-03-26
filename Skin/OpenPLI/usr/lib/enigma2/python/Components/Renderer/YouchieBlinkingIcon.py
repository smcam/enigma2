##############################################################################################################################################
#  Youchie-PLI-FHD Renderer for Enigma2 By @Youchie
#  Coded by Youchie SmartCam Tem (c)2025
#  If you use this Renderer for other skins and rename it, please keep the second line adding your credits below
#
##############################################################################################################################################
# -*- coding: utf-8 -*-
from Components.Renderer.Pixmap import Pixmap
from Tools.Directories import fileExists
from enigma import eTimer

class YouchieBlinkingIcon(Pixmap):
    def __init__(self):
        Pixmap.__init__(self)
        self.png_path = None
        self.timer = eTimer()
        self.timer.callback.append(self.updatePixmap)  
        self.timer.start(500, True)  

    def applySkin(self, desktop, parent):
        attribs = []
        for attrib, value in self.skinAttributes:
            if attrib == "pixmap":
                self.png_path = value
            else:
                attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Pixmap.applySkin(self, desktop, parent)

    def changed(self, what):
        self.updatePixmap()

    def updatePixmap(self):
        if self.instance is None:
            return
        if self.source.text and fileExists(self.source.text):  
            self.instance.setPixmapFromFile(self.source.text)
        self.timer.start(500, True)  
