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
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
    # For frozen apps, resources are in _MEIPASS/resources
    RESOURCES_DIR = os.path.join(sys._MEIPASS, 'resources')
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')

# default enc key, change this to whatever you want in your ENV
DEFAULT_ENV_KEY = 'iDd40QsvCwsntXuLniIbNd6cAJEcALd85QTEgEhIc1c='
BOIIIWD_ENC_KEY = base64.urlsafe_b64decode(os.getenv('BOIIIWD_ENC_KEY', DEFAULT_ENV_KEY))

# Constants
CONFIG_FILE_PATH = "config.ini"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
ITEM_INFO_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
LIBRARY_FILE = "boiiiwd_library.json"
STEAMCMD_DIR = os.path.join(APPLICATION_PATH, "scmd")
UPDATER_FOLDER = "update"
REGISTRY_KEY_PATH = r"Software\BOIIIWD"
STEAMCMD_WARNING_COUNTER = 20  # how many times steamcmd fails before showing a non breaking warning
SECONDS_UNTIL_FAIL_COUNTS = 15  # Minimum steamcmd runtime in seconds before a failed attempt counts as a fail (+1 to fail counter)
FAIL_THRESHOLD_FALLBACK = 25
VERSION = "v0.3.8.1"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}

def _build_steam_session():
    session = requests.Session()
    session.headers.update(BROWSER_HEADERS)
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.6,
        backoff_max=6,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["GET", "POST", "HEAD"]),
        respect_retry_after_header=False,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=10)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

STEAM_SESSION = _build_steam_session()
