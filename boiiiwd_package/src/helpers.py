import src.shared_vars as main_app
from src.imports import *

# Start helper functions
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
    if os.path.exists(os.path.join(application_path, theme_name)):
        return os.path.join(application_path, theme_name)
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

def is_internet_available():
    try:
        requests.get("https://www.google.com", timeout=3)
        return True
    except:
        return False

def check_for_updates_func(window, ignore_up_todate=False):
    if not is_internet_available():
        show_message("Error!", "Internet connection is not available. Please check your internet connection and try again.")
        return
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
                from src.update_window import UpdateWindow
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
        "SteamCMDPath": application_path,
        "DestinationFolder": "",
        "checkforupdtes": "on",
        "console": "off"
    }
    with open(CONFIG_FILE_PATH, "w") as config_file:
        config.write(config_file)

def get_steamcmd_path():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    return config.get("Settings", "SteamCMDPath", fallback=application_path)

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
        main_app.app.after(0, callback)

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

    directories_to_reset = ["steamapps", "dumps", "logs", "depotcache", "appcache","userdata",]

    for directory in directories_to_reset:
        directory_path = os.path.join(steamcmd_path, directory)
        if os.path.exists(directory_path):
            remove_tree(directory_path, show_error=True)

    for root, _, files in os.walk(steamcmd_path):
        for filename in files:
            if filename.endswith((".old", ".crash")):
                file_path = os.path.join(root, filename)
                os.remove(file_path)

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
    ctk_tooltip.CTkToolTip(widget, message=message, is_noti=True, noti_event=event, noti_dur=noti_dur, topmost=topmost)

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
