from CTkMessagebox import CTkMessagebox
from tkinter import Menu, END, Event
from bs4 import BeautifulSoup
import customtkinter as ctk
from CTkToolTip import *
from pathlib import Path
from PIL import Image
import configparser
import webbrowser
import subprocess
import threading
import datetime
import requests
import zipfile
import shutil
import psutil
import json
import math
import time
import sys
import io
import os
import re

VERSION = "v0.2.9"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
UPDATER_FOLDER = "update"
CONFIG_FILE_PATH = "config.ini"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')