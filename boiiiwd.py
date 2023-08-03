import os
import sys
import re
import subprocess
import configparser
import json
import shutil
import zipfile
import psutil
import requests
import time
import threading
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QDialog, \
    QVBoxLayout, QMessageBox, QHBoxLayout, QProgressBar, QSizePolicy, QFileDialog, QCheckBox, QSpacerItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QCloseEvent
import webbrowser
import qdarktheme

VERSION = "v0.1.3"
GITHUB_REPO = "faroukbmiled/BOIIIWD"
LATEST_RELEASE_URL = "https://github.com/faroukbmiled/BOIIIWD/releases/latest/download/Release.zip"
UPDATER_FOLDER = "update"
CONFIG_FILE_PATH = "config.ini"
global stopped, steampid, console, up_cancelled
steampid = None
stopped = False
console = False
up_cancelled = False

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

def initialize_steam():
    try:
        steamcmd_path = get_steamcmd_path()
        steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")
        process = subprocess.Popen([steamcmd_exe_path, "+quit"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        process.wait()

        show_message("Done!", "BOIIIWD is ready for action.", icon=QMessageBox.Information)
    except:
        show_message("Done!", "An error occurred please check your paths and try again.")

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

def run_steamcmd_command(command):
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

    if process.returncode != 0:
        show_message("Warning", "SteamCMD encountered an error while downloading, try again!")

    return process.returncode

def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback=cwd())

def config_check_for_updates(state=None):
    if state:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        config["Settings"]["checkforupdtes"] = state
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        return
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "checkforupdtes", fallback="on")

def config_console_state(state=None):
    if state:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        config["Settings"]["console"] = state
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)
        return
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "console", fallback="off")

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

def update_progress_bar(current_size, file_size, progress_bar):
    if file_size is not None:
        progress = int(current_size / file_size * 100)
        progress_bar.setValue(progress)

def check_and_update_progress(file_size, folder_name_path, progress_bar, speed_label):
    previous_net_speed = 0

    while not stopped:
        current_size = sum(os.path.getsize(os.path.join(folder_name_path, f)) for f in os.listdir(folder_name_path))
        update_progress_bar(current_size, file_size, progress_bar)

        current_net_speed = psutil.net_io_counters().bytes_recv

        net_speed_bytes = current_net_speed - previous_net_speed
        previous_net_speed = current_net_speed

        net_speed, speed_unit = convert_speed(net_speed_bytes)

        speed_label.setText(f"Network Speed: {net_speed:.2f} {speed_unit}")

        QCoreApplication.processEvents()
        time.sleep(1)

def download_workshop_map(workshop_id, destination_folder, progress_bar, speed_label):
    file_size = get_workshop_file_size(workshop_id)
    if file_size is None:
        show_message("Error", "Failed to retrieve file size.")
        return

    download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    command = f"+login anonymous +workshop_download_item 311210 {workshop_id} +quit"
    progress_thread = threading.Thread(target=check_and_update_progress, args=(file_size, download_folder, progress_bar, speed_label))
    progress_thread.daemon = True
    progress_thread.start()

    run_steamcmd_command(command)

    global stopped
    stopped = True
    progress_bar.setValue(100)

    map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

    json_file_path = os.path.join(map_folder, "workshop.json")

    if os.path.exists(json_file_path):
        global mod_type
        mod_type, folder_name = extract_json_data(json_file_path)

        if mod_type == "mod":
            mods_folder = os.path.join(destination_folder, "mods")
            folder_name_path = os.path.join(mods_folder, folder_name, "zone")
        elif mod_type == "map":
            usermaps_folder = os.path.join(destination_folder, "usermaps")
            folder_name_path = os.path.join(usermaps_folder, folder_name, "zone")
        else:
            show_message("Error", "Invalid map type in workshop.json.")
            return

        os.makedirs(folder_name_path, exist_ok=True)

        try:
            shutil.copytree(map_folder, folder_name_path, dirs_exist_ok=True)
        except Exception as E:
            show_message("Error", f"Error copying files: {E}")

        show_message("Download Complete", f"{mod_type} files are downloaded at \n{folder_name_path}\nYou can run the game now!", icon=QMessageBox.Information)

def show_message(title, message, icon=QMessageBox.Warning, exit_on_close=False):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setWindowIcon(QIcon('ryuk.ico'))
    msg.setText(message)
    msg.setIcon(icon)

    if exit_on_close:
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Ok)
        result = msg.exec_()

        if result == QMessageBox.No:
            sys.exit(0)
    else:
        msg.exec_()

class UpdatePorgressThread(QThread):
    global up_cancelled
    progress_update = pyqtSignal(int)

    def __init__(self, label_progress, progress_bar, label_size):
        super().__init__()
        self.label_progress = label_progress
        self.progress_bar = progress_bar
        self.label_size = label_size
        self.cancelled = False

    def run(self):
        try:
            update_dir = os.path.join(os.getcwd(), UPDATER_FOLDER)
            response = requests.get(LATEST_RELEASE_URL, stream=True)
            response.raise_for_status()
            current_exe = sys.argv[0]
            program_name = os.path.basename(current_exe)
            new_exe = os.path.join(update_dir, "BOIIIWD.exe")

            if not os.path.exists(update_dir):
                os.makedirs(update_dir)

            zip_path = os.path.join(update_dir, "latest_version.zip")
            total_size = int(response.headers.get('content-length', 0))
            size = convert_bytes_to_readable(total_size)
            self.label_size.setText(f"Size: {size}")

            with open(zip_path, "wb") as zip_file:
                chunk_size = 8192
                current_size = 0

                for chunk in response.iter_content(chunk_size=chunk_size):
                    if up_cancelled:
                        break

                    if chunk:
                        zip_file.write(chunk)
                        current_size += len(chunk)
                        progress = int(current_size / total_size * 100)
                        self.progress_update.emit(progress)
                        QCoreApplication.processEvents()

            if not up_cancelled:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(update_dir)

                self.label_progress.setText("Update installed successfully!")
                time.sleep(1)
                script_path = create_update_script(current_exe, new_exe, update_dir, program_name)
                subprocess.run(('cmd', '/C', 'start', '', fr'{script_path}'))
                sys.exit(0)
            else:
                if os.path.exists(zip_path):
                    os.remove(fr"{zip_path}")
                self.label_progress.setText("Update cancelled.")

        except Exception as e:
            self.label_progress.setText("Error installing the update.")
            show_message("Warning", f"Error installing the update: {e}")

class UpdateProgressWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Updating...")
        self.setWindowIcon(QIcon('ryuk.ico'))

        layout = QVBoxLayout()

        info_layout = QHBoxLayout()
        self.label_progress = QLabel("Downloading latest update from Github...")
        info_layout.addWidget(self.label_progress, 3)

        self.label_size = QLabel("File size: 0KB")
        info_layout.addWidget(self.label_size, 1)

        layout.addLayout(info_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_update)
        button_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        global up_cancelled
        self.thread = None
        up_cancelled = False


    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def start_update(self):
        self.thread = UpdatePorgressThread(self.label_progress, self.progress_bar, self.label_size)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.finished.connect(self.on_update_finished)
        self.thread.start()

    def on_update_finished(self):
        """code"""
        # self.accept()

    def cancel_update(self):
        global up_cancelled
        up_cancelled = True
        self.label_progress.setText("Update cancelled.")

    def closeEvent(self, event: QCloseEvent):
        global up_cancelled
        if not up_cancelled:
            self.cancel_update()
        super().closeEvent(event)

class DownloadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, workshop_id, destination_folder, progress_bar, label_speed):
        super().__init__()
        self.workshop_id = workshop_id
        self.destination_folder = destination_folder
        self.progress_bar = progress_bar
        self.label_speed = label_speed

    def run(self):
        download_workshop_map(self.workshop_id, self.destination_folder, self.progress_bar, self.label_speed)
        self.finished.emit()

class WorkshopDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        if not check_steamcmd():
            self.show_warning_message()

        self.download_thread = None
        self.button_download.setEnabled(True)
        self.button_stop.setEnabled(False)

    def show_warning_message(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Warning")
        msg_box.setWindowIcon(QIcon('ryuk.ico'))
        msg_box.setText("steamcmd.exe was not found in the specified directory.\nPress Download to get it or Press OK and select it from there!.")
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        download_button = msg_box.addButton("Download", QMessageBox.AcceptRole)
        download_button.clicked.connect(self.download_steamcmd)
        msg_box.setDefaultButton(download_button)

        result = msg_box.exec_()
        if result == QMessageBox.Cancel:
            sys.exit(0)

    def download_steamcmd(self):
        self.edit_steamcmd_path.setText(cwd())
        self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())
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
                show_message("Success", "SteamCMD has been downloaded ,Press ok to initialize it.", icon=QMessageBox.Information, exit_on_close=True)
                initialize_steam()

            else:
                show_message("Error", "Failed to find steamcmd.exe after extraction.\nMake you sure to select the correct SteamCMD path (which is the current BOIIIWD path)")
                os.remove(fr"{steamcmd_zip_path}")
        except requests.exceptions.RequestException as e:
            show_message("Error", f"Failed to download SteamCMD: {e}")
            os.remove(fr"{steamcmd_zip_path}")
        except zipfile.BadZipFile:
            show_message("Error", "Failed to extract SteamCMD. The downloaded file might be corrupted.")
            os.remove(fr"{steamcmd_zip_path}")

    def check_for_updates(self, ignore_up_todate=False):
        try:
            latest_version = get_latest_release_version()
            current_version = VERSION

            if latest_version and latest_version != current_version:
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Update Available")
                msg_box.setWindowIcon(QIcon('ryuk.ico'))
                msg_box.setText(f"An update is available!, Do you want to install it?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Open)
                msg_box.setDefaultButton(QMessageBox.Yes)
                result = msg_box.exec_()

                if result == QMessageBox.Open:
                    webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")

                if result == QMessageBox.Yes:
                    update_progress_window = UpdateProgressWindow()
                    update_progress_window.start_update()
                    update_progress_window.exec_()
            elif latest_version == current_version:
                if ignore_up_todate:
                    return
                msg_box = QMessageBox()
                msg_box.setWindowTitle("Up to Date!")
                msg_box.setWindowIcon(QIcon('ryuk.ico'))
                msg_box.setText(f"No Updates Available!")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.setDefaultButton(QMessageBox.Ok)
                result = msg_box.exec_()
        except Exception as e:
            show_message("Error", f"Error while checking for updates: \n{e}")

    def initUI(self):
        self.setWindowTitle(f'BOIII Workshop Downloader {VERSION}-beta')
        self.setWindowIcon(QIcon('ryuk.ico'))
        self.setGeometry(100, 100, 400, 200)
        self.settings = QSettings("MyApp", "MyWindow")
        self.restore_geometry()

        layout = QVBoxLayout()

        browse_layout = QHBoxLayout()

        self.label_workshop_id = QLabel("Enter the Workshop ID or Link of the map/mod you want to download:")
        browse_layout.addWidget(self.label_workshop_id, 3)

        self.button_browse = QPushButton("Browse")
        self.button_browse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_browse.clicked.connect(self.open_browser)
        browse_layout.addWidget(self.button_browse, 1)

        layout.addLayout(browse_layout)

        info_workshop_layout = QHBoxLayout()

        self.edit_workshop_id = QLineEdit()
        self.edit_workshop_id.setPlaceholderText("Workshop ID/Link => Press info to see map/mod info")
        self.edit_workshop_id.textChanged.connect(self.reset_file_size)
        info_workshop_layout.addWidget(self.edit_workshop_id, 3)

        layout.addLayout(info_workshop_layout)
        self.info_button = QPushButton("Info")
        self.info_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.info_button.clicked.connect(self.show_map_info)
        info_workshop_layout.addWidget(self.info_button, 1)

        self.label_destination_folder = QLabel("Enter Your BOIII folder:")
        layout.addWidget(self.label_destination_folder, 3)

        Boiii_Input = QHBoxLayout()
        self.edit_destination_folder = QLineEdit()
        self.edit_destination_folder.setPlaceholderText("Your BOIII Instalation folder")
        Boiii_Input.addWidget(self.edit_destination_folder, 90)

        layout.addLayout(Boiii_Input)

        self.button_BOIII_browse = QPushButton("Select")
        self.button_BOIII_browse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_BOIII_browse.clicked.connect(self.open_BOIII_browser)
        Boiii_Input.addWidget(self.button_BOIII_browse, 10)

        self.label_steamcmd_path = QLabel("Enter SteamCMD path (default):")
        layout.addWidget(self.label_steamcmd_path)

        steamcmd_path = QHBoxLayout()
        self.edit_steamcmd_path = QLineEdit()
        steamcmd_path.addWidget(self.edit_steamcmd_path, 90)

        self.button_steamcmd_browse = QPushButton("Select")
        self.button_steamcmd_browse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_steamcmd_browse.clicked.connect(self.open_steamcmd_path_browser)
        steamcmd_path.addWidget(self.button_steamcmd_browse, 10)

        layout.addLayout(steamcmd_path)
        layout.addSpacing(10)

        buttons_layout = QHBoxLayout()

        self.button_download = QPushButton("Download")
        self.button_download.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_download.clicked.connect(self.download_map)
        buttons_layout.addWidget(self.button_download, 70)

        self.button_stop = QPushButton("Stop")
        self.button_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_stop.clicked.connect(self.stop_download)
        buttons_layout.addWidget(self.button_stop, 25)

        layout.addLayout(buttons_layout)

        InfoBar = QHBoxLayout()

        self.label_speed = QLabel("Network Speed: 0 KB/s")
        InfoBar.addWidget(self.label_speed, 3)

        self.label_file_size = QLabel("File size: 0KB")
        InfoBar.addWidget(self.label_file_size, 1)

        InfoWidget = QWidget()
        InfoWidget.setLayout(InfoBar)

        layout.addWidget(InfoWidget)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar, 75)

        spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addSpacerItem(spacer)

        check_for_update_layout = QHBoxLayout()
        check_update_button = QPushButton("Check for Updates")
        check_update_button.clicked.connect(self.check_for_updates)
        check_update_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        self.check_for_update_layout = QVBoxLayout()
        self.check_for_update_layout.addWidget(check_update_button)

        self.show_more_button = QPushButton("Launch boiii")
        self.show_more_button.clicked.connect(self.launch_boiii)

        check_for_update_layout = QHBoxLayout()
        check_for_update_layout.addWidget(check_update_button)

        self.check_for_updates_checkbox = QPushButton("Settings")
        self.check_for_updates_checkbox.clicked.connect(self.open_settings_dialog)


        check_for_update_layout = QHBoxLayout()
        check_for_update_layout.addWidget(check_update_button)
        check_for_update_layout.addWidget(self.check_for_updates_checkbox)
        check_for_update_layout.addWidget(self.show_more_button)

        layout.addLayout(check_for_update_layout)

        self.setLayout(layout)

        self.load_config()

        if config_check_for_updates() == "on":
            self.check_for_updates(ignore_up_todate=True)

        try:
            global console
            if config_console_state() == "on":
                console = True
                return 1
            else:
                console = False
                return 0
        except:
            pass

    def download_map(self):
        global stopped
        stopped = False
        self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())

        if not check_steamcmd():
            self.show_warning_message()
            return

        steamcmd_path = get_steamcmd_path()
        steamcmd_exe_path = os.path.join(steamcmd_path, "steamcmd.exe")
        steamcmd_size = os.path.getsize(steamcmd_exe_path)
        if steamcmd_size < 3 * 1024 * 1024:
            show_message("Warning", "SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.", icon=QMessageBox.Warning, exit_on_close=True)
            initialize_steam()
            return

        workshop_id = self.edit_workshop_id.text().strip()
        if not workshop_id.isdigit():
            try:
                if extract_workshop_id(workshop_id).strip().isdigit():
                    workshop_id = extract_workshop_id(workshop_id).strip()
                else:
                    QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
                    return
            except:
                QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
                return

        if not valid_id(workshop_id):
            QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
            return

        destination_folder = self.edit_destination_folder.text()
        steamcmd_path = self.edit_steamcmd_path.text()
        self.label_file_size.setText(f"File size: {get_workshop_file_size(workshop_id, raw=True)}")

        if not destination_folder:
            show_message("Error", "Please select a destination folder.")
            return

        if not steamcmd_path:
            show_message("Error", "Please enter the SteamCMD path.")
            return

        self.button_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.button_download.setEnabled(False)

        self.download_thread = DownloadThread(workshop_id, destination_folder, self.progress_bar, self.label_speed)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()

    def stop_download(self):
        global stopped
        stopped = True

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()

        self.button_download.setEnabled(True)
        self.button_stop.setEnabled(False)
        self.progress_bar.setValue(0)
        self.label_speed.setText(f"Network Speed: {0:.2f} KB/s")
        self.label_file_size.setText(f"File size: 0KB")

    def open_BOIII_browser(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Select BOIII Folder", "")
        if selected_folder:
            self.edit_destination_folder.setText(selected_folder)
            self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())

    def open_steamcmd_path_browser(self):
        selected_folder = QFileDialog.getExistingDirectory(self, "Select SteamCMD Folder", "")
        if selected_folder:
            self.edit_steamcmd_path.setText(selected_folder)
            self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())

    def on_download_finished(self):
        self.button_download.setEnabled(True)
        self.progress_bar.setValue(0)
        self.label_speed.setText(f"Network Speed: {0:.2f} KB/s")
        self.label_file_size.setText(f"File size: 0KB")
        self.button_stop.setEnabled(False)
        self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())

    def open_browser(self):
        link = "https://steamcommunity.com/app/311210/workshop/"
        webbrowser.open(link)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE_PATH):
            config.read(CONFIG_FILE_PATH)
            destination_folder = config.get("Settings", "DestinationFolder", fallback="")
            steamcmd_path = config.get("Settings", "SteamCMDPath", fallback=cwd())
            self.edit_destination_folder.setText(destination_folder)
            self.edit_steamcmd_path.setText(steamcmd_path)
        else:
            create_default_config()

    def save_config(self, destination_folder, steamcmd_path):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        config.set("Settings", "DestinationFolder", destination_folder)
        config.set("Settings", "SteamCMDPath", steamcmd_path)
        with open(CONFIG_FILE_PATH, "w") as config_file:
            config.write(config_file)

    def reset_file_size(self):
        self.label_file_size.setText(f"File size: 0KB")

    def show_map_info(self):
        workshop_id = self.edit_workshop_id.text().strip()

        if not workshop_id:
            QMessageBox.warning(self, "Warning", "Please enter a Workshop ID first.")
            return

        if not workshop_id.isdigit():
            try:
                if extract_workshop_id(workshop_id).strip().isdigit():
                    workshop_id = extract_workshop_id(workshop_id).strip()
                else:
                    QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
                    return
            except:
                QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
                return

        self.label_file_size.setText(f"File size: {get_workshop_file_size(workshop_id, raw=True)}")
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
                stars_div = soup.find("div", class_="fileRatingDetails")
                stars = stars_div.find("img")["src"]
            except:
                QMessageBox.warning(self, "Warning", "Please enter a valid Workshop ID.")
                return

            try:
                preview_image_element = soup.find("img", id="previewImage")
                workshop_item_image_url = preview_image_element["src"]
            except:
                preview_image_element = soup.find("img", id="previewImageMain")
                workshop_item_image_url = preview_image_element["src"]

            image_response = requests.get(workshop_item_image_url)
            image_response.raise_for_status()

            stars_response = requests.get(stars)
            stars_response.raise_for_status()

            pixmap = QPixmap()
            pixmap.loadFromData(image_response.content)

            pixmap_stars = QPixmap()
            pixmap_stars.loadFromData(stars_response.content)

            label = QLabel(self)
            label.setPixmap(pixmap)
            label.setAlignment(Qt.AlignCenter)

            label_stars = QLabel(self)
            label_stars.setPixmap(pixmap_stars)
            label_stars.setAlignment(Qt.AlignCenter)

            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Map/Mod Information")
            msg_box.setWindowIcon(QIcon('ryuk.ico'))
            msg_box.setIconPixmap(pixmap)
            msg_box.setText(f"Name: {map_name}\nType: {map_mod_type}\nSize: {map_size}")

            layout = QVBoxLayout()
            layout.addWidget(label)
            layout.addWidget(label_stars)
            msg_box.setLayout(layout)

            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDetailedText(f"Stars: {stars}\nLink: {url}")

            msg_box.exec_()

        except requests.exceptions.RequestException as e:
            show_message("Error", f"Failed to fetch map information.\nError: {e}")

    def launch_boiii(self):
        try:
            boiii_path = os.path.join(self.edit_destination_folder.text(), "boiii.exe")
            subprocess.Popen([boiii_path], cwd=self.edit_destination_folder.text())
        except Exception as e:
            show_message("Error: Failed to launch BOIII", f"Failed to launch boiii.exe\nMake sure to put in your correct boiii path\n{e}")

    def open_settings_dialog(self):
        settings_dialog = SettingsDialog()
        settings_dialog.exec_()

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def restore_geometry(self):
        geometry = self.settings.value("geometry", None)
        if geometry is not None:
            self.restoreGeometry(geometry)

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon('ryuk.ico'))
        self.setGeometry(50, 50, 250, 120)
        self.settings = QSettings("MyApp2", "MyWindow2")
        self.restore_geometry()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.check_updates_checkbox = QCheckBox("Check for updates on launch")
        self.check_updates_checkbox.setChecked(self.load_settings(updates=True))
        layout.addWidget(self.check_updates_checkbox)

        buttons_layout = QHBoxLayout()
        self.checkbox_show_console = QCheckBox("Console (On Download)", self)
        self.checkbox_show_console.setChecked(self.load_settings(console=True))
        tooltip_text = "<font color='black'>Toggle SteamCMD console\nPlease don't close the Console If you want to stop press the Stop boutton.</font>"
        self.checkbox_show_console.setToolTip(tooltip_text)

        buttons_layout.addWidget(self.checkbox_show_console, 5)

        layout.addLayout(buttons_layout)

        save_button = QPushButton("Save")
        save_button.setFixedWidth(60)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button, alignment=Qt.AlignLeft)

        self.setLayout(layout)

    def save_settings(self):
        global console
        if self.check_updates_checkbox.isChecked():
            config_check_for_updates(state="on")
        else:
            config_check_for_updates(state="off")

        if self.checkbox_show_console.isChecked():
            config_console_state(state="on")
            console = True
        else:
            config_console_state(state="off")
            console = False

        self.accept()

    def load_settings(self, console=None, updates=None):
        if updates:
            if config_check_for_updates() == "on":
                return 1
            else:
                return 0
        if console:
            if config_console_state() == "on":
                console = True
                return 1
            else:
                console = False
                return 0

    def closeEvent(self, event):
        self.settings.setValue("geometry", self.saveGeometry())
        super().closeEvent(event)

    def restore_geometry(self):
        geometry = self.settings.value("geometry", None)
        if geometry is not None:
            self.restoreGeometry(geometry)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    if not os.path.exists(CONFIG_FILE_PATH):
        create_default_config()

    window = WorkshopDownloaderApp()
    window.show()

    sys.exit(app.exec_())
