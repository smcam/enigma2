##############################################################################################################################################
#  Youchie-PLI-FHD Renderer for Enigma2
#  Coded by Youchie SmartCam Tem (c)2025
#  If you use this Renderer for other skins and rename it, please keep the second line adding your credits below
#
##############################################################################################################################################

from Components.Renderer.Renderer import Renderer
from enigma import ePixmap
import os
import glob

class YouchieProviderIcon(Renderer):
    GUI_WIDGET = ePixmap

    def __init__(self):
        Renderer.__init__(self)
        self.icon_path_base = "/usr/share/enigma2/Youchie-PLI-FHD/provider_icons"
        self.default_icon = os.path.join(self.icon_path_base, "default.png")

    def changed(self, what):
        if not self.instance:
            return

        provider_name = self.source.text if self.source else None
        if provider_name:
            provider_name = provider_name.strip().upper()

            pattern = os.path.join(self.icon_path_base, f"{provider_name}*.png")
            matching_files = glob.glob(pattern)

            icon_path = matching_files[0] if matching_files else self.default_icon
        else:
            icon_path = self.default_icon

        try:
            self.instance.setPixmapFromFile(icon_path)
            self.instance.show()
        except Exception as e:
            print(f"Error loading provider icon: {e}")
            self.instance.hide()
