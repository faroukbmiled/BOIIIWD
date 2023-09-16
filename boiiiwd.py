# Use CTkToolTip and CTkListbox from my repo originally by Akascape (https://github.com/Akascape)
from CTkMessagebox import CTkMessagebox
from tkinter import Menu, END, Event
from bs4 import BeautifulSoup
from datetime import datetime
import customtkinter as ctk
from pathlib import Path
from CTkToolTip import *
from CTkListbox import *
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

VERSION = "v0.3.1"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
UPDATER_FOLDER = "update"
CONFIG_FILE_PATH = "config.ini"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')
LIBRARY_FILE = "boiiiwd_library.json"

# Start Helper Functions
def cwd():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def check_config(name, fallback=None):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    if fallback:
        return config.get("Settings", name, fallback=fallback)
    return config.get("Settings", name, fallback="")

def save_config(name, value):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    if name and value:
        config.set("Settings", name, value)
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def check_custom_theme(theme_name):
    if os.path.exists(os.path.join(cwd(), theme_name)):
        return os.path.join(cwd(), theme_name)
    else:
        try:
            return os.path.join(RESOURCES_DIR, theme_name)
        except:
            return os.path.join(RESOURCES_DIR, "boiiiwd_theme.json")

# theme initialization
ctk.set_appearance_mode(check_config("appearance", "Dark"))  # Modes: "System" (standard), "Dark", "Light"
try:
    ctk.set_default_color_theme(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")))
except:
    save_config("theme", "boiiiwd_theme.json")
    ctk.set_default_color_theme(os.path.join(RESOURCES_DIR, "boiiiwd_theme.json"))

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
        int_latest_version = int(latest_version.replace("v", "").replace(".", ""))
        int_current_version = int(current_version.replace("v", "").replace(".", ""))

        if latest_version and int_latest_version > int_current_version:
            msg_box = CTkMessagebox(title="Update Available", message=f"An update is available! Install now?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}", option_1="View", option_2="No", option_3="Yes", fade_in_duration=int(1), sound=True)

            result = msg_box.get()

            if result == "View":
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")

            if result == "Yes":
                update_window = UpdateWindow(window, LATEST_RELEASE_URL)
                update_window.start_update()

            if result == "No":
                return

        elif int_latest_version < int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(title="Up to Date!", message=f"Unreleased version!\nCurrent Version: {current_version}\nLatest Version: {latest_version}", option_1="Ok", sound=True)
            result = msg_box.get()
        elif int_latest_version == int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(title="Up to Date!", message="No Updates Available!", option_1="Ok", sound=True)
            result = msg_box.get()

        else:
            show_message("Error!", "An error occured while checking for updates!\nCheck your internet and try again")

    except Exception as e:
        show_message("Error", f"Error while checking for updates: \n{e}", icon="cancel")

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
        if is_steamcmd_initialized():
            show_message("SteamCMD has terminated!", "BOIIIWD is ready for action.", icon="info")
        else:
            show_message("SteamCMD has terminated!!", "SteamCMD isn't initialized yet")
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

def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback=cwd())

def extract_json_data(json_path, key):
    with open(json_path, 'r') as json_file:
        data = json.load(json_file)
        return data.get(key, '')

def convert_bytes_to_readable(size_in_bytes, no_symb=None):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            if no_symb:
                return f"{size_in_bytes:.2f}"
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

def show_message(title, message, icon="warning", _return=False, option_1="No", option_2="Ok"):
    if _return:
        msg = CTkMessagebox(title=title, message=message, icon=icon, option_1=option_1, option_2=option_2, sound=True)
        response = msg.get()
        if response == option_1:
            return False
        elif response == option_2:
            return True
        else:
            return False
    else:
        def callback():
            CTkMessagebox(title=title, message=message, icon=icon, sound=True)
        app.after(0, callback)

def launch_boiii_func(path):
    procname = "boiii.exe"
    try:
        if procname in (p.name() for p in psutil.process_iter()):
            for proc in psutil.process_iter():
                if proc.name() == procname:
                    proc.kill()
        boiii_path = os.path.join(path, procname)
        subprocess.Popen([boiii_path ,"-launch"] , cwd=path)
        show_message("Please wait!", "The game has launched in the background it will open up in a sec!", icon="info")
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

def convert_seconds(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, seconds

def get_folder_size(folder_path):
    total_size = 0
    for path, dirs, files in os.walk(folder_path):
        for f in files:
            fp = os.path.join(path, f)
            total_size += os.stat(fp).st_size
    return total_size

def is_steamcmd_initialized():
    steamcmd_path = get_steamcmd_path()
    steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")
    steamcmd_size = os.path.getsize(steamcmd_exe_path)
    if steamcmd_size < 3 * 1024 * 1024:
        return False
    return True

def get_button_state_colors(file_path, state):
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            if 'BOIIIWD_Globals' in data:
                boiiiwd_globals = data['BOIIIWD_Globals']
                if state in boiiiwd_globals:
                    return boiiiwd_globals[state]
                else:
                    return None
            else:
                return None
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

def reset_steamcmd(no_warn=None):
    steamcmd_path = get_steamcmd_path()
    steamcmd_steamapps = os.path.join(steamcmd_path, "steamapps")
    if os.path.exists(steamcmd_steamapps):
        remove_tree(steamcmd_steamapps, show_error=True)
        if not no_warn:
            show_message("Success!", "SteamCMD has been reset successfully!", icon="info")
    else:
        if not no_warn:
            show_message("Warning!", "steamapps folder was not found, maybe already removed?", icon="warning")

def get_item_name(id):
    try:
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={id}"
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        soup = BeautifulSoup(content, "html.parser")

        try:
            map_name = soup.find("div", class_="workshopItemTitle").text.strip()
            name = map_name[:32] + "..." if len(map_name) > 32 else map_name
            return name
        except:
            return True
    except:
        return False

# you gotta use my modded CTkToolTip originaly by Akascape
def show_noti(widget ,message, event=None, noti_dur=3.0, topmost=False):
    CTkToolTip(widget, message=message, is_noti=True, noti_event=event, noti_dur=noti_dur, topmost=topmost)

def check_item_date(down_date, date_updated):
    current_year = datetime.now().year
    date_format_with_year = "%d %b, %Y @ %I:%M%p"
    date_format_with_added_year = "%d %b @ %I:%M%p, %Y"
    try:
        try:
            download_datetime = datetime.strptime(down_date, date_format_with_year)
        except ValueError:
            download_datetime = datetime.strptime(down_date + f", {current_year}", date_format_with_added_year)

        try:
            upload_datetime = datetime.strptime(date_updated, date_format_with_year)
        except ValueError:
            upload_datetime = datetime.strptime(date_updated + f", {current_year}", date_format_with_added_year)

        if upload_datetime >= download_datetime:
            return True
        elif upload_datetime < download_datetime:
            return False
    except:
        return False

# End helper functions
class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, update_url):
        global master_win
        master_win = master
        super().__init__(master)
        self.title("BOIIIWD Self-Updater")
        self.geometry("400x150")
        if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
            self.after(250, lambda: self.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
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

        self.progress_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "progress_bar_fill_color")
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", height=20, corner_radius=7, progress_color=self.progress_color)
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
                def update_msg():
                    msg = CTkMessagebox(title="Success!", message="Update Downloaded successfully!\nPress ok to install it", icon="info", option_1="No", option_2="Ok", sound=True)
                    response = msg.get()
                    if response == "No":
                        self.destroy()
                        return
                    elif response == "Ok":
                        script_path = create_update_script(current_exe, new_exe, update_dir, program_name)
                        subprocess.run(('cmd', '/C', 'start', '', fr'{script_path}'))
                        sys.exit(0)
                    else:
                        return
                self.after(0, update_msg)
                return
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

class LibraryTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.added_items = set()
        self.to_update = set()
        self.grid_columnconfigure(0, weight=1)

        self.radiobutton_variable = ctk.StringVar()
        self.no_items_label = ctk.CTkLabel(self, text="", anchor="w")
        self.filter_entry = ctk.CTkEntry(self, placeholder_text="Your search query here, or type in mod or map to only see that")
        self.filter_entry.bind("<KeyRelease>", self.filter_items)
        self.filter_entry.grid(row=0, column=0,  padx=(10, 20), pady=(10, 20), sticky="we")
        filter_refresh_button_image = os.path.join(RESOURCES_DIR, "Refresh_icon.svg.png")
        update_button_image = os.path.join(RESOURCES_DIR, "update_icon.png")
        self.filter_refresh_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(filter_refresh_button_image)), command=self.refresh_items, width=20, height=20,
                                                   fg_color="transparent", text="")
        self.filter_refresh_button.grid(row=0, column=1, padx=(10, 0), pady=(10, 20), sticky="nw")
        self.update_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(update_button_image)), command=self.check_for_updates, width=65, height=20,
                                           text="", fg_color="transparent")
        self.update_button.grid(row=0, column=1, padx=(0, 20), pady=(10, 20), sticky="en")
        self.update_tooltip = CTkToolTip(self.update_button, message="Check items for updates", topmost=True)
        filter_tooltip = CTkToolTip(self.filter_refresh_button, message="Refresh library", topmost=True)
        self.label_list = []
        self.button_list = []
        self.folders_to_rename = []
        self.button_view_list = []
        self.filter_type = True
        self.clipboard_has_content = False

    def add_item(self, item, image=None, workshop_id=None, folder=None):
        label = ctk.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text="Remove", width=60, height=24, fg_color="#3d3f42")
        button_view = ctk.CTkButton(self, text="Details", width=55, height=24, fg_color="#3d3f42")
        button.configure(command=lambda: self.remove_item(item, folder, workshop_id))
        button_view.configure(command=lambda: self.show_map_info(workshop_id))
        button_view_tooltip = CTkToolTip(button_view, message="Opens up a window that shows basic details")
        button_tooltip = CTkToolTip(button, message="Removes the map/mod from your game")
        label.grid(row=len(self.label_list) + 1, column=0, pady=(0, 10), padx=(5, 10), sticky="w")
        button.grid(row=len(self.button_list) + 1, column=1, pady=(0, 10), padx=(50, 10), sticky="e")
        button_view.grid(row=len(self.button_view_list) + 1, column=1, pady=(0, 10), padx=(10, 75), sticky="w")
        self.label_list.append(label)
        self.button_list.append(button)
        self.button_view_list.append(button_view)
        label.bind("<Enter>", lambda event, label=label: self.on_label_hover(label, enter=True))
        label.bind("<Leave>", lambda event, label=label: self.on_label_hover(label, enter=False))
        label.bind("<Button-1>", lambda event, label=label: self.copy_to_clipboard(label, workshop_id, event))
        label.bind("<Control-Button-1>", lambda event, label=label: self.copy_to_clipboard(label, workshop_id, event, append=True))
        label.bind("<Button-2>", lambda event: self.open_folder_location(folder, event))
        label.bind("<Button-3>", lambda event, label=label: self.copy_to_clipboard(label, folder, event))

    def on_label_hover(self, label, enter):
        if enter:
            label.configure(fg_color="#272727")
        else:
            label.configure(fg_color="transparent")

    def copy_to_clipboard(self, label, something, event=None, append=False):
        try:
            if append:
                if self.clipboard_has_content:
                    label.clipboard_append(f"\n{something}")
                    show_noti(label, "Appended to clipboard", event, 1.0)
                else:
                    label.clipboard_clear()
                    label.clipboard_append(something)
                    self.clipboard_has_content = True
                    show_noti(label, "Copied to clipboard", event, 1.0)
            else:
                label.clipboard_clear()
                label.clipboard_append(something)
                self.clipboard_has_content = True
                show_noti(label, "Copied to clipboard", event, 1.0)
        except:
            pass

    def open_folder_location(self, folder, event=None):
        if os.path.exists(folder):
            os.startfile(folder)
            show_noti(self, "Opening folder", event, 1.0)

    def item_exists_in_file(self, items_file, workshop_id):
        if not os.path.exists(items_file):
            return False

        with open(items_file, "r") as f:
            items_data = json.load(f)
            for item_info in items_data:
                if item_info["id"] == workshop_id:
                    return True
        return False

    def remove_item_by_id(self, items_file, item_id):

        items_file_ = os.path.join(cwd(), items_file)

        if not os.path.exists(items_file_):
            return

        with open(items_file_, "r") as f:
            items_data = json.load(f)

        updated_items_data = [item for item in items_data if item.get("id") != item_id]

        if len(updated_items_data) < len(items_data):
            with open(items_file_, "w") as f:
                json.dump(updated_items_data, f, indent=4)

    def get_item_by_id(self, items_file, item_id, return_option="all"):
        items_file_ = os.path.join(cwd(), items_file)

        if not os.path.exists(items_file_):
            return None

        with open(items_file_, "r") as f:
            items_data = json.load(f)

        for item in items_data:
            if item.get("id") == item_id:
                if return_option == "all":
                    return item
                elif return_option == return_option:
                    return item.get(return_option)
        return None

    def get_item_index_by_id(self, items_data, item_id):
        for index, item in enumerate(items_data):
            if item.get("id") == item_id:
                return index
        return None

    def update_or_add_item_by_id(self, items_file, item_info, item_id):
        if not os.path.exists(items_file):
            with open(items_file, "w") as f:
                json.dump([item_info], f, indent=4)
        else:
            with open(items_file, "r+") as f:
                items_data = json.load(f)
                existing_item_index = self.get_item_index_by_id(items_data, item_id)
                if existing_item_index is not None:
                    items_data[existing_item_index] = item_info
                else:
                    items_data.append(item_info)
                f.seek(0)
                f.truncate()
                json.dump(items_data, f, indent=4)

    def filter_items(self, event):
        filter_text = self.filter_entry.get().lower()
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            item_text = label.cget("text").lower()
            if filter_text in item_text:
                label.grid()
                button.grid()
                button_view_list.grid()
            else:
                label.grid_remove()
                button_view_list.grid_remove()
                button.grid_remove()

    def load_items(self, boiiiFolder):
        maps_folder = Path(boiiiFolder) / "mods"
        mods_folder = Path(boiiiFolder) / "usermaps"
        mod_img = os.path.join(RESOURCES_DIR, "mod_image.png")
        map_img = os.path.join(RESOURCES_DIR, "map_image.png")
        map_count = 0
        mod_count = 0
        total_size = 0

        folders_to_process = [mods_folder, maps_folder]

        for folder_path in folders_to_process:
            for zone_path in folder_path.glob("**/zone"):
                json_path = zone_path / "workshop.json"
                if json_path.exists():
                    workshop_id = extract_json_data(json_path, "PublisherID")

                    if folder_path.name != workshop_id:
                        self.folders_to_rename.append((zone_path.parent, folder_path / workshop_id))

                    name = extract_json_data(json_path, "Title").replace(">", "").replace("^", "")
                    name = name[:45] + "..." if len(name) > 45 else name
                    item_type = extract_json_data(json_path, "Type")
                    folder_name = extract_json_data(json_path, "FolderName")
                    folder_size_bytes = get_folder_size(zone_path.parent)
                    size = convert_bytes_to_readable(folder_size_bytes)
                    total_size += folder_size_bytes
                    text_to_add = f"{name} | Type: {item_type.capitalize()}"
                    mode_type = "ZM" if item_type == "map" and folder_name.startswith("zm") else "MP" if folder_name.startswith("mp") and item_type == "map" else None
                    if mode_type:
                        text_to_add += f" | Mode: {mode_type}"
                    text_to_add += f" | ID: {workshop_id} | Size: {size}"

                    folder_creation_timestamp = zone_path.stat().st_ctime
                    date_added = datetime.fromtimestamp(folder_creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")
                    items_file = os.path.join(cwd(), LIBRARY_FILE)
                    if text_to_add not in self.added_items:
                        self.added_items.add(text_to_add)
                        image_path = mod_img if item_type == "mod" else map_img
                        map_count += 1 if item_type == "map" else 0
                        mod_count += 1 if item_type == "mod" else 0
                        self.add_item(text_to_add, image=ctk.CTkImage(Image.open(image_path)), workshop_id=workshop_id, folder=zone_path.parent)

                        if not self.item_exists_in_file(items_file, workshop_id):
                            item_info = {
                                "id": workshop_id,
                                "text": text_to_add,
                                "date": date_added
                            }

                            if not os.path.exists(items_file):
                                with open(items_file, "w") as f:
                                    json.dump([item_info], f, indent=4)
                            else:
                                with open(items_file, "r+") as f:
                                    items_data = json.load(f)
                                    items_data.append(item_info)
                                    f.seek(0)
                                    json.dump(items_data, f, indent=4)

        if len(self.folders_to_rename) > 1:
            # well the program hangs for too long on some systems so i had to do this instead
            def update_folder_names_thread():
                for folder_path, workshop_id in self.folders_to_rename:
                    try:
                        os.rename(folder_path, workshop_id)
                    except Exception as e:
                        show_message(f"Failed to rename folder from '{folder_path}' to '{workshop_id}'",
                                    f"{e}\nPlease restart the program and go to the library tab to fix the issue!", icon="cancel")
                self.folders_to_rename.clear()
            threading.Thread(target=update_folder_names_thread).start()

        if not self.added_items:
            self.show_no_items_message()
        else:
            self.hide_no_items_message()

        return f"Maps: {map_count} - Mods: {mod_count} - Total size: {convert_bytes_to_readable(total_size)}"

    def update_item(self, boiiiFolder, id, item_type, folder_name):
        try:
            if item_type == "map":
                folder_path = Path(boiiiFolder) / "usermaps" / f"{folder_name}"
            elif item_type == "mod":
                folder_path = Path(boiiiFolder) / "mods" / f"{folder_name}"
            else:
                raise ValueError("Unsupported item_type. It must be 'map' or 'mod'.")

            for zone_path in folder_path.glob("**/zone"):
                json_path = zone_path / "workshop.json"
                if json_path.exists():
                    workshop_id = extract_json_data(json_path, "PublisherID")
                    if workshop_id == id:
                        name = extract_json_data(json_path, "Title").replace(">", "").replace("^", "")
                        name = name[:45] + "..." if len(name) > 45 else name
                        item_type = extract_json_data(json_path, "Type")
                        folder_name = extract_json_data(json_path, "FolderName")
                        size = convert_bytes_to_readable(get_folder_size(zone_path.parent))
                        text_to_add = f"{name} | Type: {item_type.capitalize()}"
                        mode_type = "ZM" if item_type == "map" and folder_name.startswith("zm") else "MP" if folder_name.startswith("mp") and item_type == "map" else None
                        if mode_type:
                            text_to_add += f" | Mode: {mode_type}"
                        text_to_add += f" | ID: {workshop_id} | Size: {size}"
                        date_added = datetime.now().strftime("%d %b, %Y @ %I:%M%p")
                        items_file = os.path.join(cwd(), LIBRARY_FILE)

                        item_info = {
                            "id": workshop_id,
                            "text": text_to_add,
                            "date": date_added
                        }
                        self.update_or_add_item_by_id(items_file, item_info, id)
                        return

        except Exception as e:
            show_message("Error updating json file", f"Error while updating library json file\n{e}")

    def remove_item(self, item, folder, id):
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            if item == label.cget("text"):
                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    show_message("Error" ,f"Error removing folder '{folder}': {e}", icon="cancel")
                    return
                label.destroy()
                button.destroy()
                button_view_list.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                self.added_items.remove(label.cget("text"))
                self.button_view_list.remove(button_view_list)
                self.remove_item_by_id(LIBRARY_FILE, id)

    def refresh_items(self):
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            label.destroy()
            button.destroy()
            button_view_list.destroy()
        self.label_list.clear()
        self.button_list.clear()
        self.button_view_list.clear()
        self.added_items.clear()
        self.load_items(app.edit_destination_folder.get().strip())

    def view_item(self, workshop_id):
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        webbrowser.open(url)

    def show_no_items_message(self):
        self.no_items_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="n")
        self.no_items_label.configure(text="No items found in the selected folder. \nMake sure you have a mod/map downloaded and or have the right boiii folder selected.")

    def hide_no_items_message(self):
        self.no_items_label.configure(text="")
        self.no_items_label.forget()

    # i know i know ,please make a pull request i cant be bother
    def show_map_info(self, workshop):
        for button_view in self.button_view_list:
            button_view.configure(state="disabled")

        def show_map_thread():
            workshop_id = workshop

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Not a valid Workshop ID.")
                except:
                    show_message("Warning", "Not a valid Workshop ID.")
                    return
            try:
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                response = requests.get(url)
                response.raise_for_status()
                content = response.text

                soup = BeautifulSoup(content, "html.parser")

                try:
                    map_mod_type = soup.find("div", class_="rightDetailsBlock").text.strip()
                    map_name = soup.find("div", class_="workshopItemTitle").text.strip()
                    map_size = map_size = get_workshop_file_size(workshop_id, raw=True)
                    details_stats_container = soup.find("div", class_="detailsStatsContainerRight")
                    details_stat_elements = details_stats_container.find_all("div", class_="detailsStatRight")
                    date_created = details_stat_elements[1].text.strip()
                    try:
                        ratings = soup.find('div', class_='numRatings')
                        ratings_text = ratings.get_text()
                    except:
                        ratings = "Not found"
                        ratings_text= "Not enough ratings"
                    try:
                        date_updated = details_stat_elements[2].text.strip()
                    except:
                        date_updated = "Not updated"
                    stars_div = soup.find("div", class_="fileRatingDetails")
                    starts = stars_div.find("img")["src"]
                except:
                    show_message("Warning", "Not a valid Workshop ID\nCouldn't get information.")
                    for button_view in self.button_view_list:
                        button_view.configure(state="normal")
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
                        for button_view in self.button_view_list:
                            button_view.configure(state="normal")
                        return

                starts_image_response = requests.get(starts)
                stars_image = Image.open(io.BytesIO(starts_image_response.content))
                stars_image_size = stars_image.size

                image_response = requests.get(workshop_item_image_url)
                image_response.raise_for_status()
                image = Image.open(io.BytesIO(image_response.content))
                image_size = image.size

                self.toplevel_info_window(map_name, map_mod_type, map_size, image, image_size, date_created,
                                        date_updated, stars_image, stars_image_size, ratings_text, url, workshop_id)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
                return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size, ratings_text, url, workshop_id):
        def main_thread():
            try:
                top = ctk.CTkToplevel(self)
                if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                    top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
                top.title("Map/Mod Information")
                top.attributes('-topmost', 'true')
                down_date = self.get_item_by_id(LIBRARY_FILE, workshop_id, 'date')

                def close_window():
                    top.destroy()

                def view_map_mod():
                    webbrowser.open(url)

                def check_for_updates():
                    try:

                        if check_item_date(down_date, date_updated):
                            if show_message("There is an update.", "Press download to redownload!", icon="info", _return=True, option_1="No", option_2="Download"):
                                if app.is_downloading:
                                    show_message("Error", "Please wait for the current download to finish or stop it then restart.", icon="cancel")
                                    return
                                app.edit_workshop_id.delete(0, "end")
                                app.edit_workshop_id.insert(0, workshop_id)
                                app.main_button_event()
                                app.download_map(update=True)
                                top.destroy()
                                return
                        else:
                            show_message("Up to date!", "No updates found!", icon="info")
                    except:
                        show_message("Up to date!", "No updates found!", icon="info")

                # frames
                stars_frame = ctk.CTkFrame(top)
                stars_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="nsew")
                stars_frame.columnconfigure(0, weight=0)
                stars_frame.rowconfigure(0, weight=1)

                image_frame = ctk.CTkFrame(top)
                image_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=0, sticky="nsew")

                info_frame = ctk.CTkFrame(top)
                info_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

                buttons_frame = ctk.CTkFrame(top)
                buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

                # fillers
                name_label = ctk.CTkLabel(info_frame, text=f"Name: {map_name}")
                name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                type_label = ctk.CTkLabel(info_frame, text=f"Type: {map_mod_type}")
                type_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                size_label = ctk.CTkLabel(info_frame, text=f"Size (Workshop): {map_size}")
                size_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                date_created_label = ctk.CTkLabel(info_frame, text=f"Posted: {date_created}")
                date_created_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}")
                date_updated_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                date_updated_label = ctk.CTkLabel(info_frame, text=f"Downloaded at: {down_date}")
                date_updated_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                stars_image_label = ctk.CTkLabel(stars_frame)
                stars_width, stars_height = stars_image_size
                stars_image_widget = ctk.CTkImage(stars_image, size=(int(stars_width), int(stars_height)))
                stars_image_label.configure(image=stars_image_widget, text="")
                stars_image_label.pack(side="left", padx=(10, 20), pady=(10, 10))

                ratings = ctk.CTkLabel(stars_frame)
                ratings.configure(text=ratings_text)
                ratings.pack(side="right", padx=(10, 20), pady=(10, 10))

                image_label = ctk.CTkLabel(image_frame)
                width, height = image_size
                image_widget = ctk.CTkImage(image, size=(int(width), int(height)))
                image_label.configure(image=image_widget, text="")
                image_label.pack(expand=True, fill="both", padx=(10, 20), pady=(10, 10))

                # Buttons
                close_button = ctk.CTkButton(buttons_frame, text="View", command=view_map_mod, width=130)
                close_button.grid(row=0, column=0, padx=(20, 20), pady=(10, 10), sticky="n")

                update_btn = ctk.CTkButton(buttons_frame, text="Update", command=check_for_updates, width=130)
                update_btn.grid(row=0, column=1, padx=(10, 20), pady=(10, 10), sticky="n")
                update_btn_tooltip = CTkToolTip(update_btn, message="Checks and installs updates of the current selected item (redownload!)", topmost=True)

                view_button = ctk.CTkButton(buttons_frame, text="Close", command=close_window, width=130)
                view_button.grid(row=0, column=2, padx=(10, 20), pady=(10, 10), sticky="n")

                top.grid_rowconfigure(0, weight=0)
                top.grid_rowconfigure(1, weight=0)
                top.grid_rowconfigure(2, weight=1)
                top.grid_columnconfigure(0, weight=1)
                top.grid_columnconfigure(1, weight=1)

                buttons_frame.grid_rowconfigure(0, weight=1)
                buttons_frame.grid_rowconfigure(1, weight=1)
                buttons_frame.grid_rowconfigure(2, weight=1)
                buttons_frame.grid_columnconfigure(0, weight=1)
                buttons_frame.grid_columnconfigure(1, weight=1)
                buttons_frame.grid_columnconfigure(2, weight=1)

            finally:
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
        self.after(0, main_thread)

    def check_for_updates(self, on_launch=False):
        self.after(1, self.update_button.configure(state="disabled"))
        self.update_tooltip.configure(message='Still loading please wait...')
        cevent = Event()
        cevent.x_root = self.update_button.winfo_rootx()
        cevent.y_root = self.update_button.winfo_rooty()
        if not on_launch:
            show_noti(self.update_button, "Please wait, window will popup shortly", event=cevent, noti_dur=3.0, topmost=True)
        threading.Thread(target=self.check_items_func, args=(on_launch,)).start()

    def items_update_message(self, to_update_len):
        def main_thread():
            if show_message(f"{to_update_len} Item updates available", f"{to_update_len} Workshop Items have an update, Would you like to open the item updater window?", icon="info", _return=True):
                app.after(1, self.update_items_window)
            else:
                return
        app.after(0, main_thread)
        self.update_button.configure(state="normal", width=65, height=20)
        self.update_tooltip.configure(message='Check items for updates')
        return

    def check_items_func(self, on_launch):
        # Needed to refresh item that needs updates
        self.to_update.clear()

        def if_id_needs_update(item_id, item_date, text):
            try:
                headers = {'Cache-Control': 'no-cache'}
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={item_id}"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                content = response.text
                soup = BeautifulSoup(content, "html.parser")
                details_stats_container = soup.find("div", class_="detailsStatsContainerRight")
                details_stat_elements = details_stats_container.find_all("div", class_="detailsStatRight")
                try:
                    date_updated = details_stat_elements[2].text.strip()
                except:
                    try:
                        date_updated = details_stat_elements[1].text.strip()
                    except:
                        return False

                if check_item_date(item_date, date_updated):
                    self.to_update.add(text + f" | Updated: {date_updated}")
                    return True
                else:
                    return False

            except Exception as e:
                show_message("Error", f"Error occured\n{e}", icon="cancel")
                return

        def check_for_update():
            lib_data = None

            if not os.path.exists(os.path.join(cwd(), LIBRARY_FILE)):
                show_message("Error checking for item updates! -> Setting is on", "Please visit library tab at least once with the correct boiii path!, you also need to have at lease 1 item!")
                return

            with open(LIBRARY_FILE, 'r') as file:
                lib_data = json.load(file)

            for item in lib_data:
                item_id = item["id"]
                item_date = item["date"]
                if_id_needs_update(item_id, item_date, item["text"])

        check_for_update()

        to_update_len = len(self.to_update)
        if to_update_len > 0:
            self.items_update_message(to_update_len)
        else:
            self.update_button.configure(state="normal", width=65, height=20)
            self.update_tooltip.configure(message='Check items for updates')
            if not on_launch:
                show_message("No updates found!", "Items are up to date!", icon="info")

    def update_items_window(self):
        try:
            top = ctk.CTkToplevel(master=None)
            top.withdraw()
            if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            top.title("Item updater - List of Items with Updates - Click to select 1 or more")
            longest_text_length = max(len(text) for text in self.to_update)
            window_width = longest_text_length * 6 + 5
            top.geometry(f"{window_width}x450")
            top.attributes('-topmost', 'true')
            top.resizable(True, True)
            selected_id_list = []
            cevent = Event()
            self.select_all_bool = False

            listbox = CTkListbox(top, multiple_selection=True)
            listbox.grid(row=0, column=0, sticky="nsew")

            update_button = ctk.CTkButton(top, text="Update")
            update_button.grid(row=1, column=0, pady=10, padx=5, sticky='ns')

            select_button = ctk.CTkButton(top, text="Select All", width=5)
            select_button.grid(row=1, column=0, pady=10, padx=(230, 0), sticky='ns')

            def open_url(id_part, e=None):
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={id_part}"
                webbrowser.open(url)

            # you gotta use my modded CTkListbox originaly by Akascape
            def add_checkbox_item(index, item_text):
                parts = item_text.split('ID: ')
                id_part = parts[1].split('|')[0].strip()
                listbox.insert(index, item_text, keybind="<Button-3>", func=lambda e: open_url(id_part))

            def load_items():
                for index, item_text in enumerate(self.to_update):
                    if index == len(self.to_update) - 1:
                        add_checkbox_item("end", item_text)
                        top.deiconify()
                        return
                    add_checkbox_item(index, item_text)

            def update_list(selected_option):
                selected_id_list.clear()

                if selected_option:
                    for option in selected_option:
                        parts = option.split('ID: ')
                        if len(parts) > 1:
                            id_part = parts[1].split('|')[0].strip()
                            selected_id_list.append(id_part)

            def select_all():
                if self.select_all_bool:
                    listbox.deactivate("all")
                    update_list(listbox.get())
                    self.select_all_bool = False
                    return
                listbox.deactivate("all")
                listbox.activate("all")
                update_list(listbox.get())
                self.select_all_bool = True

            def update_btn_fun():
                if len(selected_id_list) == 1:
                    if app.is_downloading:
                        show_message("Error", "Please wait for the current download to finish or stop it then start.", icon="cancel")
                        return
                    app.edit_workshop_id.delete(0, "end")
                    app.edit_workshop_id.insert(0, selected_id_list[0])
                    app.main_button_event()
                    app.download_map(update=True)
                    top.destroy()
                    return

                elif len(selected_id_list) > 1:
                    if app.is_downloading:
                        show_message("Error", "Please wait for the current download to finish or stop it then start.", icon="cancel")
                        return
                    comma_separated_ids = ",".join(selected_id_list)
                    app.queuetextarea.delete("1.0", "end")
                    app.queuetextarea.insert("1.0", comma_separated_ids)
                    app.queue_button_event()
                    app.download_map(update=True)
                    top.destroy()
                    return

                else:
                    cevent.x_root = update_button.winfo_rootx()
                    cevent.y_root = update_button.winfo_rooty()
                    show_noti(update_button ,"Please select 1 or more items", event=cevent, noti_dur=0.8, topmost=True)


            listbox.configure(command=update_list)
            update_button.configure(command=update_btn_fun)
            select_button.configure(command=select_all)

            top.grid_rowconfigure(0, weight=1)
            top.grid_columnconfigure(0, weight=1)

            load_items()

        except Exception as e:
            show_message("Error", f"{e}", icon="cancel")

        finally:
            self.update_button.configure(state="normal", width=65, height=20)
            self.update_tooltip.configure(message='Check items for updates')

class SettingsTab(ctk.CTkFrame):
    def __init__(self, master=None):
        super().__init__(master)
        # settings default bools
        self.skip_already_installed = True
        self.stopped = False
        self.console = False
        self.clean_on_finish = True
        self.continuous = True
        self.estimated_progress = True
        self.steam_fail_counter_toggle = True
        self.steam_fail_counter = 0
        self.steam_fail_number = 10
        self.steamcmd_reset = False
        self.show_fails = True
        self.check_items_on_launch = False

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

        # Show continuous checkbox
        self.continuous_var = ctk.BooleanVar()
        self.continuous_var.trace_add("write", self.enable_save_button)
        self.checkbox_continuous = ctk.CTkSwitch(left_frame, text="Continuous Download", variable=self.continuous_var)
        self.checkbox_continuous.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.checkbox_continuous_tooltip = CTkToolTip(self.checkbox_continuous, message="This will make sure that the download restarts and resumes! until it finishes if steamcmd crashes randomly (it will not redownload from the start)")
        self.continuous_var.set(self.load_settings("continuous_download"))

        # clean on finish checkbox
        self.clean_checkbox_var = ctk.BooleanVar()
        self.clean_checkbox_var.trace_add("write", self.enable_save_button)
        self.clean_checkbox = ctk.CTkSwitch(left_frame, text="Clean on finish", variable=self.clean_checkbox_var)
        self.clean_checkbox.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.clean_checkbox_tooltip = CTkToolTip(self.clean_checkbox, message="Cleans the map that have been downloaded and installed from steamcmd's steamapps folder ,to save space")
        self.clean_checkbox_var.set(self.load_settings("clean_on_finish", "on"))

        # Show estimated_progress checkbox
        self.estimated_progress_var = ctk.BooleanVar()
        self.estimated_progress_var.trace_add("write", self.enable_save_button)
        self.estimated_progress_cb = ctk.CTkSwitch(left_frame, text="Estimated Progress Bar", variable=self.estimated_progress_var)
        self.estimated_progress_cb.grid(row=4, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.estimated_progress_var_tooltip = CTkToolTip(self.estimated_progress_cb, message="This will change how to progress bar works by estimating how long the download will take\
            \nThis is not accurate ,it's better than with it off which is calculating the downloaded folder size which steamcmd dumps the full size rigth mostly")
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))

        # Show show fails checkbox
        self.show_fails_var = ctk.BooleanVar()
        self.show_fails_var.trace_add("write", self.enable_save_button)
        self.show_fails_cb = ctk.CTkSwitch(left_frame, text="Show fails (on top of progress bar)", variable=self.show_fails_var)
        self.show_fails_cb.grid(row=5, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.show_fails_tooltip = CTkToolTip(self.show_fails_cb, message="Display how many times steamcmd has failed/crashed\nIf the number is getting high quickly then try pressing Reset SteamCMD and try again, otherwise its fine")
        self.estimated_progress_var.set(self.load_settings("show_fails", "on"))

        # Show skip_already_installed maps checkbox
        self.skip_already_installed_var = ctk.BooleanVar()
        self.skip_already_installed_var.trace_add("write", self.enable_save_button)
        self.skip_already_installed_ch = ctk.CTkSwitch(left_frame, text="Skip already installed maps", variable=self.skip_already_installed_var)
        self.skip_already_installed_ch.grid(row=6, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.skip_already_installed_ch_tooltip = CTkToolTip(self.skip_already_installed_ch, message="If on it will not download installed maps,\nthis can miss sometimes if you remove maps manually and not from library tab while the app is running")
        self.skip_already_installed_var.set(self.load_settings("skip_already_installed", "on"))

        # check items for update on launch
        self.check_items_var = ctk.BooleanVar()
        self.check_items_var.trace_add("write", self.enable_save_button)
        self.check_items_ch = ctk.CTkSwitch(left_frame, text="Check Library items on launch", variable=self.check_items_var)
        self.check_items_ch.grid(row=7, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.check_items_tooltip = CTkToolTip(self.check_items_ch, message="This will show a window on launch of items that have pending updates -> you can open it manually from library tab")
        self.check_items_var.set(self.load_settings("check_items", "off"))

        # Resetr steam on many fails
        self.reset_steamcmd_on_fail_var = ctk.IntVar()
        self.reset_steamcmd_on_fail_var.trace_add("write", self.enable_save_button)
        self.reset_steamcmd_on_fail_text = ctk.CTkLabel(left_frame, text=f"Reset steamcmd on % fails: (n of fails)", anchor="w")
        self.reset_steamcmd_on_fail_text.grid(row=8, column=1, padx=20, pady=(10, 0), sticky="nw")
        self.reset_steamcmd_on_fail = ctk.CTkOptionMenu(left_frame, values=["5", "10", "20", "30", "40", "Custom", "Disable"], variable=self.reset_steamcmd_on_fail_var, command=self.reset_steamcmd_on_fail_func)
        self.reset_steamcmd_on_fail.grid(row=9, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.reset_steamcmd_on_fail_tooltip = CTkToolTip(self.reset_steamcmd_on_fail, message="This actually fixes steamcmd when its crashing way too much")
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))

        # Check for updates button n Launch boiii
        self.check_for_updates = ctk.CTkButton(right_frame, text="Check for updates", command=self.settings_check_for_updates)
        self.check_for_updates.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="n")

        self.launch_boiii = ctk.CTkButton(right_frame, text="Launch boiii", command=self.settings_launch_boiii)
        self.launch_boiii.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="n")

        self.reset_steamcmd = ctk.CTkButton(right_frame, text="Reset SteamCMD", command=self.settings_reset_steamcmd)
        self.reset_steamcmd.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="n")
        self.reset_steamcmd_tooltip = CTkToolTip(self.reset_steamcmd, message="This will remove steamapps folder + all the maps that are potentioaly corrupted\nor not so use at ur own risk (could fix some issues as well)")

        self.steam_to_boiii = ctk.CTkButton(right_frame, text="Steam to Boiii", command=self.from_steam_to_boiii_toplevel)
        self.steam_to_boiii.grid(row=5, column=1, padx=20, pady=(20, 0), sticky="n")
        self.steam_to_boiii_tooltip = CTkToolTip(self.steam_to_boiii, message="Moves/copies maps and mods from steam to boiii (opens up a window)")

        # appearance
        self.appearance_mode_label = ctk.CTkLabel(right_frame, text="Appearance Mode:", anchor="n")
        self.appearance_mode_label.grid(row=6, column=1, padx=20, pady=(20, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(right_frame, values=["Light", "Dark", "System"],
                                                                       command=master.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=1, padx=20, pady=(0, 0))
        self.scaling_label = ctk.CTkLabel(right_frame, text="UI Scaling:", anchor="n")
        self.scaling_label.grid(row=8, column=1, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(right_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=master.change_scaling_event)
        self.scaling_optionemenu.grid(row=9, column=1, padx=20, pady=(0, 0))

        # self.custom_theme = ctk.CTkButton(right_frame, text="Custom theme", command=self.boiiiwd_custom_theme)
        # self.custom_theme.grid(row=8, column=1, padx=20, pady=(20, 0), sticky="n")

        self.theme_options_label = ctk.CTkLabel(right_frame, text="Themes:", anchor="n")
        self.theme_options_label.grid(row=10, column=1, padx=20, pady=(10, 0))
        self.theme_options = ctk.CTkOptionMenu(right_frame, values=["Default", "Blue", "Grey", "Obsidian", "Ghost","NeonBanana", "Custom"],
                                                               command=self.theme_options_func)
        self.theme_options.grid(row=11, column=1, padx=20, pady=(0, 0))
        self.theme_options.set(value=self.load_settings("theme", "Default"))

        # Save button
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_settings, state='disabled')
        self.save_button.grid(row=3, column=0, padx=20, pady=(20, 20), sticky="nw")

        #version
        self.version_info = ctk.CTkLabel(self, text=f"{VERSION}")
        self.version_info.grid(row=3, column=1, padx=20, pady=(20, 20), sticky="e")

    def reset_steamcmd_on_fail_func(self, option: str):
        if option == "Custom":
            try:
                save_config("reset_on_fail", "10")
                def callback():
                    msg = CTkMessagebox(title="config.ini", message="change reset_on_fail value to whatever you want", icon="info", option_1="No", option_2="Ok", sound=True)
                    response = msg.get()
                    if response == "No":
                        return
                    elif response == "Ok":
                        os.system(f"notepad {os.path.join(cwd(), 'config.ini')}")
                    else:
                        return
                self.after(0, callback)
            except:
                show_message("Couldn't open config.ini" ,"you can do so by yourself and change reset_on_fail value to whatever you want")
        else:
            return
    def theme_options_func(self, option: str):
        if option == "Default":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_theme.json")
        if option == "Blue":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_blue.json")
        if option == "Grey":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_grey.json")
        if option == "Ghost":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_ghost.json")
        if option == "Obsidian":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_obsidian.json")
        if option == "NeonBanana":
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", "boiiiwd_neonbanana.json")
        if option == "Custom":
            self.boiiiwd_custom_theme()
            save_config("theme", "boiiiwd_theme.json")
        if not option == "Custom":
            if show_message("Restart to take effect!", f"{option} theme has been set ,please restart to take effect", icon="info", _return=True, option_1="Ok", option_2="Restart"):
                try:
                    p = psutil.Process(os.getpid())
                    for handler in p.open_files() + p.connections():
                        os.close(handler.fd)
                except Exception:
                    pass
                python = sys.executable
                os.execl(python, python, *sys.argv)
            else:
                pass

    def enable_save_button(self, *args):
        try:
            self.save_button.configure(state='normal')
        except:
            pass

    def save_settings(self):
        self.save_button.configure(state='disabled')

        if self.check_items_var.get():
            save_config("check_items", "on")
        else:
            save_config("check_items", "off")

        if self.check_updates_checkbox.get():
            save_config("checkforupdtes", "on")
        else:
            save_config("checkforupdtes", "off")

        if self.checkbox_show_console.get():
            save_config("console", "on")
            self.console = True
        else:
            save_config("console", "off")
            self.console = False

        if self.skip_already_installed_ch.get():
            save_config("skip_already_installed", "on")
            self.skip_already_installed = True
        else:
            save_config("skip_already_installed", "off")
            self.skip_already_installed = False

        if self.clean_checkbox.get():
            save_config("clean_on_finish", "on")
            self.clean_on_finish = True
        else:
            save_config("clean_on_finish", "off")
            self.clean_on_finish = False

        if self.checkbox_continuous.get():
            save_config("continuous_download", "on")
            self.continuous = True
        else:
            save_config("continuous_download", "off")
            self.continuous = False

        if self.estimated_progress_cb.get():
            save_config("estimated_progress", "on")
            self.estimated_progress = True
        else:
            save_config("estimated_progress", "off")
            self.estimated_progress = False

        if self.show_fails_cb.get():
            save_config("show_fails", "on")
            self.show_fails = True
        else:
            save_config("show_fails", "off")
            self.show_fails = False

        if self.reset_steamcmd_on_fail.get():
            value = self.reset_steamcmd_on_fail.get()
            if value == "Disable":
                self.steam_fail_counter_toggle = False
            else:
                self.steam_fail_counter_toggle = True
                self.steam_fail_number = int(value)
            save_config("reset_on_fail", value)

    def load_settings(self, setting, fallback=None):
        if setting == "console":
            if check_config(setting, fallback) == "on":
                self.console = True
                return 1
            else:
                self.console = False
                return 0

        if setting == "continuous_download":
            if check_config(setting, "on") == "on":
                self.continuous = True
                return 1
            else:
                self.continuous = False
                return 0

        if setting == "clean_on_finish":
            if check_config(setting, fallback) == "on":
                self.clean_on_finish = True
                return 1
            else:
                self.clean_on_finish = False
                return 0
        if setting == "estimated_progress":
            if check_config(setting, fallback) == "on":
                self.estimated_progress = True
                return 1
            else:
                self.estimated_progress = False
                return 0

        if setting == "reset_on_fail":
            option = check_config(setting, fallback)
            if option == "Disable" or option == "Custom":
                self.steam_fail_counter_toggle = False
                return "Disable"
            else:
                try:
                    self.steam_fail_number = int(option)
                    self.steam_fail_counter_toggle = True
                    return option
                except:
                    self.steam_fail_counter_toggle = True
                    self.steam_fail_number = 10
                    return "10"

        if setting == "show_fails":
            if check_config(setting, fallback) == "on":
                self.show_fails = True
                return 1
            else:
                self.show_fails = False
                return 0

        if setting == "skip_already_installed":
            if check_config(setting, fallback) == "on":
                self.skip_already_installed = True
                return 1
            else:
                self.skip_already_installed = False
                return 0

        if setting == "theme":
            if os.path.exists(os.path.join(cwd(), "boiiiwd_theme.json")):
                return "Custom"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_theme.json":
                return "Default"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_grey.json":
                return "Grey"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_blue.json":
                return "Blue"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_obsidian.json":
                return "Obsidian"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_ghost.json":
                return "Ghost"
            if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_neonbanana.json":
                return "NeonBanana"
        else:
            if check_config(setting, fallback) == "on":
                return 1
            else:
                return 0

    def boiiiwd_custom_theme(self, disable_only=None):
        file_to_rename = os.path.join(cwd(), "boiiiwd_theme.json")
        if os.path.exists(file_to_rename):
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            new_name = f"boiiiwd_theme_{timestamp}.json"
            os.rename(file_to_rename, os.path.join(cwd(), new_name))

            if not disable_only:
                show_message("Preset file renamed", "Custom preset disabled, file has been renmaed\n* Restart the app to take effect", icon="info")
        else:
            if disable_only:
                return
            try:
                shutil.copy(os.path.join(RESOURCES_DIR, check_config("theme", "boiiiwd_theme.json")), os.path.join(cwd(), "boiiiwd_theme.json"))
            except:
                shutil.copy(os.path.join(RESOURCES_DIR, "boiiiwd_theme.json"), os.path.join(cwd(), "boiiiwd_theme.json"))
            show_message("Preset file created", "You can now edit boiiiwd_theme.json in the current directory to your liking\n* Edits will apply next time you open boiiiwd\n* Program will always take boiiiwd_theme.json as the first theme option if found\n* Click on this button again to disable your custom theme or just rename boiiiwd_theme.json", icon="info")

    def settings_check_for_updates(self):
        check_for_updates_func(self, ignore_up_todate=False)

    def load_on_switch_screen(self):
        self.check_updates_var.set(self.load_settings("checkforupdtes"))
        self.console_var.set(self.load_settings("console"))
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))
        self.clean_checkbox_var.set(self.load_settings("clean_on_finish", "on"))
        self.continuous_var.set(self.load_settings("continuous_download"))
        self.show_fails_var.set(self.load_settings("show_fails", "on"))
        self.skip_already_installed_var.set(self.load_settings("skip_already_installed", "on"))

        # keep last cuz of trace_add()
        self.save_button.configure(state='disabled')

    def settings_launch_boiii(self):
        launch_boiii_func(check_config("destinationfolder"))

    def settings_reset_steamcmd(self):
        reset_steamcmd()

    def from_steam_to_boiii_toplevel(self):
        def main_thread():
            try:
                top = ctk.CTkToplevel(self)
                if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                    top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
                top.title("Steam to boiii -> Workshop items")
                top.attributes('-topmost', 'true')
                top.resizable(False, False)
                # Create input boxes
                center_frame = ctk.CTkFrame(top)
                center_frame.grid(row=0, column=0, padx=20, pady=20)

                # Create input boxes
                steam_folder_label = ctk.CTkLabel(center_frame, text="Steam Folder:")
                steam_folder_label.grid(row=0, column=0, padx=(20, 20), pady=(10, 0), sticky='w')
                steam_folder_entry = ctk.CTkEntry(center_frame, width=225)
                steam_folder_entry.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=(10, 10), sticky='nes')
                button_steam_browse = ctk.CTkButton(center_frame, text="Select", width=10)
                button_steam_browse.grid(row=1, column=2, padx=(0, 20), pady=(10, 10), sticky="wnes")

                boiii_folder_label = ctk.CTkLabel(center_frame, text="BOIII Folder:")
                boiii_folder_label.grid(row=2, column=0, padx=(20, 20), pady=(10, 0), sticky='w')
                boiii_folder_entry = ctk.CTkEntry(center_frame, width=225)
                boiii_folder_entry.grid(row=3, column=0, columnspan=2, padx=(0, 20), pady=(10, 10), sticky='nes')
                button_BOIII_browse = ctk.CTkButton(center_frame, text="Select", width=10)
                button_BOIII_browse.grid(row=3, column=2, padx=(0, 20), pady=(10, 10), sticky="wnes")

                # Create option to choose between cut or copy
                operation_label = ctk.CTkLabel(center_frame, text="Choose operation:")
                operation_label.grid(row=4, column=0, padx=(20, 20), pady=(10, 10), sticky='wnes')
                copy_var = ctk.BooleanVar()
                cut_var = ctk.BooleanVar()
                copy_check = ctk.CTkCheckBox(center_frame, text="Copy", variable=copy_var)
                cut_check = ctk.CTkCheckBox(center_frame, text="Cut", variable=cut_var)
                copy_check.grid(row=4, column=1, padx=(0, 10), pady=(10, 10), sticky='wnes')
                cut_check.grid(row=4, column=2, padx=(0, 10), pady=(10, 10), sticky='nes')

                # Create progress bar
                progress_bar = ctk.CTkProgressBar(center_frame, mode="determinate", height=20, corner_radius=7)
                progress_bar.grid(row=5, column=0, columnspan=3, padx=(20, 20), pady=(10, 10), sticky='wnes')
                progress_text = ctk.CTkLabel(progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", text_color="white", height=0, width=0, corner_radius=0)
                progress_text.place(relx=0.5, rely=0.5, anchor="center")

                copy_button = ctk.CTkButton(center_frame, text="Start (Copy)")
                copy_button.grid(row=6, column=0, columnspan=3,padx=(20, 20), pady=(10, 10), sticky='wnes')

                # funcs
                # had to use this shit again cuz of threading issues with widgets
                def copy_with_progress(src, dst):
                    try:
                        total_files = sum([len(files) for root, dirs, files in os.walk(src)])
                        progress = 0

                        def copy_progress(src, dst):
                            nonlocal progress
                            shutil.copy2(src, dst)
                            progress += 1
                            top.after(0, progress_text.configure(text=f"Copying files: {progress}/{total_files}"))
                            value = (progress / total_files) * 100
                            valuep = value / 100
                            progress_bar.set(valuep)

                        try:
                            shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=copy_progress)
                        except Exception as E:
                            show_message("Error", f"Error copying files: {E}", icon="cancel")
                    finally:
                        top.after(0, progress_text.configure(text="0%"))
                        top.after(0, progress_bar.set(0.0))

                def check_status(var, op_var):
                    if var.get():
                        op_var.set(False)
                    if cut_var.get():
                        copy_button.configure(text=f"Start (Cut)")
                    if copy_var.get():
                        copy_button.configure(text=f"Start (Copy)")

                def open_BOIII_browser():
                    selected_folder = ctk.filedialog.askdirectory(title="Select BOIII Folder")
                    if selected_folder:
                        boiii_folder_entry.delete(0, "end")
                        boiii_folder_entry.insert(0, selected_folder)

                def open_steam_browser():
                    selected_folder = ctk.filedialog.askdirectory(title="Select Steam Folder (ex: C:\Program Files (x86)\Steam)")
                    if selected_folder:
                        steam_folder_entry.delete(0, "end")
                        steam_folder_entry.insert(0, selected_folder)
                        save_config("steam_folder" ,steam_folder_entry.get())

                def start_copy_operation():
                    def start_thread():
                        try:
                            if not cut_var.get() and not copy_var.get():
                                show_message("Choose operation!", "Please choose an operation, Copy or Cut files from steam!")
                                return

                            copy_button.configure(state="disabled")
                            steam_folder = steam_folder_entry.get()
                            ws_folder = os.path.join(steam_folder, "steamapps/workshop/content/311210")
                            boiii_folder = boiii_folder_entry.get()

                            if not os.path.exists(steam_folder) and not os.path.exists(ws_folder):
                                show_message("Not found", "Either you have no items downloaded from Steam or wrong path, please recheck path (ex: C:\Program Files (x86)\Steam)")
                                return

                            if not os.path.exists(boiii_folder):
                                show_message("Not found", "BOIII folder not found, please recheck path")
                                return

                            top.after(0, progress_text.configure(text="Loading..."))

                            map_folder = os.path.join(ws_folder)

                            subfolders = [f for f in os.listdir(map_folder) if os.path.isdir(os.path.join(map_folder, f))]
                            total_folders = len(subfolders)

                            if not subfolders:
                                show_message("No items found", f"No items found in \n{map_folder}")
                                return

                            for i, workshop_id in enumerate(subfolders, start=1):
                                json_file_path = os.path.join(map_folder, workshop_id, "workshop.json")
                                copy_button.configure(text=f"Working on -> {i}/{total_folders}")

                                if os.path.exists(json_file_path):
                                    mod_type = extract_json_data(json_file_path, "Type")
                                    folder_name = extract_json_data(json_file_path, "PublisherID")

                                    if mod_type == "mod":
                                        mods_folder = os.path.join(boiii_folder, "mods")
                                        folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                                    elif mod_type == "map":
                                        usermaps_folder = os.path.join(boiii_folder, "usermaps")
                                        folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                                    else:
                                        show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                                        continue

                                    os.makedirs(folder_name_path, exist_ok=True)

                                    try:
                                        copy_with_progress(os.path.join(map_folder, workshop_id), folder_name_path)
                                    except Exception as E:
                                        show_message("Error", f"Error copying files: {E}", icon="cancel")
                                        continue

                                    if cut_var.get():
                                        remove_tree(os.path.join(map_folder, workshop_id))

                            if subfolders:
                                app.show_complete_message(message=f"All items were moved\nYou can run the game now!\nPS: You have to restart the game\n(pressing launch will launch/restarts)")

                        finally:
                            if cut_var.get():
                                copy_button.configure(text=f"Start (Cut)")
                            if copy_var.get():
                                copy_button.configure(text=f"Start (Copy)")
                            copy_button.configure(state="normal")
                            top.after(0, progress_bar.set(0))
                            top.after(0, progress_text.configure(text="0%"))

                    # prevents app hanging
                    threading.Thread(target=start_thread).start()

                # config
                progress_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "progress_bar_fill_color")
                progress_bar.configure(progress_color=progress_color)
                steam_folder_entry.insert(1, check_config("steam_folder", ""))
                boiii_folder_entry.insert(1, app.edit_destination_folder.get())
                button_BOIII_browse.configure(command=open_BOIII_browser)
                button_steam_browse.configure(command=open_steam_browser)
                copy_button.configure(command=start_copy_operation)
                cut_check.configure(command = lambda: check_status(cut_var, copy_var))
                copy_check.configure(command = lambda: check_status(copy_var, cut_var))
                app.create_context_menu(steam_folder_entry)
                app.create_context_menu(boiii_folder_entry)
                copy_var.set(True)
                progress_bar.set(0)

            except Exception as e:
                show_message("Error", f"{e}", icon="cancel")

        app.after(0, main_thread)

class BOIIIWD(ctk.CTk):
    def __init__(self):
        super().__init__()
        # self.app_instance = BOIIIWD()

        # configure window
        self.title("BOIII Workshop Downloader - Main")

        try:
            geometry_file = os.path.join(cwd(), "boiiiwd_dont_touch.conf")
            if os.path.isfile(geometry_file):
                with open(geometry_file, "r") as conf:
                    self.geometry(conf.read())
            else:
                self.geometry(f"{910}x{560}")
        except:
            self.geometry(f"{910}x{560}")

        if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
            self.wm_iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico"))
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Qeue frame/tab, keep here or app will start shrinked eveytime
        self.qeueuframe = ctk.CTkFrame(self)
        self.qeueuframe.columnconfigure(1, weight=1)
        self.qeueuframe.columnconfigure(2, weight=1)
        self.qeueuframe.columnconfigure(3, weight=1)
        self.qeueuframe.rowconfigure(1, weight=1)
        self.qeueuframe.rowconfigure(2, weight=1)
        self.qeueuframe.rowconfigure(3, weight=1)
        self.qeueuframe.rowconfigure(4, weight=1)

        self.workshop_queue_label = ctk.CTkLabel(self.qeueuframe, text="Workshop IDs/Links -> press help to see examples:")
        self.workshop_queue_label.grid(row=0, column=0, padx=(20, 20), pady=(20, 20), sticky="wns")

        self.help_button = ctk.CTkButton(master=self.qeueuframe, text="Help", command=self.help_queue_text_func, width=10, height=10, fg_color="#585858")
        self.help_button.grid(row=0, column=0, padx=(352, 0), pady=(23, 0), sticky="en")
        self.help_restore_content = None

        self.queuetextarea = ctk.CTkTextbox(master=self.qeueuframe, font=("", 15))
        self.queuetextarea.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(0, 20), sticky="nwse")

        self.status_text = ctk.CTkLabel(self.qeueuframe, text="Status: Standby!")
        self.status_text.grid(row=3, column=0, padx=(20, 20), pady=(0, 20), sticky="ws")

        self.skip_boutton = ctk.CTkButton(master=self.qeueuframe, text="Skip", command=self.skip_current_queue_item, width=10, height=10, fg_color="#585858")

        self.qeueuframe.grid_remove()

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.settings_tab = SettingsTab(self)
        self.library_tab = LibraryTab(self, corner_radius=3)

        # create sidebar frame with widgets
        font = "Comic Sans MS"
        if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.png")):
            ryuks_icon = os.path.join(RESOURCES_DIR, "ryuk.png")
            self.sidebar_icon = ctk.CTkImage(light_image=Image.open(ryuks_icon), dark_image=Image.open(ryuks_icon), size=(40, 40))
        else:
            self.sidebar_icon = None
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, padx=(10, 20), pady=(10, 10), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text='',image=self.sidebar_icon)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.txt_label = ctk.CTkLabel(self.sidebar_frame, text="- Sidebar -", font=(font, 17))
        self.txt_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_main = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_main.grid(row=2, column=0, padx=10, pady=(20, 6))
        self.sidebar_queue = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_queue.grid(row=3, column=0, padx=10, pady=6)
        self.sidebar_library = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_library.grid(row=4, column=0, padx=10, pady=6, sticky="n")
        self.sidebar_settings = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_settings.grid(row=5, column=0, padx=10, pady=6, sticky="n")

        # create optionsframe
        self.optionsframe = ctk.CTkFrame(self)
        self.optionsframe.grid(row=0, column=1, rowspan=2, padx=(0, 20), pady=(20, 0), sticky="nsew")
        self.txt_main = ctk.CTkLabel(self.optionsframe, text="💎 BOIIIWD 💎", font=(font, 20))
        self.txt_main.grid(row=0, column=1, columnspan=5, padx=0, pady=(20, 20), sticky="n")

        # create slider and progressbar frame
        self.slider_progressbar_frame = ctk.CTkFrame(self)
        self.slider_progressbar_frame.grid(row=2, column=1, rowspan=1, padx=(0, 20), pady=(20, 20), sticky="nsew")

        self.slider_progressbar_frame.columnconfigure(0, weight=0)
        self.slider_progressbar_frame.columnconfigure(1, weight=1)
        self.slider_progressbar_frame.columnconfigure(2, weight=0)
        self.slider_progressbar_frame.rowconfigure(0, weight=1)
        self.slider_progressbar_frame.rowconfigure(1, weight=1)
        self.slider_progressbar_frame.rowconfigure(2, weight=1)
        self.slider_progressbar_frame.rowconfigure(3, weight=1)

        # self.spacer = ctk.CTkLabel(master=self.slider_progressbar_frame, text="")
        # self.spacer.grid(row=0, column=0, columnspan=1)

        self.label_speed = ctk.CTkLabel(master=self.slider_progressbar_frame, text="Awaiting Download!")
        self.label_speed.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        self.elapsed_time = ctk.CTkLabel(master=self.slider_progressbar_frame, text="", anchor="center")
        self.elapsed_time.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="nsew")  # Use "nsew" to center label
        self.label_file_size = ctk.CTkLabel(master=self.slider_progressbar_frame, text="File size: 0KB")
        self.label_file_size.grid(row=1, column=2, padx=(0, 20), pady=(0, 10), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(master=self.slider_progressbar_frame, mode="determinate", height=20, corner_radius=7)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 10), columnspan=3, sticky="ew")

        self.progress_text = ctk.CTkLabel(self.progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", text_color="white", height=0, width=0, corner_radius=0)
        self.progress_text.place(relx=0.5, rely=0.5, anchor="center")

        self.button_download = ctk.CTkButton(master=self.slider_progressbar_frame, text="Download", command=self.download_map)
        self.button_download.grid(row=4, column=0, padx=20, pady=(5, 20), columnspan=2, sticky="ew")

        self.button_stop = ctk.CTkButton(master=self.slider_progressbar_frame, text="Stop", command=self.stop_download)
        self.button_stop.grid(row=4, column=2, padx=(0, 20), pady=(5, 20), columnspan=1, sticky="w")

        # options frame
        self.optionsframe.columnconfigure(1, weight=1)
        self.optionsframe.columnconfigure(2, weight=1)
        self.optionsframe.columnconfigure(3, weight=1)
        self.optionsframe.rowconfigure(1, weight=1)
        self.optionsframe.rowconfigure(2, weight=1)
        self.optionsframe.rowconfigure(3, weight=1)
        self.optionsframe.rowconfigure(4, weight=1)

        self.label_workshop_id = ctk.CTkLabel(master=self.optionsframe, text="Enter the Workshop ID or Link of the map/mod you want to download:\n")
        self.label_workshop_id.grid(row=1, column=1, padx=20, pady=(10, 0), columnspan=4, sticky="ws")

        self.check_if_changed = ctk.StringVar()
        self.check_if_changed.trace_add("write", self.id_chnaged_handler)
        self.edit_workshop_id = ctk.CTkEntry(master=self.optionsframe, textvariable=self.check_if_changed)
        self.edit_workshop_id.grid(row=2, column=1, padx=20, pady=(0, 10), columnspan=4, sticky="ewn")

        self.button_browse = ctk.CTkButton(master=self.optionsframe, text="Workshop", command=self.open_browser, width=10)
        self.button_browse.grid(row=2, column=5, padx=(0, 20), pady=(0, 10), sticky="en")
        self.button_browse_tooltip = CTkToolTip(self.button_browse, message="Will open steam workshop for boiii in your browser")

        self.info_button = ctk.CTkButton(master=self.optionsframe, text="Details", command=self.show_map_info, width=10)
        self.info_button.grid(row=2, column=5, padx=(0, 20), pady=(0, 10), sticky="wn")

        self.label_destination_folder = ctk.CTkLabel(master=self.optionsframe, text="Enter Your BOIII folder:")
        self.label_destination_folder.grid(row=3, column=1, padx=20, pady=(0, 0), columnspan=4, sticky="ws")

        self.edit_destination_folder = ctk.CTkEntry(master=self.optionsframe, placeholder_text="Your BOIII Instalation folder")
        self.edit_destination_folder.grid(row=4, column=1, padx=20, pady=(0, 25), columnspan=4, sticky="ewn")

        self.button_BOIII_browse = ctk.CTkButton(master=self.optionsframe, text="Select", command=self.open_BOIII_browser)
        self.button_BOIII_browse.grid(row=4, column=5, padx=(0, 20), pady=(0, 10), sticky="ewn")

        self.label_steamcmd_path = ctk.CTkLabel(master=self.optionsframe, text="Enter SteamCMD path:")
        self.label_steamcmd_path.grid(row=5, column=1, padx=20, pady=(0, 0), columnspan=3, sticky="wn")

        self.edit_steamcmd_path = ctk.CTkEntry(master=self.optionsframe, placeholder_text="Enter your SteamCMD path")
        self.edit_steamcmd_path.grid(row=6, column=1, padx=20, pady=(0, 30), columnspan=4, sticky="ewn")

        self.button_steamcmd_browse = ctk.CTkButton(master=self.optionsframe, text="Select", command=self.open_steamcmd_path_browser)
        self.button_steamcmd_browse.grid(row=6, column=5, padx=(0, 20), pady=(0, 30), sticky="ewn")


        # set default values
        self.active_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "button_active_state_color")
        self.normal_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "button_normal_state_color")
        self.progress_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "progress_bar_fill_color")
        self.settings_tab.appearance_mode_optionemenu.set("Dark")
        self.settings_tab.scaling_optionemenu.set("100%")
        self.progress_bar.set(0.0)
        self.progress_bar.configure(progress_color=self.progress_color)
        self.hide_settings_widgets()
        self.button_stop.configure(state="disabled")
        self.is_pressed = False
        self.queue_enabled = False
        self.queue_stop_button = False
        self.is_downloading = False
        self.item_skipped = False
        self.fail_threshold = 0

        # sidebar windows bouttons
        self.sidebar_main.configure(command=self.main_button_event, text="Main ⬇️", fg_color=(self.active_color), state="active")
        self.sidebar_library.configure(text="Library 📙", command=self.library_button_event)
        self.sidebar_queue.configure(text="Queue 🚧", command=self.queue_button_event)
        sidebar_settings_button_image = os.path.join(RESOURCES_DIR, "sett10.png")
        self.sidebar_settings.configure(command=self.settings_button_event, text="", image=ctk.CTkImage(Image.open(sidebar_settings_button_image), size=(int(35), int(35))), fg_color="transparent", width=45, height=45)
        self.sidebar_settings_tooltip = CTkToolTip(self.sidebar_settings, message="Settings")
        self.sidebar_library_tooltip = CTkToolTip(self.sidebar_library, message="Experimental")
        self.sidebar_queue_tooltip = CTkToolTip(self.sidebar_queue, message="Experimental")
        self.bind("<Configure>", self.save_window_size)

        # context_menus
        self.create_context_menu(self.edit_workshop_id)
        self.create_context_menu(self.edit_destination_folder)
        self.create_context_menu(self.edit_steamcmd_path)
        self.create_context_menu(self.queuetextarea, textbox=True)
        self.create_context_menu(self.library_tab.filter_entry, textbox=False, library=True)
        # valid event required for filter_items()
        self.cevent = Event()
        self.cevent.x = 0
        self.cevent.y = 0

        # load ui configs
        self.load_configs()

        if check_config("checkforupdtes") == "on":
            self.withdraw()
            check_for_updates_func(self, ignore_up_todate=True)
            self.update()
            self.deiconify()

        try:
            self.settings_tab.load_settings("clean_on_finish", "on")
            self.settings_tab.load_settings("continuous_download", "on")
            self.settings_tab.load_settings("console", "off")
            self.settings_tab.load_settings("estimated_progress", "on")
            self.settings_tab.load_settings("reset_on_fail", "10")
            self.settings_tab.load_settings("show_fails", "on")
            self.settings_tab.load_settings("skip_already_installed", "on")
        except:
            pass

        if not check_steamcmd():
            self.show_steam_warning_message()

        # items check for update, ill change all the variables to work this way at a later date
        if self.settings_tab.check_items_var.get():
            self.library_tab.check_for_updates(on_launch=True)

    def do_popup(self, event, frame):
        try: frame.tk_popup(event.x_root, event.y_root)
        finally: frame.grab_release()

    def create_context_menu(self, text_widget, textbox=False, library=False):
        context_menu = Menu(text_widget, tearoff=False, background='#565b5e', fg='white', borderwidth=0, bd=0)
        context_menu.add_command(label="Paste", command=lambda: self.clipboard_paste(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Copy", command=lambda: self.clipboard_copy(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=lambda: self.clipboard_cut(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.select_all(text_widget, textbox))
        text_widget.bind("<Button-3>", lambda event: self.do_popup(event, frame=context_menu))

    def clipboard_copy(self, text, textbox=False, library=False):
        text.clipboard_clear()
        try:
            text.clipboard_append(text.selection_get())
        except:
            if textbox:
                text.clipboard_append(text.get("1.0", END))
            else:
                text.clipboard_append(text.get())
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

    def clipboard_paste(self, text, textbox=False, library=False):
        try:
            if textbox:
                text_cont = text.get("1.0", END)
            else:
                text_cont = text.get()
            if textbox:
                if text.tag_ranges("sel"):
                    text.delete("sel.first", "sel.last")
            else:
                if text.selection_get() in text_cont:
                    start_index = text_cont.index(text.selection_get())
                    end_index = start_index + len(text.selection_get())
                    text.delete(start_index, end_index)
            text.insert(ctk.INSERT, text.clipboard_get())
        except:
            text.insert(ctk.INSERT, text.clipboard_get())
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

    def select_all(self, text_widget, textbox=False):
        if textbox:
            text_widget.tag_add("sel", "1.0", "end")
            text_widget.focus()
        else:
            text_widget.select_range(0, END)
            text_widget.focus()

    def clipboard_cut(self, text, textbox=False, library=False):
        text.clipboard_clear()
        if textbox:
            text_cont = text.get(1.0, END)
        else:
            text_cont = text.get()
        try:
            if textbox:
                if text.tag_ranges("sel"):
                    selected_text = text.get("sel.first", "sel.last")
                    text.clipboard_append(selected_text)
                    text.delete("sel.first", "sel.last")
                else:
                    raise
            else:
                text.clipboard_append(text.selection_get())
                if text.selection_get() in text_cont:
                    start_index = text_cont.index(text.selection_get())
                    end_index = start_index + len(text.selection_get())
                    text.delete(start_index, end_index)
        except:
            if textbox:
                text.clipboard_append(text.get("1.0", END))
                text.delete(1.0, "end")
            else:
                text.clipboard_append(text.get())
                text.delete(0, "end")
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

    def save_window_size(self, event):
        with open("boiiiwd_dont_touch.conf", "w") as conf:
            conf.write(self.geometry())

    def on_closing(self):
        save_config("DestinationFolder" ,self.edit_destination_folder.get())
        save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())
        self.stop_download(on_close=True)
        os._exit(0)

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

    def hide_main_widgets(self):
        self.optionsframe.grid_forget()
        self.slider_progressbar_frame.grid_forget()

    def show_main_widgets(self):
        self.title("BOIII Workshop Downloader - Main")
        self.slider_progressbar_frame.grid(row=2, column=1, rowspan=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.optionsframe.grid(row=0, column=1, rowspan=2, padx=(0, 20), pady=(20, 0), sticky="nsew")

    def hide_settings_widgets(self):
        self.settings_tab.grid_forget()

    def show_settings_widgets(self):
        self.title("BOIII Workshop Downloader - Settings")
        self.settings_tab.grid(row=0, rowspan=3, column=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.settings_tab.load_on_switch_screen()

    def hide_library_widgets(self):
        self.library_tab.grid_remove()

    def show_library_widgets(self):
        self.title("BOIII Workshop Downloader - Library")
        count = self.library_tab.load_items(self.edit_destination_folder.get())
        self.library_tab.grid(row=0, rowspan=3, column=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.title(f"BOIII Workshop Downloader - Library  ➜  {count}")

    def show_queue_widgets(self):
        self.title("BOIII Workshop Downloader - Queue")
        self.optionsframe.grid_forget()
        self.queue_enabled = True
        self.slider_progressbar_frame.grid(row=2, column=1, rowspan=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.qeueuframe.grid(row=0, column=1, rowspan=2, padx=(0, 20), pady=(20, 0), sticky="nsew")

    def hide_queue_widgets(self):
        self.queue_enabled = False
        self.qeueuframe.grid_forget()

    def main_button_event(self):
        self.sidebar_main.configure(state="active", fg_color=(self.active_color))
        self.sidebar_settings.configure(state="normal", fg_color="transparent")
        self.sidebar_library.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_queue.configure(state="normal", fg_color=(self.normal_color))
        self.hide_settings_widgets()
        self.hide_library_widgets()
        self.hide_queue_widgets()
        self.show_main_widgets()

    def settings_button_event(self):
        self.sidebar_main.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_library.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_queue.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_settings.configure(state="active", fg_color=(self.active_color))
        self.hide_main_widgets()
        self.hide_library_widgets()
        self.hide_queue_widgets()
        self.show_settings_widgets()

    def library_button_event(self):
        self.sidebar_main.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_settings.configure(state="normal", fg_color="transparent")
        self.sidebar_queue.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_library.configure(state="active", fg_color=(self.active_color))
        self.hide_main_widgets()
        self.hide_settings_widgets()
        self.hide_queue_widgets()
        self.show_library_widgets()

    def queue_button_event(self):
        self.sidebar_main.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_settings.configure(state="normal", fg_color="transparent")
        self.sidebar_library.configure(state="normal", fg_color=(self.normal_color))
        self.sidebar_queue.configure(state="active", fg_color=(self.active_color))
        self.hide_settings_widgets()
        self.hide_library_widgets()
        self.show_queue_widgets()

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
            self.settings_tab.appearance_mode_optionemenu.set(new_appearance_mode)
            scaling_float = float(new_scaling)*100
            scaling_int = math.trunc(scaling_float)
            self.settings_tab.scaling_optionemenu.set(f"{scaling_int}%")
        else:
            new_appearance_mode = check_config("appearance", "Dark")
            new_scaling = check_config("scaling", 1.0)
            ctk.set_appearance_mode(new_appearance_mode)
            ctk.set_widget_scaling(float(new_scaling))
            self.settings_tab.appearance_mode_optionemenu.set(new_appearance_mode)
            scaling_float = float(new_scaling)*100
            scaling_int = math.trunc(scaling_float)
            self.settings_tab.scaling_optionemenu.set(f"{scaling_int}%")
            self.edit_steamcmd_path.delete(0, "end")
            self.edit_steamcmd_path.insert(0, cwd())
            create_default_config()

    def help_queue_text_func(self, event=None):
        textarea_content = self.queuetextarea.get("1.0", "end").strip()
        help_text = "3010399939,2976006537,2118338989,...\nor:\n3010399939\n2976006537\n2113146805\n..."
        if any(char.strip() for char in textarea_content):
            if help_text in textarea_content:
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press help to see examples:")
                self.help_button.configure(text="Help")
                self.queuetextarea.configure(state="normal")
                self.queuetextarea.delete(1.0, "end")
                self.queuetextarea.insert(1.0, "")
                if self.help_restore_content:
                    self.queuetextarea.insert(1.0, self.help_restore_content.strip())
                else:
                    self.queuetextarea.insert(1.0, "")
            else:
                if not help_text in textarea_content:
                        self.help_restore_content = textarea_content
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press help to see examples:")
                self.help_button.configure(text="Restore")
                self.queuetextarea.configure(state="normal")
                self.queuetextarea.delete(1.0, "end")
                self.queuetextarea.insert(1.0, "")
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press restore to remove examples:")
                self.queuetextarea.insert(1.0, help_text)
                self.queuetextarea.configure(state="disabled")
        else:
            self.help_restore_content = textarea_content
            self.workshop_queue_label.configure(text="Workshop IDs/Links => press restore to remove examples:")
            self.help_button.configure(text="Restore")
            self.queuetextarea.insert(1.0, help_text)
            self.queuetextarea.configure(state="disabled")

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

    def show_steam_warning_message(self):
        def callback():
            msg = CTkMessagebox(title="Warning", message="steamcmd.exe was not found in the specified directory.\nPress Download to get it or Press Cancel and select it from there!.",
                                icon="warning", option_1="Cancel", option_2="Download", sound=True)
            response = msg.get()
            if response == "Cancel":
                return
            elif response == "Download":
                self.download_steamcmd()
        self.after(0, callback)

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
                def inti_steam():
                    msg = CTkMessagebox(title="Success", message="SteamCMD has been downloaded ,Press ok to initialize it.", icon="info", option_1="No", option_2="Ok", sound=True)
                    response = msg.get()
                    if response == "No":
                        pass
                    elif response == "Ok":
                        initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                        initialize_steam_thread.start()
                    else:
                        pass
                self.after(0, inti_steam)
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
                show_message("Warning", "Please enter a Workshop ID/Link first.")
                return

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Please enter a valid Workshop ID/Link.")
                except:
                    show_message("Warning", "Please enter a valid Workshop ID/Link.")
                    return
            if self.button_download._state == "normal":
                self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))

            try:
                headers = {'Cache-Control': 'no-cache'}
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                content = response.text

                soup = BeautifulSoup(content, "html.parser")

                try:
                    map_mod_type = soup.find("div", class_="rightDetailsBlock").text.strip()
                    map_name = soup.find("div", class_="workshopItemTitle").text.strip()
                    map_size = map_size = get_workshop_file_size(workshop_id, raw=True)
                    details_stats_container = soup.find("div", class_="detailsStatsContainerRight")
                    details_stat_elements = details_stats_container.find_all("div", class_="detailsStatRight")
                    date_created = details_stat_elements[1].text.strip()
                    try:
                        ratings = soup.find('div', class_='numRatings')
                        ratings_text = ratings.get_text()
                    except:
                        ratings = "Not found"
                        ratings_text= "Not enough ratings"
                    try:
                        date_updated = details_stat_elements[2].text.strip()
                    except:
                        date_updated = "Not updated"
                    stars_div = soup.find("div", class_="fileRatingDetails")
                    starts = stars_div.find("img")["src"]
                except:
                    show_message("Warning", "Please enter a valid Workshop ID/Link\nCouldn't get information.")
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

                starts_image_response = requests.get(starts)
                stars_image = Image.open(io.BytesIO(starts_image_response.content))
                stars_image_size = stars_image.size

                image_response = requests.get(workshop_item_image_url)
                image_response.raise_for_status()
                image = Image.open(io.BytesIO(image_response.content))
                image_size = image.size

                self.toplevel_info_window(map_name, map_mod_type, map_size, image, image_size, date_created ,
                                          date_updated, stars_image, stars_image_size, ratings_text, url)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")
                return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size, ratings_text, url):
        def main_thread():
            top = ctk.CTkToplevel(self)
            top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            top.title("Map/Mod Information")
            top.attributes('-topmost', 'true')

            def close_window():
                top.destroy()

            def view_map_mod():
                webbrowser.open(url)

            # frames
            stars_frame = ctk.CTkFrame(top)
            stars_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="nsew")
            stars_frame.columnconfigure(0, weight=0)
            stars_frame.rowconfigure(0, weight=1)

            image_frame = ctk.CTkFrame(top)
            image_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=0, sticky="nsew")

            info_frame = ctk.CTkFrame(top)
            info_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

            buttons_frame = ctk.CTkFrame(top)
            buttons_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="nsew")

            # fillers
            name_label = ctk.CTkLabel(info_frame, text=f"Name: {map_name}")
            name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            type_label = ctk.CTkLabel(info_frame, text=f"Type: {map_mod_type}")
            type_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            size_label = ctk.CTkLabel(info_frame, text=f"Size: {map_size}")
            size_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            date_created_label = ctk.CTkLabel(info_frame, text=f"Posted: {date_created}")
            date_created_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}")
            date_updated_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            stars_image_label = ctk.CTkLabel(stars_frame)
            stars_width, stars_height = stars_image_size
            stars_image_widget = ctk.CTkImage(stars_image, size=(int(stars_width), int(stars_height)))
            stars_image_label.configure(image=stars_image_widget, text="")
            stars_image_label.pack(side="left", padx=(10, 20), pady=(10, 10))

            ratings = ctk.CTkLabel(stars_frame)
            ratings.configure(text=ratings_text)
            ratings.pack(side="right", padx=(10, 20), pady=(10, 10))

            image_label = ctk.CTkLabel(image_frame)
            width, height = image_size
            image_widget = ctk.CTkImage(image, size=(int(width), int(height)))
            image_label.configure(image=image_widget, text="")
            image_label.pack(expand=True, fill="both", padx=(10, 20), pady=(10, 10))

            # Buttons
            close_button = ctk.CTkButton(buttons_frame, text="View", command=view_map_mod)
            close_button.pack(side="left", padx=(10, 20), pady=(10, 10))

            view_button = ctk.CTkButton(buttons_frame, text="Close", command=close_window)
            view_button.pack(side="right", padx=(10, 20), pady=(10, 10))

            top.grid_rowconfigure(0, weight=0)
            top.grid_rowconfigure(1, weight=0)
            top.grid_rowconfigure(2, weight=1)
            top.grid_columnconfigure(0, weight=1)
            top.grid_columnconfigure(1, weight=1)

        self.after(0, main_thread)

    def check_steamcmd_stdout(self, log_file_path, target_item_id):
        temp_file_path = log_file_path + '.temp'
        shutil.copy2(log_file_path, temp_file_path)

        try:
            with open(temp_file_path, 'r') as log_file:
                log_file.seek(0, os.SEEK_END)
                file_size = log_file.tell()

                position = file_size
                lines_found = 0

                while lines_found < 7 and position > 0:
                    position -= 1
                    log_file.seek(position, os.SEEK_SET)

                    char = log_file.read(1)

                    if char == '\n':
                        lines_found += 1

                lines = log_file.readlines()[-7:]

                for line in reversed(lines):
                    line = line.lower().strip()
                    if f"download item {target_item_id.strip()}" in line:
                        return True

            return False
        finally:
            os.remove(temp_file_path)

    def skip_current_queue_item(self):
        if self.button_download._state == "normal":
            self.skip_boutton.grid_remove()
            self.after(1, self.status_text.configure(text=f"Status: Standby!"))
            return
        self.settings_tab.stopped = True
        self.item_skipped = True
        self.settings_tab.steam_fail_counter = 0
        self.is_pressed = False
        self.is_downloading = False
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW)
        self.skip_boutton.grid_remove()
        self.after(2, self.status_text.configure(text=f"Status: Skipping..."))
        self.label_speed.configure(text="Network Speed: 0 KB/s")
        self.progress_text.configure(text="0%")
        self.progress_bar.set(0.0)

    # the real deal
    def run_steamcmd_command(self, command, map_folder, wsid, queue=None):
        steamcmd_path = get_steamcmd_path()
        stdout_path = os.path.join(steamcmd_path, "logs", "workshop_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        os.makedirs(os.path.dirname(stdout_path), exist_ok=True)

        try:
            with open(stdout_path, 'w') as file:
                file.write('')
        except:
            os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

        show_console = subprocess.CREATE_NO_WINDOW
        if self.settings_tab.console:
            show_console = subprocess.CREATE_NEW_CONSOLE

        if os.path.exists(map_folder):
            try:
                try:
                    os.remove(map_folder)
                except:
                    os.rename(map_folder, os.path.join(map_folder, os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", f"couldntremove_{timestamp}")))
            except Exception as e:
                self.settings_tab.stopped = True
                self.queue_stop_button = True
                show_message("Error", f"Couldn't remove {map_folder}, please do so manually\n{e}", icon="cancel")
                self.stop_download()
                return

        if self.settings_tab.continuous:
            start_time = 0
            while not os.path.exists(map_folder) and not self.settings_tab.stopped:
                process = subprocess.Popen(
                    [steamcmd_path + "\steamcmd.exe"] + command.split(),
                    stdout=None if self.settings_tab.console else subprocess.PIPE,
                    stderr=None if self.settings_tab.console else subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=show_console
                )

                #wait for process
                while True:
                    if not self.is_downloading:
                        if self.check_steamcmd_stdout(stdout_path, wsid):
                            start_time = time.time()
                            self.is_downloading = True
                    elapsed_time = time.time() - start_time
                    if process.poll() != None:
                        break
                    time.sleep(1)

                # print("Broken freeeee!")
                self.is_downloading = False
                try:
                    with open(stdout_path, 'w') as file:
                        file.write('')
                except:
                    os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

                if not self.settings_tab.stopped:
                    self.settings_tab.steam_fail_counter = self.settings_tab.steam_fail_counter + 1
                    if elapsed_time < 20 and elapsed_time > 0 and not os.path.exists(map_folder):
                        self.fail_threshold = self.fail_threshold + 1

                if self.settings_tab.steam_fail_counter_toggle:
                    try:
                        if self.fail_threshold >= int(self.settings_tab.steam_fail_number):
                            reset_steamcmd(no_warn=True)
                            self.settings_tab.steamcmd_reset = True
                            self.settings_tab.steam_fail_counter = 0
                            self.fail_threshold = 0
                    except:
                        if self.fail_threshold >= 25:
                            reset_steamcmd(no_warn=True)
                            self.settings_tab.steam_fail_counter = 0
                            self.fail_threshold = 0
        else:
            process = subprocess.Popen(
                [steamcmd_path + "\steamcmd.exe"] + command.split(),
                stdout=None if self.settings_tab.console else subprocess.PIPE,
                stderr=None if self.settings_tab.console else subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=show_console
            )

            while True:
                if not self.is_downloading:
                    if self.check_steamcmd_stdout(stdout_path, wsid):
                        self.is_downloading = True
                if process.poll() != None:
                    break
                time.sleep(1)

            # print("Broken freeeee!")
            self.is_downloading = False
            try:
                with open(stdout_path, 'w') as file:
                    file.write('')
            except:
                os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

            if not os.path.exists(map_folder):
                show_message("SteamCMD has terminated", "SteamCMD has been terminated\nAnd failed to download the map/mod, try again or enable continuous download in settings")

        self.settings_tab.stopped = True
        if not queue:
            self.button_download.configure(state="normal")
            self.button_stop.configure(state="disabled")

        return process.returncode

    def show_init_message(self):
        def callback():
            msg = CTkMessagebox(title="Warning", message="SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.", icon="info", option_1="No", option_2="Ok", sound=True)
            response = msg.get()
            if response == "No":
                return
            elif response == "Ok":
                initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                initialize_steam_thread.start()
            else:
                return
        self.after(0, callback)

    def show_complete_message(self, message):
        def callback():
            msg = CTkMessagebox(title="Downloads Complete", message=message, icon="info", option_1="Launch", option_2="Ok", sound=True)
            response = msg.get()
            if response=="Launch":
                launch_boiii_func(self.edit_destination_folder.get().strip())
            if response=="Ok":
                return
        self.after(0, callback)

    def download_map(self, update=False):
        self.is_downloading = False
        self.fail_threshold = 0
        if not self.is_pressed:
            self.after(1, self.label_speed.configure(text=f"Loading..."))
            self.is_pressed = True
            self.library_tab.load_items(self.edit_destination_folder.get())
            if self.queue_enabled:
                self.item_skipped = False
                start_down_thread = threading.Thread(target=self.queue_download_thread, args=(update,))
                start_down_thread.start()
            else:
                start_down_thread = threading.Thread(target=self.download_thread, args=(update,))
                start_down_thread.start()
        else:
            show_message("Warning", "Already pressed, Please wait.")

    def queue_download_thread(self, update=None):
        self.stopped = False
        self.queue_stop_button = False
        try:
            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_steam_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                self.show_init_message()
                return

            text = self.queuetextarea.get("1.0", "end")
            items = []
            if "," in text:
                items = [n.strip() for n in text.split(",")]
            else:
                items = [n.strip() for n in text.split("\n") if n.strip()]

            if not items:
                show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                self.stop_download()
                return

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder => in the main tab!.")
                self.stop_download()
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path => in the main tab!.")
                self.stop_download()
                return

            self.total_queue_size = 0
            self.already_installed = []
            for item in items:
                self.fail_threshold = 0
                item.strip()
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download()
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download()
                        return
                if not valid_id(workshop_id):
                    show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                    self.stop_download()
                    return

                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.total_queue_size += ws_file_size

                if file_size is None:
                    show_message("Error", "Failed to retrieve file size.", icon="cancel")
                    self.stop_download()
                    return

                if any(workshop_id in item for item in self.library_tab.added_items):
                    self.already_installed.append(workshop_id)

            if not update:
                if self.already_installed:
                    item_ids = ", ".join(self.already_installed)
                    if self.settings_tab.skip_already_installed:
                        for item in self.already_installed:
                            if item in items:
                                items.remove(item)
                        show_message("Heads up!, map/s skipped => skip is on in settings", f"These item IDs may already be installed and are skipped:\n{item_ids}", icon="info")
                        if not any(isinstance(item, int) for item in items):
                            self.stop_download()
                            return
                    else:
                        show_message("Heads up! map/s not skipped => skip is off in settings", f"These item IDs may already be installed:\n{item_ids}", icon="info")

            self.after(1, self.status_text.configure(text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)}"))
            start_time = time.time()
            for index, item in enumerate(items):
                self.settings_tab.steam_fail_counter = 0
                current_number = index + 1
                total_items = len(items)
                if self.queue_stop_button:
                    self.stop_download()
                    break
                item.strip()
                self.settings_tab.stopped = False
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download()
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download()
                        return
                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
                download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
                map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)

                def check_and_update_progress():
                    previous_net_speed = 0
                    est_downloaded_bytes = 0
                    file_size = ws_file_size
                    item_name = get_item_name(workshop_id) if get_item_name(workshop_id) else "Error getting name"

                    while not self.settings_tab.stopped:
                        if self.settings_tab.steamcmd_reset:
                            self.settings_tab.steamcmd_reset = False
                            previous_net_speed = 0
                            est_downloaded_bytes = 0

                        if self.item_skipped:
                            if index > 0:
                                prev_item_size = None
                                previous_item = items[index - 1]
                                prev_item_path = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", previous_item)
                                prev_item_path_2 = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", previous_item)
                                if os.path.exists(prev_item_path):
                                    prev_item_size = sum(os.path.getsize(os.path.join(prev_item_path, f)) for f in os.listdir(prev_item_path))
                                elif os.path.exists(prev_item_path_2):
                                    prev_item_size = sum(os.path.getsize(os.path.join(prev_item_path_2, f)) for f in os.listdir(prev_item_path_2))
                                else:
                                    prev_item_size = get_workshop_file_size(previous_item)
                                if prev_item_size:
                                    self.total_queue_size -= prev_item_size
                            self.item_skipped = False

                        while not self.is_downloading and not self.settings_tab.stopped:
                            self.after(1, self.label_speed.configure(text=f"Waiting for steamcmd..."))
                            time_elapsed = time.time() - start_time
                            elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Waiting {current_number}/{total_items}"))
                            if len(items) > 1:
                                self.skip_boutton.grid(row=3, column=1, padx=(10, 20), pady=(0, 25), sticky="ws")
                                if index == len(items) - 1:
                                    self.skip_boutton.grid_remove()
                            time.sleep(1)
                            if self.is_downloading:
                                break

                        try:
                            current_size = sum(os.path.getsize(os.path.join(download_folder, f)) for f in os.listdir(download_folder))
                        except:
                            try:
                                current_size = sum(os.path.getsize(os.path.join(map_folder, f)) for f in os.listdir(map_folder))
                            except:
                                continue

                        progress = int(current_size / file_size * 100)

                        if progress > 100 and not self.settings_tab.stopped:
                            progress = int(current_size / current_size * 100)
                            self.total_queue_size -= file_size
                            file_size = current_size
                            self.total_queue_size += file_size
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Downloading {current_number}/{total_items}"))
                            self.after(1, lambda p=progress: self.label_file_size.configure(text=f"Wrong size reported\nFile size: ~{convert_bytes_to_readable(current_size)}"))

                        if self.settings_tab.estimated_progress and not self.settings_tab.stopped:
                            time_elapsed = time.time() - start_time
                            raw_net_speed = psutil.net_io_counters().bytes_recv

                            current_net_speed_text = raw_net_speed
                            net_speed_bytes = current_net_speed_text - previous_net_speed
                            previous_net_speed = current_net_speed_text

                            current_net_speed = net_speed_bytes
                            down_cap = 150000000
                            if current_net_speed >= down_cap:
                                current_net_speed = 10

                            est_downloaded_bytes += current_net_speed

                            percentage_complete = (est_downloaded_bytes / file_size) * 100

                            progress = min(percentage_complete / 100, 0.99)

                            net_speed, speed_unit = convert_speed(net_speed_bytes)

                            elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)

                            # print(f"raw_net {raw_net_speed}\ncurrent_net_speed: {current_net_speed}\nest_downloaded_bytes {est_downloaded_bytes}\npercentage_complete {percentage_complete}\nprogress {progress}")
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Downloading {current_number}/{total_items}"))
                            self.after(1, self.progress_bar.set(progress))
                            self.after(1, lambda v=net_speed: self.label_speed.configure(text=f"Network Speed: {v:.2f} {speed_unit}"))
                            self.after(1, lambda p=min(percentage_complete ,99): self.progress_text.configure(text=f"{p:.2f}%"))
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                            time.sleep(1)
                        else:
                            if not self.settings_tab.stopped:
                                time_elapsed = time.time() - start_time
                                progress = int(current_size / file_size * 100)
                                self.after(1, lambda v=progress / 100.0: self.progress_bar.set(v))

                                current_net_speed = psutil.net_io_counters().bytes_recv

                                net_speed_bytes = current_net_speed - previous_net_speed
                                previous_net_speed = current_net_speed

                                net_speed, speed_unit = convert_speed(net_speed_bytes)
                                elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)

                                self.after(1, self.status_text.configure(
                                    text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Downloading {current_number}/{total_items}"))
                                self.after(1, lambda v=net_speed: self.label_speed.configure(text=f"Network Speed: {v:.2f} {speed_unit}"))
                                self.after(1, lambda p=progress: self.progress_text.configure(text=f"{p}%"))
                                if self.settings_tab.show_fails:
                                    self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                                else:
                                    self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                                time.sleep(1)

                command = f"+login anonymous app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
                steamcmd_thread = threading.Thread(target=lambda: self.run_steamcmd_command(command, map_folder, workshop_id, queue=True))
                steamcmd_thread.start()

                def wait_for_threads():
                    update_ui_thread = threading.Thread(target=check_and_update_progress)
                    update_ui_thread.daemon = True
                    update_ui_thread.start()
                    update_ui_thread.join()

                    self.progress_text.configure(text="0%")
                    self.progress_bar.set(0.0)

                    map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

                    json_file_path = os.path.join(map_folder, "workshop.json")

                    if os.path.exists(json_file_path):
                        self.label_speed.configure(text="Installing...")
                        mod_type = extract_json_data(json_file_path, "Type")
                        folder_name = extract_json_data(json_file_path, "PublisherID")

                        if mod_type == "mod":
                            mods_folder = os.path.join(destination_folder, "mods")
                            folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                        elif mod_type == "map":
                            usermaps_folder = os.path.join(destination_folder, "usermaps")
                            folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                        else:
                            show_message("Error", f"Invalid workshop type in workshop.json, are you sure this is a map or a mod?., skipping {workshop_id}...", icon="cancel")
                            return

                        os.makedirs(folder_name_path, exist_ok=True)

                        try:
                            self.copy_with_progress(map_folder, folder_name_path)
                        except Exception as E:
                            show_message("Error", f"Error copying files: {E}", icon="cancel")

                        if self.settings_tab.clean_on_finish:
                            remove_tree(map_folder)
                            remove_tree(download_folder)

                        self.library_tab.update_item(self.edit_destination_folder.get(), workshop_id, mod_type, folder_name)

                        if index == len(items) - 1:
                            self.after(1, self.status_text.configure(text=f"Status: Done! => Please press stop only if you see no popup window (rare bug)"))
                            self.show_complete_message(message=f"All files were downloaded\nYou can run the game now!\nPS: You have to restart the game \n(pressing launch will launch/restarts)")
                            self.label_speed.configure(text="Awaiting Download!")
                    elif os.path.exists(json_file_path) and not self.settings_tab.stopped:
                        show_message("Error", "Failed to find workshop.json, please try again.", icon="cancel")
                        if index == len(items) - 1:
                            self.stop_download()
                        return

                self.button_download.configure(state="disabled")
                self.button_stop.configure(state="normal")
                update_wait_thread = threading.Thread(target=wait_for_threads)
                update_wait_thread.start()
                steamcmd_thread.join()
                update_wait_thread.join()

                if index == len(items) - 1:
                    self.button_download.configure(state="normal")
                    self.button_stop.configure(state="disabled")
                    self.after(1, self.status_text.configure(text=f"Status: Done!"))
                    self.skip_boutton.grid_remove()
                    self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
                    self.settings_tab.stopped = True
                    self.stop_download()
                    return
        finally:
            self.settings_tab.steam_fail_counter = 0
            self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
            self.stop_download()
            self.is_pressed = False

    def download_thread(self, update=None):
        try:
            self.settings_tab.stopped = False

            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_steam_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                self.show_init_message()
                return

            workshop_id = self.edit_workshop_id.get().strip()

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder.")
                self.stop_download()
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path.")
                self.stop_download()
                return

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                        self.stop_download()
                        return
                except:
                    show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                    self.stop_download()
                    return

            ws_file_size = get_workshop_file_size(workshop_id)
            file_size = ws_file_size

            if not valid_id(workshop_id):
                show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                self.stop_download()
                return

            if file_size is None:
                show_message("Error", "Failed to retrieve file size.", icon="cancel")
                self.stop_download()
                return

            if not update:
                if any(workshop_id in item for item in self.library_tab.added_items):
                    if self.settings_tab.skip_already_installed:
                        show_message("Heads up!, map skipped => Skip is on in settings", f"This item may already be installed, Stopping: {workshop_id}", icon="info")
                        self.stop_download()
                        return
                    show_message("Heads up! map not skipped => Skip is off in settings", f"This item may already be installed: {workshop_id}", icon="info")

            self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
            download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
            map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            def check_and_update_progress():
                previous_net_speed = 0
                est_downloaded_bytes = 0
                start_time = time.time()
                file_size = ws_file_size

                while not self.settings_tab.stopped:
                    if self.settings_tab.steamcmd_reset:
                        self.settings_tab.steamcmd_reset = False
                        previous_net_speed = 0
                        est_downloaded_bytes = 0

                    while not self.is_downloading and not self.settings_tab.stopped:
                        self.after(1, self.label_speed.configure(text=f"Waiting for steamcmd..."))
                        time_elapsed = time.time() - start_time
                        elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)
                        if self.settings_tab.show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                        time.sleep(1)
                        if self.is_downloading:
                            break

                    try:
                        current_size = sum(os.path.getsize(os.path.join(download_folder, f)) for f in os.listdir(download_folder))
                    except:
                        try:
                            current_size = sum(os.path.getsize(os.path.join(map_folder, f)) for f in os.listdir(map_folder))
                        except:
                            continue

                    progress = int(current_size / file_size * 100)

                    if progress > 100:
                        progress = int(current_size / current_size * 100)
                        file_size = current_size
                        self.after(1, lambda p=progress: self.label_file_size.configure(text=f"Wrong size reported\nActual size: ~{convert_bytes_to_readable(current_size)}"))


                    if self.settings_tab.estimated_progress and not self.settings_tab.stopped:
                        time_elapsed = time.time() - start_time
                        raw_net_speed = psutil.net_io_counters().bytes_recv

                        current_net_speed_text = raw_net_speed
                        net_speed_bytes = current_net_speed_text - previous_net_speed
                        previous_net_speed = current_net_speed_text

                        current_net_speed = net_speed_bytes
                        down_cap = 150000000
                        if current_net_speed >= down_cap:
                            current_net_speed = 10

                        est_downloaded_bytes += current_net_speed

                        percentage_complete = (est_downloaded_bytes / file_size) * 100

                        progress = min(percentage_complete / 100, 0.99)

                        net_speed, speed_unit = convert_speed(net_speed_bytes)

                        elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)

                        # print(f"raw_net {raw_net_speed}\ncurrent_net_speed: {current_net_speed}\nest_downloaded_bytes {est_downloaded_bytes}\npercentage_complete {percentage_complete}\nprogress {progress}")

                        self.after(1, self.progress_bar.set(progress))
                        self.after(1, lambda v=net_speed: self.label_speed.configure(text=f"Network Speed: {v:.2f} {speed_unit}"))
                        self.after(1, lambda p=min(percentage_complete ,99): self.progress_text.configure(text=f"{p:.2f}%"))
                        if self.settings_tab.show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                        time.sleep(1)
                    else:
                        if not self.settings_tab.stopped:
                            time_elapsed = time.time() - start_time
                            progress = int(current_size / file_size * 100)
                            self.after(1, lambda v=progress / 100.0: self.progress_bar.set(v))

                            current_net_speed = psutil.net_io_counters().bytes_recv

                            net_speed_bytes = current_net_speed - previous_net_speed
                            previous_net_speed = current_net_speed

                            net_speed, speed_unit = convert_speed(net_speed_bytes)
                            elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)

                            self.after(1, lambda v=net_speed: self.label_speed.configure(text=f"Network Speed: {v:.2f} {speed_unit}"))
                            self.after(1, lambda p=progress: self.progress_text.configure(text=f"{p}%"))
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                            time.sleep(1)

            command = f"+login anonymous app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
            steamcmd_thread = threading.Thread(target=lambda: self.run_steamcmd_command(command, map_folder, workshop_id))
            steamcmd_thread.start()

            def wait_for_threads():
                update_ui_thread = threading.Thread(target=check_and_update_progress)
                update_ui_thread.daemon = True
                update_ui_thread.start()
                update_ui_thread.join()

                self.settings_tab.stopped = True
                self.progress_text.configure(text="0%")
                self.progress_bar.set(0.0)

                map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

                json_file_path = os.path.join(map_folder, "workshop.json")

                if os.path.exists(json_file_path):
                    self.label_speed.configure(text="Installing...")
                    mod_type = extract_json_data(json_file_path, "Type")
                    folder_name = extract_json_data(json_file_path, "PublisherID")

                    if mod_type == "mod":
                        mods_folder = os.path.join(destination_folder, "mods")
                        folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                    elif mod_type == "map":
                        usermaps_folder = os.path.join(destination_folder, "usermaps")
                        folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                    else:
                        show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                        self.stop_download()
                        return

                    os.makedirs(folder_name_path, exist_ok=True)

                    try:
                        self.copy_with_progress(map_folder, folder_name_path)
                    except Exception as E:
                        show_message("Error", f"Error copying files: {E}", icon="cancel")

                    if self.settings_tab.clean_on_finish:
                        remove_tree(map_folder)
                        remove_tree(download_folder)

                    self.library_tab.update_item(self.edit_destination_folder.get(), workshop_id, mod_type, folder_name)
                    self.show_complete_message(message=f"{mod_type.capitalize()} files were downloaded\nYou can run the game now!\nPS: You have to restart the game \n(pressing launch will launch/restarts)")
                    self.button_download.configure(state="normal")
                    self.button_stop.configure(state="disabled")
                elif os.path.exists(json_file_path) and not self.settings_tab.stopped:
                    show_message("Error", "Failed to find workshop.json, please try again.", icon="cancel")
                    self.stop_download()
                    return

            update_wait_thread = threading.Thread(target=wait_for_threads)
            update_wait_thread.start()
            self.button_download.configure(state="disabled")
            self.button_stop.configure(state="normal")
            steamcmd_thread.join()
            update_wait_thread.join()

        finally:
            self.settings_tab.steam_fail_counter = 0
            self.stop_download()
            self.is_pressed = False

    def copy_with_progress(self, src, dst):
        try:
            total_files = sum([len(files) for root, dirs, files in os.walk(src)])
            progress = 0

            def copy_progress(src, dst):
                nonlocal progress
                shutil.copy2(src, dst)
                progress += 1
                self.progress_text.configure(text=f"Copying files: {progress}/{total_files}")
                value = (progress / total_files) * 100
                valuep = value / 100
                self.progress_bar.set(valuep)

            try:
                shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=copy_progress)
            except Exception as E:
                show_message("Error", f"Error copying files: {E}", icon="cancel")
        finally:
            self.progress_text.configure(text="0%")
            self.progress_bar.set(0.0)

    def stop_download(self, on_close=None):
        self.settings_tab.stopped = True
        self.queue_stop_button = True
        self.settings_tab.steam_fail_counter = 0
        self.is_pressed = False
        self.is_downloading = False
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

        if on_close:
            subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
            return

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)

        self.button_download.configure(state="normal")
        self.button_stop.configure(state="disabled")
        self.progress_text.configure(text="0%")
        self.elapsed_time.configure(text=f"")
        self.progress_bar.set(0.0)
        self.after(50, self.status_text.configure(text=f"Status: Standby!"))
        self.after(1, self.label_speed.configure(text=f"Awaiting Download!"))
        self.skip_boutton.grid_remove()

if __name__ == "__main__":
    app = BOIIIWD()
    app.mainloop()
