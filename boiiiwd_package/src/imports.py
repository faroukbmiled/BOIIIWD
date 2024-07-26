import configparser
import io
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
import base64
import zipfile

from datetime import datetime
from pathlib import Path
from tkinter import END, Event, Menu

import customtkinter as ctk
import ujson as json
import psutil
import requests
import socket
import winreg
import ctypes
import shlex
from bs4 import BeautifulSoup

from CTkMessagebox import CTkMessagebox
from PIL import Image

# Use CTkToolTip and CTkListbox from my repo originally by Akascape (https://github.com/Akascape)
from .CTkListbox.ctk_listbox import CTkListbox
from .CTkToolTip.ctk_tooltip import CTkToolTip

# winpty, sorry to my linux friends, blame Steamcmd for their awful output buffering
from src.winpty_patch import PtyProcess, PatchedPtyProcess

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

# default enc key, change this to whatever you want in your ENV
DEFAULT_ENV_KEY = 'iDd40QsvCwsntXuLniIbNd6cAJEcALd85QTEgEhIc1c='
BOIIIWD_ENC_KEY = base64.urlsafe_b64decode(os.getenv('BOIIIWD_ENC_KEY', DEFAULT_ENV_KEY))

# Constants
CONFIG_FILE_PATH = "config.ini"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
ITEM_INFO_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
LIBRARY_FILE = "boiiiwd_library.json"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')
UPDATER_FOLDER = "update"
REGISTRY_KEY_PATH = r"Software\BOIIIWD"
STEAMCMD_WARNING_COUNTER = 20  # how many times steamcmd fails before showing a non breaking warning
SECONDS_UNTIL_FAIL_COUNTS = 15  # Minimum steamcmd runtime in seconds before a failed attempt counts as a fail (+1 to fail counter)
FAIL_THRESHOLD_FALLBACK = 25
DOWN_CAP = 15000000  # 15MB, workaround for psutil net_io_counters
VERSION = "v0.3.7.3"
