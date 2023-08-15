from CTkMessagebox import CTkMessagebox
from bs4 import BeautifulSoup
import customtkinter as ctk
from pathlib import Path
from CTkToolTip import *
from PIL import Image
import configparser
import webbrowser
import subprocess
import threading
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

VERSION = "v0.2.0"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
UPDATER_FOLDER = "update"
CONFIG_FILE_PATH = "config.ini"

# fuck it we ball, ill remove these when i finish with eveything (and replace them with none global bools)
global stopped, steampid, console, clean_on_finish
steampid = None
stopped = False
console = False
clean_on_finish = True

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Start Helper Functions
def get_latest_release_version():
    try:
        release_api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(release_api_url)
        response.raise_for_status()
        data = response.json()
        return data["tag_name"]
    except requests.exceptions.RequestException as e:
        show_message("Warning", f"Error while checking for updates: \n{e}")
        return None


def create_update_script(current_exe, new_exe, updater_folder, program_name):
    script_content = f"""
    @echo off
    echo Terminating BOIIIWD.exe...
    taskkill /im "{program_name}" /t /f

    echo Replacing BOIIIWD.exe...
    cd "{updater_folder}"
    taskkill /im "{program_name}" /t /f
    move /y "{new_exe}" "../"{program_name}""

    echo Starting BOIIIWD.exe...
    cd ..
    start "" "{current_exe}"

    echo Exiting!
    exit
    """

    script_path = os.path.join(updater_folder, "boiiiwd_updater.bat")
    with open(script_path, "w") as script_file:
        script_file.write(script_content)

    return script_path

def check_for_updates_func(window, ignore_up_todate=False):
    try:
        latest_version = get_latest_release_version()
        current_version = VERSION

        if latest_version and latest_version != current_version:
            msg_box = CTkMessagebox(title="Update Available", message=f"An update is available! Install now?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}", option_1="View", option_2="No", option_3="Yes", fade_in_duration=int(1))

            result = msg_box.get()

            if result == "View":
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")

            if result == "Yes":
                update_window = UpdateWindow(window, LATEST_RELEASE_URL)
                update_window.start_update()

            if result == "No":
                return

        elif latest_version == current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(title="Up to Date!", message="No Updates Available!", option_1="Ok")
            result = msg_box.get()
    except Exception as e:
        show_message("Error", f"Error while checking for updates: \n{e}", icon="cancel")

def cwd():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def extract_workshop_id(link):
    try:
        pattern = r'(?<=id=)(\d+)'
        match = re.search(pattern, link)

        if match:
            return match.group(0)
        else:
            return None
    except:
        return None

def check_steamcmd():
    steamcmd_path = get_steamcmd_path()
    steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")

    if not os.path.exists(steamcmd_exe_path):
        return False

    return True

def initialize_steam(master):
    try:
        steamcmd_path = get_steamcmd_path()
        steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")
        process = subprocess.Popen([steamcmd_exe_path, "+quit"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        master.attributes('-alpha', 0.0)
        process.wait()
        show_message("SteamCMD has terminated!", "BOIIIWD is ready for action.", icon="info")
    except:
        show_message("Error!", "An error occurred please check your paths and try again.", icon="cancel")
    master.attributes('-alpha', 1.0)

def valid_id(workshop_id):
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
    response = requests.get(url)
    response.raise_for_status()
    content = response.text
    soup = BeautifulSoup(content, "html.parser")

    try:
        soup.find("div", class_="rightDetailsBlock").text.strip()
        soup.find("div", class_="workshopItemTitle").text.strip()
        soup.find("div", class_="detailsStatRight").text.strip()
        stars_div = soup.find("div", class_="fileRatingDetails")
        stars_div.find("img")["src"]
        return True
    except:
        return False

def convert_speed(speed_bytes):
    if speed_bytes < 1024:
        return speed_bytes, "B/s"
    elif speed_bytes < 1024 * 1024:
        return speed_bytes / 1024, "KB/s"
    elif speed_bytes < 1024 * 1024 * 1024:
        return speed_bytes / (1024 * 1024), "MB/s"
    else:
        return speed_bytes / (1024 * 1024 * 1024), "GB/s"

def create_default_config():
    config = configparser.ConfigParser()
    config["Settings"] = {
        "SteamCMDPath": cwd(),
        "DestinationFolder": "",
        "checkforupdtes": "on",
        "console": "off"
    }
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def run_steamcmd_command(command, self):
    steamcmd_path = get_steamcmd_path()
    show_console = subprocess.CREATE_NO_WINDOW
    if console:
        show_console = subprocess.CREATE_NEW_CONSOLE

    process = subprocess.Popen(
        [steamcmd_path + "\steamcmd.exe"] + command.split(),
        stdout=None if console else subprocess.PIPE,
        stderr=None if console else subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
        creationflags=show_console
    )

    global steampid
    steampid = process.pid

    if process.poll() is not None:
        return process.returncode

    process.communicate()

    show_message("SteamCMD has terminated", "SteamCMD has been terminated\nTry again if it randomly stopped!")
    global stopped
    stopped = True
    self.button_download.configure(state="normal")
    self.button_stop.configure(state="disabled")

    return process.returncode


def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback=cwd())

def check_config(name, fallback=None):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    if fallback:
        return config.get("Settings", name, fallback=fallback)
    return config.get("Settings", name, fallback="on")

def save_config(name, value):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    if name and value:
        config.set("Settings", name, value)
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def extract_json_data(json_path):
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    return data["Type"], data["FolderName"]

def convert_bytes_to_readable(size_in_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0

def get_workshop_file_size(workshop_id, raw=None):
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&searchtext="
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    file_size_element = soup.find("div", class_="detailsStatRight")

    try:
        if raw:
            file_size_text = file_size_element.get_text(strip=True)
            file_size_text = file_size_text.replace(",", "")
            file_size_in_mb = float(file_size_text.replace(" MB", ""))
            file_size_in_bytes = int(file_size_in_mb * 1024 * 1024)
            return convert_bytes_to_readable(file_size_in_bytes)

        if file_size_element:
            file_size_text = file_size_element.get_text(strip=True)
            file_size_text = file_size_text.replace(",", "")
            file_size_in_mb = float(file_size_text.replace(" MB", ""))
            file_size_in_bytes = int(file_size_in_mb * 1024 * 1024)
            return file_size_in_bytes
        return None
    except:
        return None

def show_message(title, message, icon="warning", exit_on_close=False):

    if exit_on_close:
        msg = CTkMessagebox(title=title, message=message, icon=icon, option_1="No", option_2="Ok")
        response = msg.get()
        if response=="No":
            return False
        if response=="Ok":
            return True
        else:
            return False
    else:
        msg = CTkMessagebox(title=title, message=message, icon=icon)

def launch_boiii_func(path):
    try:
        boiii_path = os.path.join(path, "boiii.exe")
        subprocess.Popen([boiii_path], cwd=path)
    except Exception as e:
        show_message("Error: Failed to launch BOIII", f"Failed to launch boiii.exe\nMake sure to put in your correct boiii path\n{e}")

def remove_tree(folder_path, show_error=None):
    if show_error:
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            show_message("Error!", f"An error occurred while trying to remove files:\n{e}", icon="cancel")
    try:
        shutil.rmtree(folder_path)
    except Exception as e:
        pass

# End helper functions

class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, update_url):
        global master_win
        master_win = master
        super().__init__(master)
        self.title("BOIIIWD Self-Updater")
        self.geometry("400x150")
        self.after(250, lambda: self.iconbitmap('ryuk.ico'))
        self.protocol("WM_DELETE_WINDOW", self.cancel_update)
        self.attributes('-topmost', 'true')

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.label_download = ctk.CTkLabel(self, text="Starting...")
        self.label_download.grid(row=0, column=0, padx=30, pady=(10, 0), sticky="w")

        self.label_size = ctk.CTkLabel(self, text="Size: 0")
        self.label_size.grid(row=0, column=1, padx=30, pady=(10, 0), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", height=20, corner_radius=7)
        self.progress_bar.grid(row=1, column=0, columnspan=4, padx=30, pady=10, sticky="ew")
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(self.progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", height=0, width=0, corner_radius=0)
        self.progress_label.place(relx=0.5, rely=0.5, anchor="center")

        self.cancel_button = ctk.CTkButton(self, text="Cancel", command=self.cancel_update)
        self.cancel_button.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="w")

        self.update_url = update_url
        self.total_size = None
        self.up_cancelled = False

    def update_progress_bar(self):
        try:
            update_dir = os.path.join(os.getcwd(), UPDATER_FOLDER)
            response = requests.get(LATEST_RELEASE_URL, stream=True)
            response.raise_for_status()
            current_exe = sys.argv[0]
            program_name = os.path.basename(current_exe)
            new_exe = os.path.join(update_dir, "BOIIIWD.exe")

            if not os.path.exists(update_dir):
                os.makedirs(update_dir)

            self.progress_bar.set(0.0)
            self.total_size = int(response.headers.get('content-length', 0))
            self.label_size.configure(text=f"Size: {convert_bytes_to_readable(self.total_size)}")
            zip_path = os.path.join(update_dir, "latest_version.zip")

            with open(zip_path, "wb") as file:
                downloaded_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if self.up_cancelled:
                        break
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress = int((downloaded_size / self.total_size) * 100)

                        self.after(1, lambda p=progress: self.label_download.configure(text=f"Downloading update..."))
                        self.after(1, lambda v=progress / 100.0: self.progress_bar.set(v))
                        self.after(1, lambda p=progress: self.progress_label.configure(text=f"{p}%"))

            if not self.up_cancelled:
                self.progress_bar.set(1.0)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(update_dir)
                self.label_download.configure(text="Update Downloaded successfully!")
                if not show_message("Success!", "Update Downloaded successfully!\nPress ok to install it", icon="info", exit_on_close=True):
                    return
                script_path = create_update_script(current_exe, new_exe, update_dir, program_name)
                subprocess.run(('cmd', '/C', 'start', '', fr'{script_path}'))
                sys.exit(0)
            else:
                if os.path.exists(zip_path):
                    os.remove(fr"{zip_path}")
                self.label_download.configure(text="Update cancelled.")
                self.progress_bar.set(0.0)
                # there's a better solution ill implement it later
                global master_win
                try:
                    master_win.attributes('-alpha', 1.0)
                except:
                    pass
                show_message("Cancelled!", "Update cancelled by user", icon="warning")
        except Exception as e:
            self.progress_bar.set(0.0)
            self.label_download.configure(text="Update failed")
            show_message("Error", f"Error installing the update\n{e}", icon="cancel")

    def start_update(self):
        self.thread = threading.Thread(target=self.update_progress_bar)
        self.thread.start()

    def cancel_update(self):
        self.up_cancelled = True
        self.withdraw()

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)

        # Left and right frames, use fg_color="transparent"
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=(20, 20), pady=(20, 0), sticky="nsew")
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        right_frame.grid_columnconfigure(1, weight=1)
        self.update_idletasks()

        # Check for updates checkbox
        self.check_updates_var = ctk.BooleanVar()
        self.check_updates_var.trace_add("write", self.enable_save_button)
        self.check_updates_checkbox = ctk.CTkSwitch(left_frame, text="Check for updates on launch", variable=self.check_updates_var)
        self.check_updates_checkbox.grid(row=0, column=1, padx=20 , pady=(20, 0), sticky="nw")
        self.check_updates_var.set(self.load_settings("checkforupdates"))

        # Show console checkbox
        self.console_var = ctk.BooleanVar()
        self.console_var.trace_add("write", self.enable_save_button)
        self.checkbox_show_console = ctk.CTkSwitch(left_frame, text="Console (On Download)", variable=self.console_var)
        self.checkbox_show_console.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.checkbox_show_console_tooltip = CTkToolTip(self.checkbox_show_console, message="Toggle SteamCMD console\nPlease don't close the Console If you want to stop press the Stop button")
        self.console_var.set(self.load_settings("console"))

        # clean on finish checkbox
        self.clean_checkbox_var = ctk.BooleanVar()
        self.clean_checkbox_var.trace_add("write", self.enable_save_button)
        self.clean_checkbox = ctk.CTkSwitch(left_frame, text="Clean on finish", variable=self.clean_checkbox_var)
        self.clean_checkbox.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.clean_checkbox_tooltip = CTkToolTip(self.clean_checkbox, message="Cleans the map that have been downloaded and installed from steamcmd's steamapps folder ,to save space")
        self.clean_checkbox_var.set(self.load_settings("clean_on_finish", "on"))

        # Check for updates button n Launch boiii
        self.check_for_updates = ctk.CTkButton(right_frame, text="Check for updates", command=self.settings_check_for_updates)
        self.check_for_updates.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="n")

        self.launch_boiii = ctk.CTkButton(right_frame, text="Launch boiii", command=self.settings_launch_boiii)
        self.launch_boiii.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="n")

        self.reset_steamcmd = ctk.CTkButton(right_frame, text="Reset SteamCMD", command=self.settings_reset_steamcmd)
        self.reset_steamcmd.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="n")
        self.reset_steamcmd_tooltip = CTkToolTip(self.reset_steamcmd, message="This will remove steamapps folder + all the maps that are potentioaly corrupted or not so use at ur own risk (could fix some issues as well)")

        # Save button
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_settings, state='disabled')
        self.save_button.grid(row=3, column=0, padx=20, pady=(20, 20), sticky="nw")


    def enable_save_button(self, *args):
        try:
            self.save_button.configure(state='normal')
        except:
            pass

    def save_settings(self):
        self.save_button.configure(state='disabled')
        global console, clean_on_finish
        if self.check_updates_checkbox.get():
            save_config("checkforupdtes", "on")
        else:
            save_config("checkforupdtes", "off")

        if self.checkbox_show_console.get():
            save_config("console", "on")
            console = True
        else:
            save_config("console", "off")
            console = False

        if self.clean_checkbox.get():
            save_config("clean_on_finish", "on")
            clean_on_finish = True
        else:
            save_config("clean_on_finish", "off")
            clean_on_finish = False

    def load_settings(self, setting, fallback=None):
        global console, clean_on_finish
        if setting == "console":
            if check_config(setting, fallback) == "on":
                console = True
                return 1
            else:
                console = False
                return 0
        if setting == "clean_on_finish":
            if check_config(setting, fallback) == "on":
                clean_on_finish = True
                return 1
            else:
                clean_on_finish = False
                return 0
        else:
            if check_config(setting, fallback) == "on":
                return 1
            else:
                return 0

    def settings_check_for_updates(self):
        check_for_updates_func(self, ignore_up_todate=False)

    def load_on_switch_screen(self):
        self.check_updates_var.set(self.load_settings("checkforupdtes"))
        self.console_var.set(self.load_settings("console"))

        # keep last cuz of trace_add()
        self.save_button.configure(state='disabled')

    def settings_launch_boiii(self):
        launch_boiii_func(check_config("destinationfolder"))

    def settings_reset_steamcmd(self):
        steamcmd_path = get_steamcmd_path()
        steamcmd_steamapps = os.path.join(steamcmd_path, "steamapps")
        if os.path.exists(steamcmd_steamapps):
            remove_tree(steamcmd_steamapps, show_error=True)
            show_message("Success!", "SteamCMD has been reset successfully!", icon="info")
        else:
            show_message("Warning!", "steamapps folder was not found, maybe already removed?", icon="warning")

class BOIIIWD(ctk.CTk):
    def __init__(self):
        super().__init__()
        # self.app_instance = BOIIIWD()

        # configure window
        self.title("BOIII Workshop Downloader - Main")
        self.geometry(f"{910}x{560}")
        self.wm_iconbitmap('ryuk.ico')

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.settings_tab = SettingsTab(self)

        # create sidebar frame with widgets
        self.sidebar_icon = ctk.CTkImage(light_image=Image.open("ryuk.png"), dark_image=Image.open("ryuk.png"), size=(40, 40))
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, padx=(10, 10), pady=(10, 10), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text='',image=self.sidebar_icon)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.txt_label = ctk.CTkLabel(self.sidebar_frame, text="- Sidebar -")
        self.txt_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_main = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_main.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_library = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_library.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_queue = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_queue.grid(row=4, column=0, padx=20, pady=10, sticky="n")
        self.sidebar_settings = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_settings.grid(row=5, column=0, padx=20, pady=10)
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 10))
        self.scaling_label = ctk.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=8, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=0, padx=20, pady=(10, 20))

        # create optionsframe
        self.optionsframe = ctk.CTkFrame(self)
        self.optionsframe.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        # create slider and progressbar frame
        self.slider_progressbar_frame = ctk.CTkFrame(self)
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

        self.slider_progressbar_frame.columnconfigure(0, weight=0)
        self.slider_progressbar_frame.columnconfigure(1, weight=1)
        self.slider_progressbar_frame.columnconfigure(2, weight=0)
        self.slider_progressbar_frame.rowconfigure(0, weight=1)
        self.slider_progressbar_frame.rowconfigure(1, weight=1)
        self.slider_progressbar_frame.rowconfigure(2, weight=1)
        self.slider_progressbar_frame.rowconfigure(3, weight=1)

        self.spacer = ctk.CTkLabel(master=self.slider_progressbar_frame, text="")
        self.spacer.grid(row=0, column=0, columnspan=1)

        self.label_speed = ctk.CTkLabel(master=self.slider_progressbar_frame, text="Network Speed: 0 KB/s")
        self.label_speed.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.label_file_size = ctk.CTkLabel(master=self.slider_progressbar_frame, text="File size: 0KB")
        self.label_file_size.grid(row=1, column=2, padx=(0, 20), pady=(0, 10), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(master=self.slider_progressbar_frame, mode="determinate", height=20, corner_radius=7)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 10), columnspan=3, sticky="ew")

        self.progress_text = ctk.CTkLabel(self.progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", height=0, width=0, corner_radius=0)
        self.progress_text.place(relx=0.5, rely=0.5, anchor="center")

        self.button_download = ctk.CTkButton(master=self.slider_progressbar_frame, text="Download", command=self.download_map)
        self.button_download.grid(row=4, column=0, padx=20, pady=(10, 20), columnspan=2, sticky="ew")

        self.button_stop = ctk.CTkButton(master=self.slider_progressbar_frame, text="Stop", command=self.stop_download)
        self.button_stop.grid(row=4, column=2, padx=(0, 20), pady=(10, 20), columnspan=1, sticky="ew")

        # options frame
        self.optionsframe.columnconfigure(1, weight=1)
        self.optionsframe.columnconfigure(2, weight=1)
        self.optionsframe.columnconfigure(3, weight=1)

        self.label_workshop_id = ctk.CTkLabel(master=self.optionsframe, text="Enter the Workshop ID or Link of the map/mod you want to download:")
        self.label_workshop_id.grid(row=0, column=1, padx=20, pady=(20, 0), columnspan=3, sticky="w")

        self.check_if_changed = ctk.StringVar()
        self.check_if_changed.trace_add("write", self.id_chnaged_handler)
        self.edit_workshop_id = ctk.CTkEntry(master=self.optionsframe, textvariable=self.check_if_changed)
        self.edit_workshop_id.grid(row=1, column=1, padx=20, pady=(0, 10), columnspan=4, sticky="ew")

        self.button_browse = ctk.CTkButton(master=self.optionsframe, text="Browse", command=self.open_browser)
        self.button_browse.grid(row=1, column=5, padx=(0, 20), pady=(0, 10), sticky="ew")

        self.info_button = ctk.CTkButton(master=self.optionsframe, text="Info", command=self.show_map_info)
        self.info_button.grid(row=2, column=5, padx=(0, 20), pady=(0, 10), sticky="ew")

        self.label_destination_folder = ctk.CTkLabel(master=self.optionsframe, text="Enter Your BOIII folder:")
        self.label_destination_folder.grid(row=3, column=1, padx=20, pady=(0, 10), columnspan=4, sticky="w")

        self.edit_destination_folder = ctk.CTkEntry(master=self.optionsframe, placeholder_text="Your BOIII Instalation folder")
        self.edit_destination_folder.grid(row=4, column=1, padx=20, pady=(0, 10), columnspan=4, sticky="ew")

        self.button_BOIII_browse = ctk.CTkButton(master=self.optionsframe, text="Select", command=self.open_BOIII_browser)
        self.button_BOIII_browse.grid(row=4, column=5, padx=(0, 20), pady=(0, 10), sticky="ew")

        self.label_steamcmd_path = ctk.CTkLabel(master=self.optionsframe, text="Enter SteamCMD path:")
        self.label_steamcmd_path.grid(row=5, column=1, padx=20, pady=(20, 0), columnspan=3, sticky="w")

        self.edit_steamcmd_path = ctk.CTkEntry(master=self.optionsframe, placeholder_text="Enter your SteamCMD path")
        self.edit_steamcmd_path.grid(row=6, column=1, padx=20, pady=(0, 10), columnspan=4, sticky="ew")

        self.button_steamcmd_browse = ctk.CTkButton(master=self.optionsframe, text="Select", command=self.open_steamcmd_path_browser)
        self.button_steamcmd_browse.grid(row=6, column=5, padx=(0, 20), pady=(0, 10), sticky="ew")

        # set default values
        self.appearance_mode_optionemenu.set("Dark")
        self.scaling_optionemenu.set("100%")
        self.progress_bar.set(0.0)
        self.hide_settings_widgets()
        self.button_stop.configure(state="disabled")

        # sidebar windows bouttons
        self.sidebar_main.configure(command=self.main_button_event, text="Main", fg_color=("#3d3d3d"))
        self.sidebar_library.configure(state="disabled", text="Library")
        self.sidebar_queue.configure(state="disabled", text="Queue")
        self.sidebar_settings.configure(command=self.settings_button_event, text="Settings")
        self.sidebar_library_tooltip = CTkToolTip(self.sidebar_library, message="Coming soon")
        self.sidebar_queue_tooltip = CTkToolTip(self.sidebar_queue, message="Coming soon")

        # load ui configs
        self.load_configs()

        if check_config("checkforupdtes") == "on":
            self.withdraw()
            check_for_updates_func(self, ignore_up_todate=True)
            self.update()
            self.deiconify()

        try:
            global console
            if check_config("console") == "on":
                console = True
            else:
                console = False
        except:
            pass

        if not check_steamcmd():
            self.show_warning_message()


    def id_chnaged_handler(self, some=None, other=None ,shit=None):
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

    def check_for_updates(self):
        check_for_updates_func(self, ignore_up_todate=False)

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)
        save_config("appearance", new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        ctk.set_widget_scaling(new_scaling_float)
        save_config("scaling", str(new_scaling_float))

    def sidebar_button_event(self):
        print("sidebar_button click")

    def hide_main_widgets(self):
        self.optionsframe.grid_forget()
        self.slider_progressbar_frame.grid_forget()

    def show_main_widgets(self):
        self.title("BOIII Workshop Downloader - Main")
        self.optionsframe.grid(row=0, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 0), sticky="nsew")

    def hide_settings_widgets(self):
        self.settings_tab.grid_forget()

    def show_settings_widgets(self):
        self.title("BOIII Workshop Downloader - Settings")
        self.settings_tab.grid(row=0, rowspan=3, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.settings_tab.load_on_switch_screen()

    def main_button_event(self):
        self.sidebar_main.configure(state="active", fg_color=("#3d3d3d"))
        self.sidebar_settings.configure(state="normal", fg_color=("#1f538d"))
        self.hide_settings_widgets()
        self.show_main_widgets()

    def settings_button_event(self):
        self.sidebar_main.configure(state="normal", fg_color=("#1f538d"))
        self.sidebar_settings.configure(state="active", fg_color=("#3d3d3d"))
        self.hide_main_widgets()
        self.show_settings_widgets()

    def load_configs(self):
        if os.path.exists(CONFIG_FILE_PATH):
            destination_folder = check_config("DestinationFolder", "")
            steamcmd_path = check_config("SteamCMDPath", os.getcwd())
            new_appearance_mode = check_config("appearance", "Dark")
            new_scaling = check_config("scaling", 1.0)
            self.edit_destination_folder.delete(0, "end")
            self.edit_destination_folder.insert(0, destination_folder)
            self.edit_steamcmd_path.delete(0, "end")
            self.edit_steamcmd_path.insert(0, steamcmd_path)
            ctk.set_appearance_mode(new_appearance_mode)
            ctk.set_widget_scaling(float(new_scaling))
            self.appearance_mode_optionemenu.set(new_appearance_mode)
            scaling_float = float(new_scaling)*100
            scaling_int = math.trunc(scaling_float)
            self.scaling_optionemenu.set(f"{scaling_int}%")
        else:
            new_appearance_mode = check_config("appearance", "Dark")
            new_scaling = check_config("scaling", 1.0)
            ctk.set_appearance_mode(new_appearance_mode)
            ctk.set_widget_scaling(float(new_scaling))
            self.appearance_mode_optionemenu.set(new_appearance_mode)
            scaling_float = float(new_scaling)*100
            scaling_int = math.trunc(scaling_float)
            self.scaling_optionemenu.set(f"{scaling_int}%")
            create_default_config()

    def open_BOIII_browser(self):
        selected_folder = ctk.filedialog.askdirectory(title="Select BOIII Folder")
        if selected_folder:
            self.edit_destination_folder.delete(0, "end")
            self.edit_destination_folder.insert(0, selected_folder)
            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

    def open_steamcmd_path_browser(self):
        selected_folder = ctk.filedialog.askdirectory(title="Select SteamCMD Folder")
        if selected_folder:
            self.edit_steamcmd_path.delete(0, "end")
            self.edit_steamcmd_path.insert(0, selected_folder)
            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

    def show_warning_message(self):
        msg = CTkMessagebox(title="Warning", message="steamcmd.exe was not found in the specified directory.\nPress Download to get it or Press Cancel and select it from there!.",
                            icon="warning", option_1="Cancel", option_2="Download")

        response = msg.get()
        if response == "Cancel":
            return
        elif response == "Download":
            self.download_steamcmd()

    def open_browser(self):
        link = "https://steamcommunity.com/app/311210/workshop/"
        webbrowser.open(link)

    def download_steamcmd(self):
        self.edit_steamcmd_path.delete(0, "end")
        self.edit_steamcmd_path.insert(0, cwd())
        save_config("DestinationFolder" ,self.edit_destination_folder.get())
        save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())
        steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        steamcmd_zip_path = os.path.join(cwd(), "steamcmd.zip")

        try:
            response = requests.get(steamcmd_url)
            response.raise_for_status()

            with open(steamcmd_zip_path, "wb") as zip_file:
                zip_file.write(response.content)

            with zipfile.ZipFile(steamcmd_zip_path, "r") as zip_ref:
                zip_ref.extractall(cwd())

            if check_steamcmd():
                os.remove(fr"{steamcmd_zip_path}")
                if not show_message("Success", "SteamCMD has been downloaded ,Press ok to initialize it.", icon="info", exit_on_close=True):
                    pass
                else:
                    initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                    initialize_steam_thread.start()
            else:
                show_message("Error", "Failed to find steamcmd.exe after extraction.\nMake you sure to select the correct SteamCMD path (by default current BOIIIWD path)", icon="cancel")
                os.remove(fr"{steamcmd_zip_path}")
        except requests.exceptions.RequestException as e:
            show_message("Error", f"Failed to download SteamCMD: {e}", icon="cancel")
            os.remove(fr"{steamcmd_zip_path}")
        except zipfile.BadZipFile:
            show_message("Error", "Failed to extract SteamCMD. The downloaded file might be corrupted.", icon="cancel")
            os.remove(fr"{steamcmd_zip_path}")

    def show_map_info(self):
        def show_map_thread():
            workshop_id = self.edit_workshop_id.get().strip()

            if not workshop_id:
                show_message("Warning", "Please enter a Workshop ID first.")
                return

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Please enter a valid Workshop ID.")
                except:
                    show_message("Warning", "Please enter a valid Workshop ID.")
                    return

            self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))

            try:
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                response = requests.get(url)
                response.raise_for_status()
                content = response.text

                soup = BeautifulSoup(content, "html.parser")

                try:
                    map_mod_type = soup.find("div", class_="rightDetailsBlock").text.strip()
                    map_name = soup.find("div", class_="workshopItemTitle").text.strip()
                    map_size = soup.find("div", class_="detailsStatRight").text.strip()
                except:
                    show_message("Warning", "Please enter a valid Workshop ID.")
                    return

                try:
                    preview_image_element = soup.find("img", id="previewImage")
                    workshop_item_image_url = preview_image_element["src"]
                except:
                    try:
                        preview_image_element = soup.find("img", id="previewImageMain")
                        workshop_item_image_url = preview_image_element["src"]
                    except Exception as e:
                        show_message("Warning", f"Failed to get preview image ,probably wrong link/id if not please open an issue on github.\n{e}")
                        return

                image_response = requests.get(workshop_item_image_url)
                image_response.raise_for_status()

                image = Image.open(io.BytesIO(image_response.content))
                image = image.resize((200, 200), Image.Resampling.LANCZOS)

                self.toplevel_info_window(map_name, map_mod_type, map_size, image)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image):
        top = ctk.CTkToplevel(self)
        top.after(210, lambda: top.iconbitmap("ryuk.ico"))
        top.geometry("340x430")
        top.title("Map/Mod Information")
        top.attributes('-topmost', 'true')

        label = ctk.CTkLabel(top, text="")
        image = ctk.CTkImage(image, size=(260, 200))
        label.configure(image=image)
        label.pack()

        info = (
            f"Name: {map_name}\n"
            f"Type: {map_mod_type}\n"
            f"Size: {map_size}\n"
        )

        text = ctk.CTkLabel(top)
        text.configure(text=info)
        text.pack()

    def download_map(self):
        global stopped
        stopped = False

        save_config("DestinationFolder" ,self.edit_destination_folder.get())
        save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

        if not check_steamcmd():
            self.show_warning_message()
            return

        steamcmd_path = get_steamcmd_path()
        steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")
        steamcmd_size = os.path.getsize(steamcmd_exe_path)
        if steamcmd_size < 3 * 1024 * 1024:
            if not show_message("Warning", "SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.",
                         icon="warning" ,exit_on_close=True):
                pass
            else:
                initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                initialize_steam_thread.start()
            return

        workshop_id = self.edit_workshop_id.get().strip()
        destination_folder = self.edit_destination_folder.get().strip()

        if not workshop_id.isdigit():
            try:
                if extract_workshop_id(workshop_id).strip().isdigit():
                    workshop_id = extract_workshop_id(workshop_id).strip()
                else:
                    show_message("Warning", "Please enter a valid Workshop ID.", icon="warning")
                    return
            except:
                show_message("Warning", "Please enter a valid Workshop ID.", icon="warning")
                return

        file_size = get_workshop_file_size(workshop_id)

        if not valid_id(workshop_id):
            show_message("Warning", "Please enter a valid Workshop ID.", icon="warning")
            return

        if file_size is None:
            show_message("Error", "Failed to retrieve file size.", icon="cancel")
            return

        if not Path(destination_folder).exists() and not destination_folder:
            show_message("Error", "Please select a valid destination folder.")
            return

        if not Path(steamcmd_path).exists() and not steamcmd_path.strip():
            show_message("Error", "Please enter a valid SteamCMD path.")
            return

        self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
        download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
        map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        def check_and_update_progress():
            global stopped
            previous_net_speed = 0

            while not stopped:
                try:
                    current_size = sum(os.path.getsize(os.path.join(download_folder, f)) for f in os.listdir(download_folder))
                except:
                    current_size = sum(os.path.getsize(os.path.join(map_folder, f)) for f in os.listdir(map_folder))

                progress = int(current_size / file_size * 100)
                self.after(1, lambda v=progress / 100.0: self.progress_bar.set(v))

                current_net_speed = psutil.net_io_counters().bytes_recv

                net_speed_bytes = current_net_speed - previous_net_speed
                previous_net_speed = current_net_speed

                net_speed, speed_unit = convert_speed(net_speed_bytes)

                self.after(1, lambda v=net_speed: self.label_speed.configure(text=f"Network Speed: {v:.2f} {speed_unit}"))
                self.after(1, lambda p=progress: self.progress_text.configure(text=f"{p}%"))
                time.sleep(1)

        command = f"+login anonymous +workshop_download_item 311210 {workshop_id} +quit"
        steamcmd_thread = threading.Thread(target=lambda: run_steamcmd_command(command, self))
        steamcmd_thread.start()

        def wait_for_threads():
            update_ui_thread = threading.Thread(target=check_and_update_progress)
            update_ui_thread.daemon = True
            update_ui_thread.start()
            update_ui_thread.join()

            global stopped
            stopped = True

            self.label_speed.configure(text="Network Speed: 0 KB/s")
            self.progress_text.configure(text="0%")
            self.progress_bar.set(0.0)

            map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

            json_file_path = os.path.join(map_folder, "workshop.json")

            if os.path.exists(json_file_path):
                mod_type, folder_name = extract_json_data(json_file_path)

                if mod_type == "mod":
                    mods_folder = os.path.join(destination_folder, "mods")
                    folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                elif mod_type == "map":
                    usermaps_folder = os.path.join(destination_folder, "usermaps")
                    folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                else:
                    show_message("Error", "Invalid map type in workshop.json.", icon="cancel")
                    return

                os.makedirs(folder_name_path, exist_ok=True)

                try:
                    shutil.copytree(map_folder, folder_name_path, dirs_exist_ok=True)
                except Exception as E:
                    show_message("Error", f"Error copying files: {E}", icon="cancel")

                if clean_on_finish:
                    remove_tree(map_folder)
                    remove_tree(download_folder)

                msg = CTkMessagebox(title="Download Complete", message=f"{mod_type.capitalize()} files were downloaded\nYou can run the game now!", icon="info", option_1="Launch", option_2="Ok")
                response = msg.get()
                if response=="Launch":
                    launch_boiii_func(self.edit_destination_folder.get().strip())
                if response=="Ok":
                    pass

                self.button_download.configure(state="normal")
                self.button_stop.configure(state="disabled")

        update_wait_thread = threading.Thread(target=wait_for_threads)
        update_wait_thread.start()

        self.button_download.configure(state="disabled")
        self.button_stop.configure(state="normal")

    def stop_download(self):
        global stopped
        stopped = True

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)

        self.button_download.configure(state="normal")
        self.button_stop.configure(state="disabled")
        self.label_speed.configure(text="Network Speed: 0 KB/s")
        self.progress_text.configure(text="0%")
        self.progress_bar.set(0.0)

if __name__ == "__main__":
    app = BOIIIWD()
    app.mainloop()
