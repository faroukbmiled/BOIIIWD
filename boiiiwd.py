import os
import sys
import subprocess
import configparser
import filecmp
import json
import requests
import time
import threading
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QHBoxLayout, QProgressBar, QSizePolicy
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtGui import QIcon
import webbrowser
import qdarktheme

CONFIG_FILE_PATH = "config.ini"
global stopped
stopped = False

def create_default_config():
    config = configparser.ConfigParser()
    config["Settings"] = {
        "SteamCMDPath": "steamcmd",
        "DestinationFolder": ""
    }
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def run_steamcmd_command(command):
    steamcmd_path = get_steamcmd_path()
    process = subprocess.Popen([steamcmd_path] + command.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

    while True:
        output = process.stdout.readline().rstrip()
        if process.poll() is not None:
            break

def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback="steamcmd")

def set_steamcmd_path(steamcmd_path):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    config.set("Settings", "SteamCMDPath", steamcmd_path)
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def extract_json_data(json_path):
    with open(json_path, "r") as json_file:
        data = json.load(json_file)
    return data["Type"], data["FolderName"]

def get_file_size(url):
    response = requests.head(url)
    if "Content-Length" in response.headers:
        file_size = int(response.headers["Content-Length"])
        return file_size
    return None

def get_workshop_file_size(workshop_id):
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&searchtext="
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    file_size_element = soup.find("div", class_="detailsStatRight")
    if file_size_element:
        file_size_text = file_size_element.get_text(strip=True)
        file_size_text = file_size_text.replace(",", "")
        file_size_in_mb = float(file_size_text.replace(" MB", ""))
        file_size_in_bytes = int(file_size_in_mb * 1024 * 1024)
        return file_size_in_bytes
    return None

def update_progress_bar(current_size, file_size, progress_bar):
    if file_size is not None:
        progress = int(current_size / file_size * 100)
        progress_bar.setValue(progress)

def check_and_update_progress(file_size, folder_name_path, progress_bar):
    while not stopped:
        current_size = sum(os.path.getsize(os.path.join(folder_name_path, f)) for f in os.listdir(folder_name_path))
        update_progress_bar(current_size, file_size, progress_bar)
        QCoreApplication.processEvents()
        time.sleep(1)

def download_workshop_map(workshop_id, destination_folder, progress_bar):
    file_size = get_workshop_file_size(workshop_id)
    if file_size is None:
        show_message("Error", "Failed to retrieve file size.")
        return

    download_folder = os.path.join("steamapps", "workshop", "downloads", "311210", workshop_id)
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    command = f"+login anonymous +workshop_download_item 311210 {workshop_id} +quit"
    progress_thread = threading.Thread(target=check_and_update_progress, args=(file_size, download_folder, progress_bar))
    progress_thread.daemon = True
    progress_thread.start()

    run_steamcmd_command(command)

    global stopped
    stopped = True
    progress_bar.setValue(100)

    map_folder = os.path.join("steamapps", "workshop", "content", "311210", workshop_id)

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
        map_files = os.listdir(map_folder)

        for map_file in map_files:
            source_path = os.path.join(map_folder, map_file)
            destination_path = os.path.join(folder_name_path, map_file)

            if os.path.exists(destination_path) and filecmp.cmp(source_path, destination_path):
                pass
            else:
                os.replace(source_path, destination_path)
                QCoreApplication.processEvents()

        show_message("Download Complete", f"{mod_type} files are downloaded at {folder_name_path}")

def show_message(title, message):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()

class DownloadThread(QThread):
    finished = pyqtSignal()

    def __init__(self, workshop_id, destination_folder, progress_bar):
        super().__init__()
        self.workshop_id = workshop_id
        self.destination_folder = destination_folder
        self.progress_bar = progress_bar

    def run(self):
        download_workshop_map(self.workshop_id, self.destination_folder, self.progress_bar)
        self.finished.emit()

class WorkshopDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.download_thread = None
        self.button_download.setEnabled(True)
        self.button_stop.setEnabled(False)

    def initUI(self):
        self.setWindowTitle('BOIII Workshop Downloader')
        self.setWindowIcon(QIcon('ryuk.ico'))
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        browse_layout = QHBoxLayout()

        self.label_workshop_id = QLabel("Enter the Workshop ID of the map/mod you want to download:")
        browse_layout.addWidget(self.label_workshop_id, 3)

        self.button_browse = QPushButton("Browse")
        self.button_browse.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_browse.clicked.connect(self.open_browser)
        browse_layout.addWidget(self.button_browse, 1)

        layout.addLayout(browse_layout)

        self.edit_workshop_id = QLineEdit()
        layout.addWidget(self.edit_workshop_id)

        self.label_destination_folder = QLabel("Enter Your BOIII folder:")
        layout.addWidget(self.label_destination_folder)

        self.edit_destination_folder = QLineEdit()
        layout.addWidget(self.edit_destination_folder)

        self.label_steamcmd_path = QLabel("Enter SteamCMD path (default):")
        layout.addWidget(self.label_steamcmd_path)

        self.edit_steamcmd_path = QLineEdit()
        layout.addWidget(self.edit_steamcmd_path)

        buttons_layout = QHBoxLayout()

        self.button_download = QPushButton("Download")
        self.button_download.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_download.clicked.connect(self.download_map)
        buttons_layout.addWidget(self.button_download, 75)

        self.button_stop = QPushButton("Stop")
        self.button_stop.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_stop.clicked.connect(self.stop_download)
        buttons_layout.addWidget(self.button_stop, 25)

        layout.addLayout(buttons_layout)

        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.setLayout(layout)

        self.load_config()

    def download_map(self):
        global stopped
        stopped = False

        workshop_id = self.edit_workshop_id.text()
        destination_folder = self.edit_destination_folder.text()
        steamcmd_path = self.edit_steamcmd_path.text()

        if not destination_folder:
            show_message("Error", "Please select a destination folder.")
            return

        if not steamcmd_path:
            show_message("Error", "Please enter the SteamCMD path.")
            return

        self.button_stop.setEnabled(True)
        self.progress_bar.setValue(0)
        self.button_download.setEnabled(False)

        self.download_thread = DownloadThread(workshop_id, destination_folder, self.progress_bar)
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

    def on_download_finished(self):
        self.button_download.setEnabled(True)
        self.save_config(self.edit_destination_folder.text(), self.edit_steamcmd_path.text())

    def open_browser(self):
        link = "https://steamcommunity.com/app/311210/workshop/"
        webbrowser.open(link)

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE_PATH):
            config.read(CONFIG_FILE_PATH)
            destination_folder = config.get("Settings", "DestinationFolder", fallback="")
            steamcmd_path = config.get("Settings", "SteamCMDPath", fallback="")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    qdarktheme.setup_theme()

    if not os.path.exists(CONFIG_FILE_PATH):
        create_default_config()

    window = WorkshopDownloaderApp()
    window.show()

    sys.exit(app.exec_())
