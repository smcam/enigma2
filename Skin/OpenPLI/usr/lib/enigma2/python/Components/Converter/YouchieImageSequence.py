##############################################################################################################################################
#
#  Youchie-PLI-FHD Converter for Enigma2 By @Youchie
#  Coded by Youchie SmartCam Tem (c)2025
#  If you use this Converter for other skins and rename it, please keep second line adding your credits below
#
##############################################################################################################################################
# -*- coding: utf-8 -*-
from Components.Converter.Converter import Converter
from os import listdir
from os.path import join, isfile
from time import time

class YouchieImageSequence(Converter):
    def __init__(self, args):
        Converter.__init__(self, args)
        self.image_folder = args.strip()
        self.images = self.load_images()

    def load_images(self):
        try:
            return sorted(
                [join(self.image_folder, f) for f in listdir(self.image_folder) if isfile(join(self.image_folder, f)) and f.endswith(".png")]
            )
        except Exception as e:
            print(f"[YouchieImageSequence] Error loading images: {e}")
            return []

    def getImage(self):
        if not self.images:
            return ""
        current_index = int((time() * 8) % len(self.images))  
        return self.images[current_index]

    text = property(getImage)

