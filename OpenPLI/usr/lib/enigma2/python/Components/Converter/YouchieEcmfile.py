##############################################################################################################################################
#
#  Youchie-PLI-FHD Converter for Enigma2 By @Youchie
#  Coded by Youchie SmartCam Tem (c)2025
#  If you use this Converter for other skins and rename it, please keep the second line adding your credits below
#
##############################################################################################################################################
# -*- coding: utf-8 -*-

from Components.Converter.Converter import Converter
from Tools.Directories import fileExists

class YouchieEcmfile(Converter):
    def __init__(self, session):
        Converter.__init__(self, session)
        self.info = {}
        self.last_status = "not_opened"

    def ecmfile(self):
        if fileExists("/tmp/ecm.info"):
            self.info["source"] = "opened"
        else:
            self.info["source"] = "not_opened"
        return self.info

    def convert(self):
        self.ecmfile()
        status = self.info.get("source", "not_opened")
        
        if status != self.last_status:
            self.last_status = status
            return status
        
        return self.last_status
