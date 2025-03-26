###################################################################
#  Youchie-PLI-FHD Skin Plugin Settings for Enigma2 by @Youchie
#  Coded by Youchie SmartCam Tem (c)2025
###################################################################
# -*- coding: utf-8 -*-
from Plugins.Plugin import PluginDescriptor
from Components.config import getConfigListEntry, NoSave, configfile, ConfigOnOff, config, ConfigText, ConfigNothing, ConfigSubsection, ConfigYesNo, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
import configparser
import os
import random
import sys
import time
import shutil
import glob
import requests
from urllib.request import Request, urlopen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.Progress import Progress
from Components.Sources.StaticText import StaticText
from enigma import eTimer, loadPic

try:
    from PIL import Image
except ImportError:
    from Image import Image

from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Tools.Directories import fileExists, SCOPE_PLUGINS, resolveFilename
from Tools.Downloader import downloadWithProgress

PY3 = sys.version_info.major >= 3

version = "1.0.1"
my_cur_skin = False
cur_skin = config.skin.primary_skin.value.replace('/skin.xml', '')

config_path = "/etc/enigma2/Youchie-PLI-FHD-config.ini"
skin_file = "/usr/share/enigma2/Youchie-PLI-FHD/skin.xml"
backup_file = "/usr/share/enigma2/Youchie-PLI-FHD/skin.xml.bak"


class YouchieSettingsScreen(ConfigListScreen, Screen):
    skin = '''<screen name="YouchieSettingsScreen" position="center,center" size="1000,640" title="Youchie-PLI-FHD Skin Settings">
        <widget name="config" font="Regular; 24" position="5,7" size="990,521" transparent="0" backgroundColor="background" itemHeight="42" zPosition="10" selectionPixmap="Youchie-PLI-FHD/selections/Youchie_lansel_FHD.png" scrollbarMode="showOnDemand" enableWrapAround="1" scrollbarBackgroundPicture="Youchie-PLI-FHD/frame/scrollbar_bg.png" scrollbarWidth="7" scrollbarSliderBorderWidth="0" scrollbarKeepGapColor="1" scrollbarGap="5" scrollbarSliderForegroundColor="orange" scrollbarSliderBorderColor="background" itemCornerRadius="8" foregroundColorSelected="orange" backgroundColorSelected="background" />
        <widget name="city" font="Regular; 26" position="559,590" size="420,35" foregroundColor="red" backgroundColor="black" transparent="1" zPosition="4" halign="center" valign="bottom" />
        <widget name="helpText" font="Regular; 22" position="5,549" size="990,30" foregroundColor="ffffff" backgroundColor="black" transparent="1" zPosition="2" halign="left" valign="center" />
        <!-- Cancel button -->
        <ePixmap position="27,589" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YouchieSettings/img/key_red.png" alphatest="blend" />
        <eLabel font="Regular; 24" foregroundColor="red" halign="center" position="80,594" size="120,26" text="Cancel" />
        <!-- Save button -->
        <ePixmap position="401,589" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/YouchieSettings/img/key_green.png" alphatest="blend" />
        <eLabel font="Regular; 24" foregroundColor="green" halign="center" position="280,594" size="120,26" text="Save" />
    </screen>
    '''

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)

        self.configparser = configparser.ConfigParser()
        self.configparser.read(config_path)

        self.poster_infobar_enabled = ConfigYesNo(default=self.configparser.getboolean("widgets", "poster_infobar", fallback=False))
        self.poster_infobar2_enabled = ConfigYesNo(default=self.configparser.getboolean("widgets", "poster_infobar2", fallback=False))
        self.show_2_poster_enabled = ConfigYesNo(default=self.configparser.getboolean("widgets", "show_2_poster_in_channel", fallback=False))
        self.show_7_poster_enabled = ConfigYesNo(default=self.configparser.getboolean("widgets", "show_7_poster_in_channel", fallback=False))

        self.show_2_poster_enabled.addNotifier(self.disable_7_poster, initial_call=False)
        self.show_7_poster_enabled.addNotifier(self.disable_2_poster, initial_call=False)

        config_list = [
            ("Enable Poster Display in the First Infobar", self.poster_infobar_enabled),
            ("Enable Poster Display in the Second Infobar", self.poster_infobar2_enabled),
            ("Enable 2-Poster Display in Channel Selection", self.show_2_poster_enabled),
            ("Enable 7-Poster Display in Channel Selection", self.show_7_poster_enabled)
        ]

        ConfigListScreen.__init__(self, config_list)
        self["actions"] = ActionMap(["SetupActions", "ColorActions"], {
            "ok": self.saveConfig,
            "cancel": self.close,
            "green": self.saveConfig
        }, -1)

    def disable_7_poster(self, config_element):
        if self.show_2_poster_enabled.value:
            self.show_7_poster_enabled.value = False

    def disable_2_poster(self, config_element):
        if self.show_7_poster_enabled.value:
            self.show_2_poster_enabled.value = False

    def saveConfig(self):
        self.configparser["widgets"] = {}
        self.configparser["widgets"]["poster_infobar"] = "on" if self.poster_infobar_enabled.value else "off"
        self.configparser["widgets"]["poster_infobar2"] = "on" if self.poster_infobar2_enabled.value else "off"
        self.configparser["widgets"]["show_2_poster_in_channel"] = "on" if self.show_2_poster_enabled.value else "off"
        self.configparser["widgets"]["show_7_poster_in_channel"] = "on" if self.show_7_poster_enabled.value else "off"

        with open(config_path, "w") as configfile:
            self.configparser.write(configfile)

        updateSkin()
        self.session.openWithCallback(self.restartGUI, MessageBox, "Settings saved! Do you want to restart Enigma2 now?", MessageBox.TYPE_YESNO)

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

def updateSkin():
    if not os.path.exists(backup_file):
        os.system(f"cp {skin_file} {backup_file}")

    with open(backup_file, "r") as f:
        skin_data = f.read()

    configparser_instance = configparser.ConfigParser()
    configparser_instance.read(config_path)

    show_poster = configparser_instance.getboolean("widgets", "poster_infobar", fallback=False)
    show_poster2 = configparser_instance.getboolean("widgets", "poster_infobar2", fallback=False)
    show_2_poster = configparser_instance.getboolean("widgets", "show_2_poster_in_channel", fallback=False)
    show_7_poster = configparser_instance.getboolean("widgets", "show_7_poster_in_channel", fallback=False)

    if show_7_poster:
        for panel in ["Channel_Select_EPG", "Channel_list_MOD_Def", "Arow_buttons_MDef"]:
            skin_data = skin_data.replace(f'<panel name="{panel}" />', '')

        if '<panel name="Chan_Sel_7Poster" />' not in skin_data:
            skin_data = skin_data.replace('<screen name="ChannelSelection" ', '''<screen name="ChannelSelection" position="0,0" size="1920,1080" title="ChannelSelection" flags="wfNoBorder" backgroundColor="transparent">
            <panel name="Chan_Sel_7Poster" />''')

        skin_data = skin_data.replace(
            '<ePixmap pixmap="Youchie-PLI-FHD/chnsel/ch_sel_bag.png" position="0,0" size="1920,1080" alphatest="off" zPosition="-11" transparent="0" />',
            '<ePixmap pixmap="Youchie-PLI-FHD/chnsel/ch_sel7p_bag.png" position="0,0" size="1920,1080" alphatest="off" zPosition="-11" transparent="0" />'
        )
    else:
        for panel in ["Channel_Select_EPG", "Channel_list_MOD_Def", "Arow_buttons_MDef"]:
            if f'<panel name="{panel}" />' not in skin_data:
                skin_data = skin_data.replace('<screen name="ChannelSelection" ', f'''<screen name="ChannelSelection" position="0,0" size="1920,1080" title="ChannelSelection" flags="wfNoBorder" backgroundColor="transparent">
                <panel name="{panel}" />''')

        skin_data = skin_data.replace('<panel name="Chan_Sel_7Poster" />', '')

        skin_data = skin_data.replace(
            '<ePixmap pixmap="Youchie-PLI-FHD/chnsel/ch_sel7p_bag.png" position="0,0" size="1920,1080" alphatest="off" zPosition="-11" transparent="0" />',
            '<ePixmap pixmap="Youchie-PLI-FHD/chnsel/ch_sel_bag.png" position="0,0" size="1920,1080" alphatest="off" zPosition="-11" transparent="0" />'
        )

    if show_poster:
        if '<panel name="Poster_Infobar1" />' not in skin_data:
            skin_data = skin_data.replace('<screen name="InfoBar" ', '''<screen name="InfoBar" position="0,0" size="1920,1080" title="InfoBar" flags="wfNoBorder" backgroundColor="transparent">
            <panel name="Poster_Infobar1" />''')
    else:
        skin_data = skin_data.replace('<panel name="Poster_Infobar1" />', '')

    if show_poster2:
        if '<panel name="Poster_Infobar2" />' not in skin_data:
            skin_data = skin_data.replace('<screen name="SecondInfoBar" ', '''<screen name="SecondInfoBar" position="0,0" size="1920,1080" title="SecondInfoBar" flags="wfNoBorder" backgroundColor="transparent">
            <panel name="Poster_Infobar2" />''')
        skin_data = skin_data.replace('<panel name="epginfo2" />', '')
    else:
        skin_data = skin_data.replace('<panel name="Poster_Infobar2" />', '')
        if '<panel name="epginfo2" />' not in skin_data:
            skin_data = skin_data.replace('<screen name="SecondInfoBar" ', '''<screen name="SecondInfoBar" position="0,0" size="1920,1080" title="SecondInfoBar" flags="wfNoBorder" backgroundColor="transparent">
            <panel name="epginfo2" />''')

    if show_2_poster:
        if '<panel name="Chan_Sel_2Poster" />' not in skin_data:
            skin_data = skin_data.replace('<screen name="ChannelSelection" ', '''<screen name="ChannelSelection" position="0,0" size="1920,1080" title="ChannelSelection" flags="wfNoBorder" backgroundColor="transparent">
            <panel name="Chan_Sel_2Poster" />''')
    else:
        skin_data = skin_data.replace('<panel name="Chan_Sel_2Poster" />', '')

    with open(skin_file, "w") as f:
        f.write(skin_data)

def main(session, **kwargs):
    session.open(YouchieSettingsScreen)

def Plugins(**kwargs):
    return [PluginDescriptor(
            name=_("Youchie Skin"),
            description=_('Manage Youchie-PLI-FHD Skin Settings'),
            where=PluginDescriptor.WHERE_PLUGINMENU,
            icon='/usr/lib/enigma2/python/Plugins/Extensions/YouchieSettings/img/YouchieSettings.png',
            fnc=main
    )]
