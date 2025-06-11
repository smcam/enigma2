#######################################################################
#
#    Renderer for Skin Youchie-PLI-FHD (Enigma2)
#    Coded by shamann (c)2020 New Edit And Fixed BY: @Youchie 2025
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#######################################################################
from Components.Renderer.Renderer import Renderer
from enigma import eLabel, eTimer, eSize, iServiceInformation, eServiceReference
from Components.VariableText import VariableText
from Components.config import config
from skin import parseFont
import NavigationInstance

class YouchieEmptyEpg(VariableText, Renderer):

    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)
        self.EmptyText = "Event Data Unavailable"  
        self.readTag = None
        self.tt = ""
        self.lastText = ""
        self.fillTimer = eTimer()
        try:
            self.fillTimer_conn = self.fillTimer.timeout.connect(self.__fillText)
        except AttributeError:
            self.fillTimer.timeout.get().append(self.__fillText)
        self.backText = ""
        self.vvv = ""
        self.testSizeLabel = None 
            
    def applySkin(self, desktop, parent):
        attribs = [ ]
        for (attrib, value) in self.skinAttributes:
            if attrib == "size":
                self.sizeX = int(value.strip().split(",")[0])
                attribs.append((attrib,value))
            elif attrib == "emptyText":
                self.EmptyText = value
            elif attrib == "font":
                self.used_font = parseFont(value, ((1,1),(1,1)))
                attribs.append((attrib,value))
            elif attrib == "readTagInfo":
                self.readTag = value
            else:
                attribs.append((attrib,value))
        self.skinAttributes = attribs
        self.testSizeLabel.setFont(self.used_font)
        self.testSizeLabel.resize(eSize(self.sizeX+500,20))
        self.testSizeLabel.setVAlign(eLabel.alignTop)
        self.testSizeLabel.setHAlign(eLabel.alignLeft)
        self.testSizeLabel.setNoWrap(1)
        if self.readTag:
            self.__tagTimer = eTimer()
            try:
                self.__tagTimer_conn = self.__tagTimer.timeout.connect(self.work)
            except AttributeError:
                self.__tagTimer.timeout.get().append(self.work)
        return Renderer.applySkin(self, desktop, parent)
        
    GUI_WIDGET = eLabel

    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((self.CHANGED_DEFAULT,))
        
    def changed(self, what):
        if self.instance and what[0] != self.CHANGED_CLEAR:
            self.tt = self.source.text
            self.work()

    def work(self):
        tmp = self.tt
        if self.readTag and self.tt == "":
            if self.__tagTimer.isActive():
                self.__tagTimer.stop()
            tmp = self.readTagInfo()
        if tmp == "":
            tmp = self.EmptyText
        if self.lastText != tmp:
            self.lastText = tmp
            self.testSizeLabel.setText(tmp)
            text_width = self.testSizeLabel.calculateSize().width()
            if text_width > (self.sizeX - 30):
                while (text_width > (self.sizeX - 30)):
                    tmp = tmp[:-1] 
                    self.testSizeLabel.setText(tmp)
                    text_width = self.testSizeLabel.calculateSize().width()
                pos = tmp.rfind(' ')
                if pos != -1:
                    tmp = tmp[:pos].rstrip(' ') + "..."
            if self.backText != tmp:
                self.backText = tmp                    
                ena = True
                try: ena = config.plugins.setupGlass17.par30.value
                except: pass
                if ena:
                    self.text = "_"                
                    self.endPoint = len(self.backText)
                    self.posIdx = 0                    
                    if self.fillTimer.isActive():
                        self.fillTimer.stop()
                    self.fillTimer.start(600, True)                     
                else:
                    self.text = tmp
                            
    def __fillText(self):
        self.fillTimer.stop()
        self.posIdx += 1
        if self.posIdx <= self.endPoint:
            self.text = self.backText[:self.posIdx] + "_"
            self.fillTimer.start(50, True)
        else:
            self.text = self.backText                     
                    
    def preWidgetRemove(self, instance):
        self.testSizeLabel = None

    def postWidgetCreate(self, instance):
        self.testSizeLabel = eLabel(instance)
        self.testSizeLabel.hide()
        
    def readTagInfo(self):
        self.__tagTimer.stop()
        ret = ""
        try:
            nav = NavigationInstance.instance
            service = nav.getCurrentService()
            info = service and service.info()
            if info is not None:
                refer = eServiceReference(info.getInfoString(iServiceInformation.sServiceref))
                if refer is not None:
                    refer = refer.toString()
                    if refer.startswith("-1:"):
                        refer = nav.getCurrentlyPlayingServiceReference()
                        if refer is not None:
                            refer = refer.toString()
                    if refer.startswith("4097:0") or "3a//" in refer or "http" in refer:
                        ret = str((service.info().getInfoString(iServiceInformation.sTagTitle)).split(',', 1)[0])
        except: pass
        self.__tagTimer.start(5000, True)
        return ret