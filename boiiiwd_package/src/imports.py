import configparser
import io
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path
from tkinter import END, Event, Menu

import customtkinter as ctk
import psutil
import requests
import winreg
from bs4 import BeautifulSoup
from CTkMessagebox import CTkMessagebox
from PIL import Image

# Use CTkToolTip and CTkListbox from my repo originally by Akascape (https://github.com/Akascape)
from .CTkListbox.ctk_listbox import CTkListbox
from .CTkToolTip.ctk_tooltip import CTkToolTip


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE_PATH = "config.ini"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
ITEM_INFO_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
LIBRARY_FILE = "boiiiwd_library.json"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')
UPDATER_FOLDER = "update"
REGISTRY_KEY_PATH = r"Software\BOIIIWD"
VERSION = "v0.3.1"