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
from bs4 import BeautifulSoup
from CTkMessagebox import CTkMessagebox
from PIL import Image

# Use CTkToolTip and CTkListbox from my repo originally by Akascape (https://github.com/Akascape)
from .CTkListbox import ctk_listbox
from .CTkToolTip import ctk_tooltip


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'.
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE_PATH = "config.ini"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
LIBRARY_FILE = "boiiiwd_library.json"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources')
UPDATER_FOLDER = "update"
VERSION = "v0.3.1"