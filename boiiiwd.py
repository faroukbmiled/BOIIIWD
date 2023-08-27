from CTkMessagebox import CTkMessagebox
from bs4 import BeautifulSoup
import customtkinter as ctk
from CTkToolTip import *
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

VERSION = "v0.2.3"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
UPDATER_FOLDER = "update"
CONFIG_FILE_PATH = "config.ini"
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), 'resources')

# fuck it we ball, ill get rid of globals when i finish everything cant be bothered rn
global stopped, steampid, console, clean_on_finish, continuous, estimated_progress, steam_fail_counter, \
    steam_fail_counter_toggle, steam_fail_number, steamcmd_reset, show_fails
steampid = None
stopped = False
console = False
clean_on_finish = True
continuous = True
estimated_progress = True
steam_fail_counter_toggle = False
steam_fail_counter = 0
steam_fail_number = 10
steamcmd_reset = False
show_fails = True

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
    return config.get("Settings", name, fallback="on")

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

def run_steamcmd_command(command, self, map_folder, queue=None):
    global steampid, stopped, steam_fail_counter, steam_fail_number, steamcmd_reset
    steamcmd_path = get_steamcmd_path()
    show_console = subprocess.CREATE_NO_WINDOW
    if console:
        show_console = subprocess.CREATE_NEW_CONSOLE

    if os.path.exists(map_folder):
        try:
            try:
                os.remove(map_folder)
            except:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
                os.rename(map_folder, os.path.join(map_folder, os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", f"couldntremove_{timestamp}")))
        except Exception as e:
            stopped = True
            self.queue_stop_button = True
            show_message("Error", f"Couldn't remove {map_folder}, please do so manually\n{e}", icon="cancel")
            return

    if continuous:
        while not os.path.exists(map_folder) and not stopped:
            process = subprocess.Popen(
                [steamcmd_path + "\steamcmd.exe"] + command.split(),
                stdout=None if console else subprocess.PIPE,
                stderr=None if console else subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=show_console
            )

            steampid = process.pid

            if process.poll() is not None:
                return process.returncode

            process.communicate()
            steam_fail_counter = steam_fail_counter + 1
            if steam_fail_counter_toggle:
                # print(steam_fail_counter)
                try:
                    if steam_fail_counter >= int(steam_fail_number):
                        reset_steamcmd(no_warn=True)
                        steamcmd_reset = True
                        steam_fail_counter = 0
                except:
                    if steam_fail_counter >= 10:
                        reset_steamcmd(no_warn=True)
                        steam_fail_counter = 0
    else:
        process = subprocess.Popen(
            [steamcmd_path + "\steamcmd.exe"] + command.split(),
            stdout=None if console else subprocess.PIPE,
            stderr=None if console else subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
            creationflags=show_console
        )

        steampid = process.pid

        if process.poll() is not None:
            return process.returncode

        process.communicate()

        if not os.path.exists(map_folder):
            show_message("SteamCMD has terminated", "SteamCMD has been terminated\nAnd failed to download the map/mod, try again or enable continuous download in settings")

    stopped = True
    if not queue:
        self.button_download.configure(state="normal")
        self.button_stop.configure(state="disabled")

    return process.returncode

def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback=cwd())

def extract_json_data(json_path, key):
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    return data[key]

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

# End helper functions

class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, update_url):
        global master_win
        master_win = master
        super().__init__(master)
        self.title("BOIIIWD Self-Updater")
        self.geometry("400x150")
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

class LibraryTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.added_items = set()
        self.grid_columnconfigure(0, weight=1)

        self.radiobutton_variable = ctk.StringVar()
        self.no_items_label = ctk.CTkLabel(self, text="", anchor="w")
        self.filter_entry = ctk.CTkEntry(self, placeholder_text="Your search query here, or type in mod or map to see only that")
        self.filter_entry.bind("<KeyRelease>", self.filter_items)
        self.filter_entry.grid(row=0, column=0,  padx=(10, 20), pady=(10, 20), sticky="we")
        filter_refresh_button_image = os.path.join(RESOURCES_DIR, "Refresh_icon.svg.png")
        self.filter_refresh_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(filter_refresh_button_image)), command=self.refresh_items, width=20, height=20,
                                                   fg_color="transparent", text="")
        self.filter_refresh_button.grid(row=0, column=1, padx=(10, 20), pady=(10, 20), sticky="enw")
        self.label_list = []
        self.button_list = []
        self.button_view_list = []
        self.filter_type = True

    def add_item(self, item, image=None, item_type="map", workshop_id=None, folder=None):
        label = ctk.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text="Remove", width=60, height=24, fg_color="#3d3f42")
        button_view = ctk.CTkButton(self, text="Details", width=55, height=24, fg_color="#3d3f42")
        button.configure(command=lambda: self.remove_item(item, folder))
        button_view.configure(command=lambda: self.show_map_info(workshop_id))
        button_view_tooltip = CTkToolTip(button_view, message="Opens up a window that shows basic details")
        button_tooltip = CTkToolTip(button, message="Removes the map/mod from your game")
        label.grid(row=len(self.label_list) + 1, column=0, pady=(0, 10), padx=(5, 10), sticky="w")
        button.grid(row=len(self.button_list) + 1, column=1, pady=(0, 10), padx=(50, 10), sticky="e")
        button_view.grid(row=len(self.button_view_list) + 1, column=1, pady=(0, 10), padx=(10, 75), sticky="w")
        self.label_list.append(label)
        self.button_list.append(button)
        self.button_view_list.append(button_view)

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
        # if you add this under init the whole app shrinks for some reason
        global boiiiFolderGlobal
        boiiiFolderGlobal = boiiiFolder
        maps_folder = os.path.join(boiiiFolder, "mods")
        mods_folder = os.path.join(boiiiFolder, "usermaps")

        folders_to_process = [mods_folder, maps_folder]

        for folder_path in folders_to_process:
            for root, _, _ in os.walk(folder_path):
                zone_path = os.path.join(root, "zone")
                if os.path.exists(zone_path):
                    json_path = os.path.join(zone_path, "workshop.json")
                    if os.path.exists(json_path):
                        name = extract_json_data(json_path, "Title").replace(">", "").replace("^", "")
                        name = name[:35] + "..." if len(name) > 35 else name
                        item_type = extract_json_data(json_path, "Type")
                        workshop_id = extract_json_data(json_path, "PublisherID")
                        size = convert_bytes_to_readable(get_folder_size(root))
                        text_to_add = f"{name} | Type: {item_type} | ID: {workshop_id} | Size: {size}"
                        if text_to_add not in self.added_items:
                            self.added_items.add(text_to_add)

                            if item_type == "mod":
                                image_path = os.path.join(RESOURCES_DIR, "mod_image.png")
                            else:
                                image_path = os.path.join(RESOURCES_DIR, "map_image.png")

                            self.add_item(text_to_add, image=ctk.CTkImage(Image.open(image_path)), item_type=item_type, workshop_id=workshop_id, folder=root)
        if not self.added_items:
            self.show_no_items_message()
        else:
            self.hide_no_items_message()

    def remove_item(self, item, folder):
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
                self.button_view_list.remove(button_view_list)

    def refresh_items(self):
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            label.destroy()
            button.destroy()
            button_view_list.destroy()
        self.label_list.clear()
        self.button_list.clear()
        self.button_view_list.clear()
        self.added_items.clear()
        self.load_items(boiiiFolderGlobal)

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

                self.toplevel_info_window(map_name, map_mod_type, map_size, image, image_size, date_created ,
                                        date_updated, stars_image, stars_image_size, ratings_text, url)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
                return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size, ratings_text, url):
        try:
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

            size_label = ctk.CTkLabel(info_frame, text=f"Size (Workshop): {map_size}")
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

        finally:
            for button_view in self.button_view_list:
                button_view.configure(state="normal")

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
        self.estimated_progress = ctk.CTkSwitch(left_frame, text="Estimated Progress Bar", variable=self.estimated_progress_var)
        self.estimated_progress.grid(row=4, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.estimated_progress_var_tooltip = CTkToolTip(self.estimated_progress, message="This will change how to progress bar works by estimating how long the download will take\
            \nThis is not accurate ,it's better than with it off which is calculating the downloaded folder size which steamcmd dumps the full size rigth mostly")
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))

        # Show estimated_progress checkbox
        self.show_fails_var = ctk.BooleanVar()
        self.show_fails_var.trace_add("write", self.enable_save_button)
        self.show_fails = ctk.CTkSwitch(left_frame, text="Show fails (on top of progress bar):", variable=self.show_fails_var)
        self.show_fails.grid(row=5, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.show_fails_tooltip = CTkToolTip(self.show_fails, message="Display how many times steamcmd has failed/crashed\nIf the number is getting high quickly then try pressing Reset SteamCMD and try again, otherwise its fine")
        self.estimated_progress_var.set(self.load_settings("show_fails", "on"))

        # Resetr steam on many fails
        self.reset_steamcmd_on_fail_var = ctk.IntVar()
        self.reset_steamcmd_on_fail_var.trace_add("write", self.enable_save_button)
        self.reset_steamcmd_on_fail_text = ctk.CTkLabel(left_frame, text=f"Reset steamcmd on % fails: (n of fails)", anchor="w")
        self.reset_steamcmd_on_fail_text.grid(row=6, column=1, padx=20, pady=(10, 0), sticky="nw")
        self.reset_steamcmd_on_fail = ctk.CTkOptionMenu(left_frame, values=["20", "30", "40", "Custom", "Disable"], variable=self.reset_steamcmd_on_fail_var, command=self.reset_steamcmd_on_fail_func)
        self.reset_steamcmd_on_fail.grid(row=7, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.reset_steamcmd_on_fail_tooltip = CTkToolTip(self.reset_steamcmd_on_fail, message="This actually fixes steamcmd when its crashing way too much")
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "Disable"))

        # Check for updates button n Launch boiii
        self.check_for_updates = ctk.CTkButton(right_frame, text="Check for updates", command=self.settings_check_for_updates)
        self.check_for_updates.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="n")

        self.launch_boiii = ctk.CTkButton(right_frame, text="Launch boiii", command=self.settings_launch_boiii)
        self.launch_boiii.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="n")

        self.reset_steamcmd = ctk.CTkButton(right_frame, text="Reset SteamCMD", command=self.settings_reset_steamcmd)
        self.reset_steamcmd.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="n")
        self.reset_steamcmd_tooltip = CTkToolTip(self.reset_steamcmd, message="This will remove steamapps folder + all the maps that are potentioaly corrupted or not so use at ur own risk (could fix some issues as well)")

        # appearance
        self.appearance_mode_label = ctk.CTkLabel(right_frame, text="Appearance Mode:", anchor="n")
        self.appearance_mode_label.grid(row=4, column=1, padx=20, pady=(20, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(right_frame, values=["Light", "Dark", "System"],
                                                                       command=master.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=5, column=1, padx=20, pady=(0, 0))
        self.scaling_label = ctk.CTkLabel(right_frame, text="UI Scaling:", anchor="n")
        self.scaling_label.grid(row=6, column=1, padx=20, pady=(10, 0))
        self.scaling_optionemenu = ctk.CTkOptionMenu(right_frame, values=["80%", "90%", "100%", "110%", "120%"],
                                                               command=master.change_scaling_event)
        self.scaling_optionemenu.grid(row=7, column=1, padx=20, pady=(0, 0))

        # self.custom_theme = ctk.CTkButton(right_frame, text="Custom theme", command=self.boiiiwd_custom_theme)
        # self.custom_theme.grid(row=8, column=1, padx=20, pady=(20, 0), sticky="n")

        self.theme_options_label = ctk.CTkLabel(right_frame, text="Themes:", anchor="n")
        self.theme_options_label.grid(row=8, column=1, padx=20, pady=(10, 0))
        self.theme_options = ctk.CTkOptionMenu(right_frame, values=["Default", "Blue", "Grey", "Custom"],
                                                               command=self.theme_options_func)
        self.theme_options.grid(row=9, column=1, padx=20, pady=(0, 0))
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
                save_config("reset_on_fail", self.reset_steamcmd_on_fail.get())
                if show_message("config.ini" ,"change reset_on_fail value to whatever you want", exit_on_close=True):
                    os.system(f"notepad {os.path.join(cwd(), 'config.ini')}")
            except:
                show_message("Couldn't open config.ini" ,"you can do so by yourself and change reset_on_fail value to whatever you want")
        else:
            pass
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
        if option == "Custom":
            self.boiiiwd_custom_theme()
            save_config("theme", "boiiiwd_theme.json")

        if not option == "Custom":
            show_message("Restart to take effect!", f"{option} theme has been set ,please restart to take effect", icon="info")

    def enable_save_button(self, *args):
        try:
            self.save_button.configure(state='normal')
        except:
            pass

    def save_settings(self):
        self.save_button.configure(state='disabled')
        global console, clean_on_finish, continuous, estimated_progress, steam_fail_number, steam_fail_counter_toggle, show_fails
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

        if self.checkbox_continuous.get():
            save_config("continuous_download", "on")
            continuous = True
        else:
            save_config("continuous_download", "off")
            continuous = False

        if self.estimated_progress.get():
            save_config("estimated_progress", "on")
            estimated_progress = True
        else:
            save_config("estimated_progress", "off")
            estimated_progress = False

        if self.show_fails.get():
            save_config("show_fails", "on")
            show_fails = True
        else:
            save_config("show_fails", "off")
            show_fails = False

        if self.reset_steamcmd_on_fail.get():
            value = self.reset_steamcmd_on_fail.get()
            if value == "Disable":
                steam_fail_counter_toggle = False
            else:
                steam_fail_counter_toggle = True
                steam_fail_number = int(value)
            save_config("reset_on_fail", value)

    def load_settings(self, setting, fallback=None):
        global console, clean_on_finish, continuous, estimated_progress, steam_fail_counter_toggle, steam_fail_number, show_fails
        if setting == "console":
            if check_config(setting, fallback) == "on":
                console = True
                return 1
            else:
                console = False
                return 0

        if setting == "continuous_download":
            if check_config(setting, "on") == "on":
                continuous = True
                return 1
            else:
                continuous = False
                return 0

        if setting == "clean_on_finish":
            if check_config(setting, fallback) == "on":
                clean_on_finish = True
                return 1
            else:
                clean_on_finish = False
                return 0
        if setting == "estimated_progress":
            if check_config(setting, fallback) == "on":
                estimated_progress = True
                return 1
            else:
                estimated_progress = False
                return 0

        if setting == "reset_on_fail":
            option = check_config(setting, fallback)
            if option == "Disable" or option == "Custom":
                steam_fail_counter_toggle = False
                return "Disable"
            else:
                try:
                    steam_fail_number = int(option)
                    return option
                except:
                    if steam_fail_counter_toggle:
                        steam_fail_number = 10
                        return "10"
                    else:
                        steam_fail_number = 10
                        return "Disable"

        if setting == "show_fails":
            if check_config(setting, fallback) == "on":
                show_fails = True
                return 1
            else:
                show_fails = False
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
        else:
            if check_config(setting, fallback) == "on":
                return 1
            else:
                return 0

    def boiiiwd_custom_theme(self, disable_only=None):
        file_to_rename = os.path.join(cwd(), "boiiiwd_theme.json")
        if os.path.exists(file_to_rename):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
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
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "Disable"))
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))
        self.clean_checkbox_var.set(self.load_settings("clean_on_finish", "on"))
        self.continuous_var.set(self.load_settings("continuous_download"))
        self.show_fails_var.set(self.load_settings("show_fails", "on"))

        # keep last cuz of trace_add()
        self.save_button.configure(state='disabled')

    def settings_launch_boiii(self):
        launch_boiii_func(check_config("destinationfolder"))

    def settings_reset_steamcmd(self):
        reset_steamcmd()

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

        self.help_button = ctk.CTkButton(master=self.qeueuframe, text="help", command=self.help_queue_text_func, width=10, height=10, fg_color="#585858")
        self.help_button.grid(row=0, column=1, padx=(0, 20), pady=(20, 20), sticky="wns")
        self.help_button_tooltip = CTkToolTip(self.help_button, message="This only works if the text area is empty (press twice if you had something in it)")

        self.queuetextarea = ctk.CTkTextbox(master=self.qeueuframe, font=("", 15))
        self.queuetextarea.grid(row=1, column=0, columnspan=2,rowspan=2, padx=(20, 20), pady=(0, 20), sticky="nwse")

        self.status_text = ctk.CTkLabel(self.qeueuframe, text="Status: Not Downloading")
        self.status_text.grid(row=3, column=0, padx=(20, 20), pady=(0, 20), sticky="ws")

        self.qeueuframe.grid_remove()

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.settings_tab = SettingsTab(self)
        self.library_tab = LibraryTab(self, corner_radius=3)

        # create sidebar frame with widgets
        font = "Comic Sans MS"
        ryuks_icon = os.path.join(RESOURCES_DIR, "ryuk.png")
        self.sidebar_icon = ctk.CTkImage(light_image=Image.open(ryuks_icon), dark_image=Image.open(ryuks_icon), size=(40, 40))
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, padx=(10, 20), pady=(10, 10), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text='',image=self.sidebar_icon)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.txt_label = ctk.CTkLabel(self.sidebar_frame, text="- Sidebar -", font=(font, 17))
        self.txt_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_main = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_main.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_queue = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_queue.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_library = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_library.grid(row=4, column=0, padx=20, pady=10, sticky="n")
        self.sidebar_settings = ctk.CTkButton(self.sidebar_frame)
        self.sidebar_settings.grid(row=5, column=0, padx=20, pady=10, sticky="n")

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

        self.label_speed = ctk.CTkLabel(master=self.slider_progressbar_frame, text="Network Speed: 0 KB/s")
        self.label_speed.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        self.elapsed_time = ctk.CTkLabel(master=self.slider_progressbar_frame, text="")
        self.elapsed_time.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="nsew", columnspan=1)

        self.label_file_size = ctk.CTkLabel(master=self.slider_progressbar_frame, text="File size: 0KB")
        self.label_file_size.grid(row=1, column=2, padx=(0, 20), pady=(0, 10), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(master=self.slider_progressbar_frame, mode="determinate", height=20, corner_radius=7)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 10), columnspan=3, sticky="ew")

        self.progress_text = ctk.CTkLabel(self.progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", height=0, width=0, corner_radius=0)
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
            self.settings_tab.load_settings("reset_on_fail", "Disable")
            self.settings_tab.load_settings("show_fails", "on")
        except:
            pass

        if not check_steamcmd():
            self.show_warning_message()

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
        self.library_tab.load_items(self.edit_destination_folder.get())
        self.library_tab.grid(row=0, rowspan=3, column=1, padx=(0, 20), pady=(20, 20), sticky="nsew")

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

    def help_queue_text_func(self):
        if any(char.isalpha() for char in self.queuetextarea.get("1.0", "end")):
            self.workshop_queue_label.configure(text="Workshop IDs/Links => press help to see examples:")
            self.queuetextarea.configure(state="normal")
            self.queuetextarea.delete(1.0, "end")
            self.queuetextarea.insert(1.0, "")
        else:
            self.workshop_queue_label.configure(text="Workshop IDs/Links => press help again to remove examples:")
            self.queuetextarea.insert(1.0, "3010399939,2976006537,2118338989,...\nor:\n3010399939\n2976006537\n2113146805\n...")
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

    def download_map(self):
        if not self.is_pressed:
            self.is_pressed = True
            if self.queue_enabled:
                start_down_thread = threading.Thread(target=self.queue_download_thread)
                start_down_thread.start()
            else:
                start_down_thread = threading.Thread(target=self.download_thread)
                start_down_thread.start()
        else:
            show_message("Warning", "Already pressed, Please wait.")

    def queue_download_thread(self):
        global stopped
        stopped = False
        self.queue_stop_button = False
        try:
            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                if not show_message("Warning", "SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.",
                            icon="warning" ,exit_on_close=True):
                    pass
                else:
                    initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                    initialize_steam_thread.start()
                return

            text = self.queuetextarea.get("1.0", "end")
            items = []
            if "," in text:
                items = [n.strip() for n in text.split(",")]
            else:
                items = [n.strip() for n in text.split("\n") if n.strip()]

            if not items:
                show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                self.stop_download
                return

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder => in the main tab!.")
                self.stop_download
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path => in the main tab!.")
                self.stop_download
                return

            self.total_queue_size = 0
            for item in items:
                item.strip()
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download
                        return
                if not valid_id(workshop_id):
                    show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                    self.stop_download
                    return

                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.total_queue_size += ws_file_size

                if file_size is None:
                    show_message("Error", "Failed to retrieve file size.", icon="cancel")
                    self.stop_download
                    return

            self.after(1, self.status_text.configure(text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)}"))
            start_time = time.time()
            for index, item in enumerate(items):
                current_number = index + 1
                total_items = len(items)
                if self.queue_stop_button:
                    self.stop_download
                    break
                item.strip()
                stopped = False
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download
                        return
                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
                download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
                map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)

                def check_and_update_progress():
                    # delay untill steam boots up and starts downloading (ive a better idea ill implement it later)
                    time.sleep(8)
                    global stopped, steamcmd_reset
                    previous_net_speed = 0
                    est_downloaded_bytes = 0
                    file_size = ws_file_size
                    item_name = get_item_name(workshop_id) if get_item_name(workshop_id) else "Error getting name"

                    while not stopped:
                        if steamcmd_reset:
                            steamcmd_reset = False
                            previous_net_speed = 0
                            est_downloaded_bytes = 0

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
                            self.total_queue_size -= file_size
                            file_size = current_size
                            self.total_queue_size += file_size
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Downloading {current_number}/{total_items}"))
                            self.after(1, lambda p=progress: self.label_file_size.configure(text=f"Wrong size reported\nFile size: ~{convert_bytes_to_readable(current_size)}"))

                        if estimated_progress:
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
                            if show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {steam_fail_counter}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                            time.sleep(1)
                        else:
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
                            if show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {steam_fail_counter}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                            time.sleep(1)

                command = f"+login anonymous +@sSteamCmdForcePlatformBitness 64 +app_info_update 1 +app_info_print 311210 app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
                steamcmd_thread = threading.Thread(target=lambda: run_steamcmd_command(command, self, map_folder, queue=True))
                steamcmd_thread.start()

                def wait_for_threads():
                    update_ui_thread = threading.Thread(target=check_and_update_progress)
                    update_ui_thread.daemon = True
                    update_ui_thread.start()
                    update_ui_thread.join()

                    self.label_speed.configure(text="Network Speed: 0 KB/s")
                    self.progress_text.configure(text="0%")
                    self.progress_bar.set(0.0)

                    map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

                    json_file_path = os.path.join(map_folder, "workshop.json")

                    if os.path.exists(json_file_path):
                        mod_type = extract_json_data(json_file_path, "Type")
                        folder_name = extract_json_data(json_file_path, "FolderName")

                        if mod_type == "mod":
                            mods_folder = os.path.join(destination_folder, "mods")
                            folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                        elif mod_type == "map":
                            usermaps_folder = os.path.join(destination_folder, "usermaps")
                            folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                        else:
                            show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                            self.stop_download
                            return

                        os.makedirs(folder_name_path, exist_ok=True)

                        try:
                            shutil.copytree(map_folder, folder_name_path, dirs_exist_ok=True)
                        except Exception as E:
                            show_message("Error", f"Error copying files: {E}", icon="cancel")

                        if clean_on_finish:
                            remove_tree(map_folder)
                            remove_tree(download_folder)

                        if index == len(items) - 1:
                            msg = CTkMessagebox(title="Downloads Complete", message=f"All files were downloaded\nYou can run the game now!", icon="info", option_1="Launch", option_2="Ok")
                            response = msg.get()
                            if response=="Launch":
                                launch_boiii_func(self.edit_destination_folder.get().strip())
                            if response=="Ok":
                                pass

                self.button_download.configure(state="disabled")
                self.button_stop.configure(state="normal")
                update_wait_thread = threading.Thread(target=wait_for_threads)
                update_wait_thread.start()
                steamcmd_thread.join()
                update_wait_thread.join()

                if index == len(items) - 1:
                    self.button_download.configure(state="normal")
                    self.button_stop.configure(state="disabled")
                    self.after(1, self.status_text.configure(text=f"Status: Done"))
                    self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
                    stopped = True
                    self.stop_download
                    return
        finally:
            global steam_fail_counter
            steam_fail_counter = 0
            self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
            self.stop_download
            self.is_pressed = False

    def download_thread(self):
        try:
            global stopped
            stopped = False

            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                if not show_message("Warning", "SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.",
                            icon="warning" ,exit_on_close=True):
                    pass
                else:
                    initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                    initialize_steam_thread.start()
                return

            workshop_id = self.edit_workshop_id.get().strip()

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder.")
                self.stop_download
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path.")
                self.stop_download
                return

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                        self.stop_download
                        return
                except:
                    show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                    self.stop_download
                    return

            ws_file_size = get_workshop_file_size(workshop_id)
            file_size = ws_file_size

            if not valid_id(workshop_id):
                show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                self.stop_download
                return

            if file_size is None:
                show_message("Error", "Failed to retrieve file size.", icon="cancel")
                self.stop_download
                return

            self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
            download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
            map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            def check_and_update_progress():
                # delay untill steam boots up and starts downloading (ive a better idea ill implement it later)
                time.sleep(8)
                global stopped, steamcmd_reset
                previous_net_speed = 0
                est_downloaded_bytes = 0
                start_time = time.time()
                file_size = ws_file_size

                while not stopped:
                    if steamcmd_reset:
                        steamcmd_reset = False
                        previous_net_speed = 0
                        est_downloaded_bytes = 0

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

                    if estimated_progress:
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
                        if show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {steam_fail_counter}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                        time.sleep(1)
                    else:
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
                        if show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {steam_fail_counter}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                        time.sleep(1)

            command = f"+login anonymous +@sSteamCmdForcePlatformBitness 64 +app_info_update 1 +app_info_print 311210 app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
            steamcmd_thread = threading.Thread(target=lambda: run_steamcmd_command(command, self, map_folder))
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
                    mod_type = extract_json_data(json_file_path, "Type")
                    folder_name = extract_json_data(json_file_path, "FolderName")

                    if mod_type == "mod":
                        mods_folder = os.path.join(destination_folder, "mods")
                        folder_name_path = os.path.join(mods_folder, folder_name, "zone")
                    elif mod_type == "map":
                        usermaps_folder = os.path.join(destination_folder, "usermaps")
                        folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
                    else:
                        show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                        self.stop_download
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

        finally:
            global steam_fail_counter
            steam_fail_counter = 0
            self.stop_download
            self.is_pressed = False

    def stop_download(self, on_close=None):
        global stopped, steam_fail_counter
        stopped = True
        self.queue_stop_button = True
        steam_fail_counter = 0
        self.is_pressed = False
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

        if on_close:
            subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
            return

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)

        self.status_text.configure(text=f"Status: Not Downloading")
        self.button_download.configure(state="normal")
        self.button_stop.configure(state="disabled")
        self.label_speed.configure(text="Network Speed: 0 KB/s")
        self.progress_text.configure(text="0%")
        self.elapsed_time.configure(text=f"")
        self.progress_bar.set(0.0)

if __name__ == "__main__":
    app = BOIIIWD()
    app.mainloop()
