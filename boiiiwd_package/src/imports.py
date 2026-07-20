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
import pty
import pexpect

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
import shlex
from bs4 import BeautifulSoup

from .CTkMessagebox import CTkMessagebox
from PIL import Image

from .CTkListbox.ctk_listbox import CTkListbox
from .CTkToolTip.ctk_tooltip import CTkToolTip
from src.winpty_patch import PtyProcess

if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
    RESOURCES_DIR = os.path.join(sys._MEIPASS, 'resources')
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))
    RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')

# default enc key
DEFAULT_ENV_KEY = 'iDd40QsvCwsntXuLniIbNd6cAJEcALd85QTEgEhIc1c='
BOIIIWD_ENC_KEY = base64.urlsafe_b64decode(os.getenv('BOIIIWD_ENC_KEY', DEFAULT_ENV_KEY))

# Constants
GITHUB_REPO = "faroukbmiled/BOIIIWD"
ITEM_INFO_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Linux.zip"
LIBRARY_FILE = "boiiiwd_library.json"
UPDATER_FOLDER = "update"
STEAMCMD_WARNING_COUNTER = 20
SECONDS_UNTIL_FAIL_COUNTS = 15
FAIL_THRESHOLD_FALLBACK = 25
VERSION = "v0.3.8.1-linux"

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
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

# Linux paths
XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
XDG_DATA_HOME = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
CONFIG_DIR = os.path.join(XDG_CONFIG_HOME, "boiiiwd")
os.makedirs(CONFIG_DIR, exist_ok=True)
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, "config.ini")
STEAMCMD_DIR = os.path.join(XDG_DATA_HOME, "steamcmd")
STEAMCMD_EXE = "steamcmd.sh"
GAME_EXE = "BlackOps3"  # Running through Proton
