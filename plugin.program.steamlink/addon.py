"""Steamlink Launcher for OSMC"""
import os
import subprocess
import xbmc
import xbmcgui
import xbmcaddon
from urllib.request import urlretrieve

__plugin__ = "steamlink"
__author__ = "toast"
__url__ = "https://github.com/swetoast/steamlink-launcher/"
__git_url__ = "https://github.com/swetoast/steamlink-launcher/"
__credits__ = "toast"
__version__ = "0.0.14"

#dialog = xbmcgui.Dialog()
__addon__ = xbmcaddon.Addon(id='plugin.program.steamlink')
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')

# Show notification in the upper right corner
def ShowNotification(line):
    print(line)
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, line, 5000, __icon__))

def InstallSteamLink():
    # Install dependencies
    ShowNotification("Installing dependencies...")
    subprocess.run(["sudo", "apt", "install" "-y", "libegl1", "libgl1-mesa-dri", "libgles2", "libpulse0", "curl", "gnupg", "wakeonlan", "dnsutils", "cec-utils", "openssl", "libusb-1.0-0", "libx11-6", "libxext6", "libxkbcommon-x11-0", "libegl1", "libegl1-mesa", "libgles2-mesa", "libavcodec58" ])

    # Install Steam Link
    ShowNotification("Installing Steam Link...")
    deb_source = "http://media.steampowered.com/steamlink/rpi/latest/steamlink.deb"
    deb_target = "/tmp/steamlink.deb"
    urlretrieve(deb_source, deb_target)
    subprocess.run(["sudo", "apt", "install", "-f", deb_target]) # sudo apt install /tmp/steamlink.deb
    os.remove(deb_target)

def StartSteamLink():
    ShowNotification("Starting... please wait...")

    with open("/tmp/steamlink-launcher.sh", "w") as outfile:
        outfile.write("""#!/usr/bin/env bash
touch /home/osmc/.local/share/SteamLink/.ignore_gpumem
touch /home/osmc/.local/share/SteamLink/.ignore_cec
sudo ln -sf /home/osmc/.local/share/SteamLink/udev/modules-load.d/uinput.conf /etc/modules-load.d/uinput.conf
sudo ln -sf /home/osmc/.local/share/SteamLink/udev/rules.d/56-steamlink.rules /lib/udev/rules.d/56-steamlink.rules
chmod 755 /tmp/steamlink-watchdog.sh
sudo openvt -c 7 -s -f clear
sudo su -c "nohup sudo openvt -c 7 -s -f -l /tmp/steamlink-watchdog.sh >/tmp/steamlink-watchdog.log 2>&1 &"
""")
        outfile.close()

    with open("/tmp/steamlink-watchdog.sh", "w") as outfile:
        outfile.write("""#!/usr/bin/env bash
systemctl stop mediacenter
if [ "$(systemctl is-active hyperion.service)" = "active" ]; then systemctl restart hyperion; fi
sudo -u osmc steamlink >/tmp/steamlink.log 2>&1
openvt -c 7 -s -f clear
systemctl start mediacenter
""")
        outfile.close()

    # start steam link
    subprocess.run(["sh", "/tmp/steamlink-launcher.sh"])

def Main():
    if subprocess.run(["which", "steamlink"]).returncode > 0:
        InstallSteamLink()

    StartSteamLink()

Main()
