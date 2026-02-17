import src.shared_vars as main_app
from src.imports import *


# Clean environment for spawning external processes
# Removes PyInstaller's bundled library paths to prevent SSL conflicts on Arch-based systems
_CLEAN_ENV = None

def _get_clean_env():
    global _CLEAN_ENV
    if _CLEAN_ENV is None:
        _CLEAN_ENV = os.environ.copy()
        _CLEAN_ENV.pop('LD_LIBRARY_PATH', None)
        _CLEAN_ENV.pop('LD_PRELOAD', None)
    return _CLEAN_ENV


def open_external(args, **kwargs):
    """Spawn external process with clean environment (no PyInstaller library paths)."""
    kwargs.setdefault('env', _get_clean_env())
    kwargs.setdefault('start_new_session', True)
    kwargs.setdefault('stdout', subprocess.DEVNULL)
    kwargs.setdefault('stderr', subprocess.DEVNULL)
    return subprocess.Popen(args, **kwargs)


def safe_open_url(url):
    """Open URL in system browser."""
    try:
        open_external(['xdg-open', url])
    except Exception:
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"[{get_current_datetime()}] Failed to open URL: {e}")


def check_config(name, fallback=None):
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        if fallback:
            return config.get("Settings", name, fallback=fallback)
        return config.get("Settings", name, fallback="")
    except Exception:
        return fallback if fallback else ""


def save_config(name, value):
    """Save a setting to the config file, preserving existing settings."""
    config = configparser.ConfigParser()

    # Try to read existing config
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            config.read(CONFIG_FILE_PATH)
        except Exception as e:
            print(f"[{get_current_datetime()}] Warning: Could not read config, preserving what we can: {e}")
            # Try to manually preserve sections
            try:
                with open(CONFIG_FILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                # If file exists but couldn't be parsed, backup and start fresh
                backup_path = CONFIG_FILE_PATH + '.backup'
                with open(backup_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.write(content)
                print(f"[{get_current_datetime()}] Backed up corrupted config to {backup_path}")
            except:
                pass

    if not config.has_section("Settings"):
        config.add_section("Settings")

    if name and value:
        config.set("Settings", name, value)

    try:
        os.makedirs(os.path.dirname(CONFIG_FILE_PATH), exist_ok=True)
        with open(CONFIG_FILE_PATH, "w", encoding='utf-8', errors="ignore") as config_file:
            config.write(config_file)
    except Exception as e:
        print(f"[{get_current_datetime()}] Error saving config: {e}")


def check_custom_theme(theme_name):
    if os.path.exists(os.path.join(APPLICATION_PATH, theme_name)):
        return os.path.join(APPLICATION_PATH, theme_name)
    else:
        try:
            return os.path.join(RESOURCES_DIR, theme_name)
        except:
            return os.path.join(RESOURCES_DIR, "boiiiwd_theme.json")


# theme initialization
# Modes: "System" (standard), "Dark", "Light"
ctk.set_appearance_mode(check_config("appearance", "Dark"))
try:
    ctk.set_default_color_theme(check_custom_theme(
        check_config("theme", fallback="boiiiwd_theme.json")))
except:
    save_config("theme", "boiiiwd_theme.json")
    ctk.set_default_color_theme(os.path.join(
        RESOURCES_DIR, "boiiiwd_theme.json"))


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
    """Create Linux update script."""
    script_content = f"""#!/bin/bash
echo "Terminating BOIIIWD..."
pkill -f "{program_name}" || true

echo "Replacing BOIIIWD..."
cd "{updater_folder}"
mv -f "{new_exe}" "../{program_name}"
chmod +x "../{program_name}"

echo "Starting BOIIIWD..."
cd ..
./{program_name} &

echo "Exiting!"
exit 0
"""
    script_path = os.path.join(updater_folder, "boiiiwd_updater.sh")

    with open(script_path, "w", encoding='utf-8', errors="ignore") as script_file:
        script_file.write(script_content)

    os.chmod(script_path, 0o755)
    return script_path


def if_internet_available(func=None, launching=False):
    def check_internet():
        endpoints = [
            ("1.1.1.1", 53),        # Cloudflare DNS
            ("8.8.8.8", 53),        # Google DNS
            ("9.9.9.9", 53),        # Quad9 DNS
            ("208.67.222.222", 53), # OpenDNS
        ]
        for host, port in endpoints:
            try:
                socket.create_connection((host, port), timeout=2)
                return True
            except:
                continue
        # Fallback: try HTTP request
        try:
            requests.head("https://steamcommunity.com", timeout=3)
            return True
        except:
            pass
        return False

    if func == "return":
        return check_internet()

    def wrapper(*args, **kwargs):
        if check_internet():
            return func(*args, **kwargs)
        else:
            if not launching:
                show_message(
                    "Offline", "No internet connection. Please check your internet connection and try again.")
            return

    return wrapper



def parse_version(version_str):
    """Parse version string to integer, handling suffixes like -linux."""
    # Remove v prefix and any suffix like -linux
    clean = version_str.replace("v", "").split("-")[0].replace(".", "")
    return int(clean)

@if_internet_available
def check_for_updates_func(window, ignore_up_todate=False):
    print(f'[{get_current_datetime()}] [Logs] check_for_updates_func invoked...')
    try:
        latest_version = get_latest_release_version()
        current_version = VERSION
        int_latest_version = parse_version(latest_version)
        int_current_version = parse_version(current_version)

        if latest_version and int_latest_version > int_current_version:
            msg_box = CTkMessagebox(master=main_app.app, title="Update Available", message=f"An update is available! Install now?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}",
                                    option_1="View", option_2="No", option_3="Yes", fade_in_duration=int(1), sound=True,
                                    button_width=70, button_height=28)

            result = msg_box.get()

            if result == "View":
                safe_open_url(
                    f"https://github.com/{GITHUB_REPO}/releases/latest")

            if result == "Yes":
                from src.update_window import UpdateWindow
                update_window = UpdateWindow(window, LATEST_RELEASE_URL)
                update_window.start_update()

            if result == "No":
                return

        elif int_latest_version < int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(master=main_app.app, title="Up to Date!", message=f"Unreleased version!\nCurrent Version: {current_version}\nLatest Version: {latest_version}",
                                    option_1="Ok", sound=True, button_width=80, button_height=28)
            result = msg_box.get()
        elif int_latest_version == int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(master=main_app.app, title="Up to Date!", message="No Updates Available!",
                                    option_1="Ok", sound=True, button_width=80, button_height=28)
            result = msg_box.get()

        else:
            show_message(
                "Error!", "An error occured while checking for updates!\nCheck your internet and try again")

    except Exception as e:
        print(f"[{get_current_datetime()}] [logs] error in check_for_updates_func: {e}")
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
    steamcmd_exe_path = os.path.join(steamcmd_path, STEAMCMD_EXE)

    if not os.path.exists(steamcmd_exe_path):
        return False

    return True


def initialize_steam(master):
    print(f'[{get_current_datetime()}] [Logs] initialize_steam invoked...')
    try:
        steamcmd_path = get_steamcmd_path()
        steamcmd_exe_path = os.path.join(steamcmd_path, STEAMCMD_EXE)
        process = subprocess.Popen([steamcmd_exe_path, "+quit"])
        master.attributes('-alpha', 0.0)
        process.wait()
        if is_steamcmd_initialized():
            show_message("SteamCMD has terminated!",
                         "BOIIIWD is ready for action.", icon="info")
        else:
            show_message("SteamCMD has terminated!!",
                         "SteamCMD isn't initialized yet")
    except:
        show_message(
            "Error!", "An error occurred please check your paths and try again.", icon="cancel")
    master.attributes('-alpha', 1.0)


@if_internet_available
def valid_id(workshop_id):
    data = item_steam_api(workshop_id)
    if check_config("skip_invalid", "on") == "off":
        if data:
            return True
    if "consumer_app_id" in data['response']['publishedfiledetails'][0]:
        return True
    else:
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
        "SteamCMDPath": STEAMCMD_DIR,
        "DestinationFolder": "",
        "checkforupdates": "on",
        "console": "off"
    }
    with open(CONFIG_FILE_PATH, "w", encoding='utf-8', errors="ignore") as config_file:
        config.write(config_file)


def get_steamcmd_path():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_PATH)
        return config.get("Settings", "SteamCMDPath", fallback=STEAMCMD_DIR)
    except Exception:
        return STEAMCMD_DIR


def get_steam_base_path():
    """Get the base Steam path where SteamCMD stores data on Linux."""
    return os.path.join(os.path.expanduser("~"), "Steam")


def get_steam_workshop_path():
    """Get the path where SteamCMD downloads workshop content on Linux.
    On Linux, SteamCMD uses ~/Steam regardless of where steamcmd.sh is installed."""
    return os.path.join(get_steam_base_path(), "steamapps", "workshop", "content", "311210")


def get_workshop_folder(workshop_id):
    """Get the full path to a workshop item's folder."""
    return os.path.join(get_steam_workshop_path(), workshop_id)


def get_workshop_downloads_folder(workshop_id):
    """Get the path where SteamCMD temporarily downloads workshop items."""
    return os.path.join(get_steam_base_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)


def extract_json_data(json_path, key):
    with open(json_path, 'r', encoding='utf-8', errors="ignore") as json_file:
        data = json.load(json_file)
        return data.get(key, '')


def extract_json_data_bulk(json_path, keys):
    """Extract multiple keys from JSON file in one read - more efficient for multiple fields."""
    try:
        with open(json_path, 'r', encoding='utf-8', errors="ignore") as json_file:
            data = json.load(json_file)
            return {key: data.get(key, '') for key in keys}
    except:
        return {key: '' for key in keys}


def convert_bytes_to_readable(size_in_bytes, no_symb=None):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_in_bytes < 1024.0:
            if no_symb:
                return f"{size_in_bytes:.2f}"
            return f"{size_in_bytes:.2f} {unit}"
        size_in_bytes /= 1024.0


def get_workshop_file_size(workshop_id, raw=None):
    print(f'[{get_current_datetime()}] [Logs] get_workshop_file_size invoked...')
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}&searchtext="
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    file_size_element = soup.find("div", class_="detailsStatRight")

    if not file_size_element:
        return None

    file_size_text = file_size_element.get_text(strip=True).replace(",", "")

    try:
        if "GB" in file_size_text:
            file_size_in_gb = float(file_size_text.replace(" GB", ""))
            file_size_in_bytes = int(file_size_in_gb * 1024 * 1024 * 1024)
        elif "MB" in file_size_text:
            file_size_in_mb = float(file_size_text.replace(" MB", ""))
            file_size_in_bytes = int(file_size_in_mb * 1024 * 1024)
        elif "KB" in file_size_text:
            file_size_in_kb = float(file_size_text.replace(" KB", ""))
            file_size_in_bytes = int(file_size_in_kb * 1024)
        elif "B" in file_size_text:
            file_size_in_b = float(file_size_text.replace(" B", ""))
            file_size_in_bytes = int(file_size_in_b)
        else:
            raise ValueError(f"Unsupported file size format: {file_size_text}")

        if raw:
            return convert_bytes_to_readable(file_size_in_bytes)
        return file_size_in_bytes

    except Exception as e:
        print(f"[{get_current_datetime()}] [logs] error in get_workshop_file_size: {e}")
        return None


def show_message(title, message, icon="warning", _return=False, option_1="No", option_2="Ok"):
    if _return:
        msg = CTkMessagebox(master=main_app.app, title=title, message=message, icon=icon,
                            option_1=option_1, option_2=option_2, sound=True,
                            button_width=80, button_height=28)
        response = msg.get()
        if response == option_1:
            return False
        elif response == option_2:
            return True
        else:
            return False
    else:
        def callback():
            CTkMessagebox(master=main_app.app, title=title, message=message, icon=icon, sound=True,
                          button_width=80, button_height=28)
        main_app.app.after(0, callback)


def input_popup(title="Input", message="Enter value:"):
    try:
        dialog = ctk.CTkInputDialog(text=message, title=title)
        return dialog.get_input()
    except Exception as e:
        print(f"[{get_current_datetime()}] [logs] error in input_popup: {e}")

def launch_game_func(path, procname=None, flags=""):
    """Launch the game. Uses platform-appropriate executable name."""
    if procname is None:
        procname = GAME_EXE

    print(f'[{get_current_datetime()}] [Logs] launch_game_func invoked...')

    try:
        # Kill existing process
        for proc in psutil.process_iter():
            try:
                if proc.name() == procname or procname in proc.name():
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

        game_path = os.path.join(path, procname)
        subprocess.Popen([game_path, flags], cwd=path)
        show_message(
            "Please wait!", "The game has launched in the background it will open up in a sec!", icon="info")
    except Exception as e:
        print(f"[{get_current_datetime()}] [logs] error in launch_game_func: {e}")
        show_message(f"Error: Failed to launch game", f"Failed to start {procname}\n\nMake sure the game path is correct.\n\n{e}")


def remove_tree(folder_path, show_error=None):
    if show_error:
        try:
            shutil.rmtree(folder_path)
        except Exception as e:
            print(f"[{get_current_datetime()}] [logs] error in remove_tree: {e}")
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
    """Calculate folder size for real-time accuracy."""
    total_size = 0
    try:
        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    # Read file to get accurate size (handles caching)
                    with open(filepath, 'rb') as f:
                        f.seek(0, 2)  # Seek to end
                        total_size += f.tell()
                except (OSError, PermissionError, IOError):
                    # try stat as fallback
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        pass
    except (OSError, PermissionError):
        pass
    return total_size


def is_steamcmd_initialized():
    steamcmd_path = get_steamcmd_path()
    steamcmd_exe_path = os.path.join(steamcmd_path, STEAMCMD_EXE)
    try:
        # Check if steamcmd.sh exists and linux32/steamcmd binary exists
        if not os.path.exists(steamcmd_exe_path):
            return False
        linux32_bin = os.path.join(steamcmd_path, "linux32", "steamcmd")
        if os.path.exists(linux32_bin):
            return True
        return False
    except OSError:
        return False


def get_button_state_colors(file_path, state):
    try:
        with open(file_path, 'r', encoding='utf-8', errors="ignore") as json_file:
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
    """Reset SteamCMD data. On Linux, data is stored in ~/Steam/, not the steamcmd installation folder."""
    print(f'[{get_current_datetime()}] [Logs] reset_steamcmd invoked...')

    # On Linux, SteamCMD stores data in ~/Steam/ regardless of where steamcmd.sh is installed
    steam_base = get_steam_base_path()
    steamcmd_path = get_steamcmd_path()

    directories_to_reset = ["steamapps", "dumps", "logs", "depotcache", "appcache", "userdata"]

    # Clean ~/Steam/ directories (where actual data is stored on Linux)
    cleaned_something = False
    for directory in directories_to_reset:
        directory_path = os.path.join(steam_base, directory)
        if os.path.exists(directory_path):
            print(f'[{get_current_datetime()}] [Logs] Cleaning: {directory_path}')
            remove_tree(directory_path, show_error=True)
            cleaned_something = True

    # Also clean .old and .crash files from ~/Steam/
    if os.path.exists(steam_base):
        for root, _, files in os.walk(steam_base):
            for filename in files:
                if filename.endswith((".old", ".crash")):
                    file_path = os.path.join(root, filename)
                    try:
                        os.remove(file_path)
                        print(f'[{get_current_datetime()}] [Logs] Removed: {file_path}')
                    except Exception as e:
                        print(f'[{get_current_datetime()}] [Logs] Could not remove {file_path}: {e}')

    # Also clean steamcmd installation folder cache if different from steam_base
    if steamcmd_path != steam_base:
        for directory in ["appcache", "depotcache"]:
            directory_path = os.path.join(steamcmd_path, directory)
            if os.path.exists(directory_path):
                print(f'[{get_current_datetime()}] [Logs] Cleaning steamcmd cache: {directory_path}')
                remove_tree(directory_path, show_error=True)
                cleaned_something = True

    if not no_warn:
        if cleaned_something:
            show_message("Success!", "SteamCMD data has been reset successfully!", icon="info")
        else:
            show_message("Info", "No SteamCMD data found to clean.", icon="info")


def get_item_name(id):
    try:
        data = item_steam_api(id)
        try:
            name = data['response']['publishedfiledetails'][0]['title']
            return name
        except:
            return True
    except:
        return False

# you gotta use my modded CTkToolTip originaly by Akascape


def show_noti(widget, message, event=None, noti_dur=3.0, topmost=False):
    CTkToolTip(widget, message=message, is_noti=True,
               noti_event=event, noti_dur=noti_dur, topmost=topmost)


def get_update_time_from_html(workshop_id):
    current_year = datetime.now().year
    date_format_with_year = "%d %b, %Y @ %I:%M%p"
    date_format_with_added_year = "%d %b @ %I:%M%p, %Y"
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        soup = BeautifulSoup(content, "html.parser")

        details_stats_container = soup.find(
            "div", class_="detailsStatsContainerRight")
        if details_stats_container:
            details_stat_elements = details_stats_container.find_all(
                "div", class_="detailsStatRight")
        try:
            date_updated = details_stat_elements[2].text.strip()
        except:
            date_updated = None

        if not date_updated:
            return None

        try:
            date_updated = datetime.strptime(
                date_updated, date_format_with_year)
        except ValueError:
            date_updated = datetime.strptime(
                date_updated + f", {current_year}", date_format_with_added_year)

        return int(date_updated.timestamp())

    except Exception as e:
        print(f"Error getting update time for URL {url}: {e}")
        return None


def check_item_date(down_date, date_updated, format=False):
    current_year = datetime.now().year
    date_format_with_year = "%d %b, %Y @ %I:%M%p"
    date_format_with_added_year = "%d %b @ %I:%M%p, %Y"
    try:
        try:
            download_datetime = datetime.strptime(
                down_date, date_format_with_year)
        except ValueError:
            download_datetime = datetime.strptime(
                down_date + f", {current_year}", date_format_with_added_year)

        if format:
            try:
                date_updated = datetime.strptime(
                    date_updated, date_format_with_year)
            except ValueError:
                date_updated = datetime.strptime(
                    date_updated + f", {current_year}", date_format_with_added_year)

        if date_updated >= download_datetime:
            return True
        elif date_updated < download_datetime:
            return False
    except:
        return False


def get_window_size_from_registry():
    """Get window geometry from separate geometry file."""
    # Default values if geometry not saved yet
    default_width, default_height, default_x, default_y = 900, 560, 100, 100
    geometry_file = os.path.join(os.path.dirname(CONFIG_FILE_PATH), "geometry.ini")
    try:
        config = configparser.ConfigParser()
        config.read(geometry_file)
        if config.has_section("Window"):
            width = config.get("Window", "width", fallback=None)
            height = config.get("Window", "height", fallback=None)
            x = config.get("Window", "x", fallback=None)
            y = config.get("Window", "y", fallback=None)
            if all([width, height, x, y]):
                return int(width), int(height), int(x), int(y)
        return default_width, default_height, default_x, default_y
    except Exception:
        return default_width, default_height, default_x, default_y


def save_window_size_to_registry(width, height, x, y):
    """Save window geometry to a separate geometry file (not the main config)."""
    # Use a separate file for geometry to avoid conflicts with settings
    geometry_file = os.path.join(os.path.dirname(CONFIG_FILE_PATH), "geometry.ini")

    config = configparser.ConfigParser()
    try:
        if not config.has_section("Window"):
            config.add_section("Window")
        config.set("Window", "width", str(width))
        config.set("Window", "height", str(height))
        config.set("Window", "x", str(x))
        config.set("Window", "y", str(y))

        os.makedirs(os.path.dirname(geometry_file), exist_ok=True)
        with open(geometry_file, "w", encoding='utf-8', errors="ignore") as f:
            config.write(f)
    except Exception as e:
        print(f"[{get_current_datetime()}] Error saving window geometry: {e}")


def item_steam_api(id):
    try:
        url = ITEM_INFO_API
        data = {
            "itemcount": 1,
            "publishedfileids[0]": int(id),
        }
        info = requests.post(url, data=data)
        return info.json()

    except Exception as e:
        print(e)
        return False


def get_item_dates(ids):
    try:
        data = {
            "itemcount": len(ids),
        }
        for i, id in enumerate(ids):
            data[f"publishedfileids[{i}]"] = int(id)

        info = requests.post(ITEM_INFO_API, data=data)
        response_data = info.json()

        if "response" in response_data:
            item_details = response_data["response"]["publishedfiledetails"]
            return_list = {item["publishedfileid"]: item.get(
                "time_updated", None) for item in item_details}
            return return_list

        return {}

    except Exception as e:
        print("Error: could not fetch all update times. Breaking early.")
        return {}


def isNullOrWhiteSpace(str):
    if (str is None) or (str == "") or (str.isspace()):
        return True
    return False


def concatenate_sublists(a):
    out = []
    for sublist in a:
        out.extend(sublist)
    return out


def nextnonexistentdir(f, dir=os.path.dirname(os.path.realpath(__file__))):
    i = 0

    def already_exists(i):
        if i==0 and os.path.exists(os.path.join(dir, (f).strip())):
            return True
        else:
            return os.path.exists(os.path.join(dir, (f + f'_{str(i)}').strip()))

    while already_exists(i):
        i += 1

    root_i_ext = [f, i]

    return root_i_ext


def xor_encrypt_decrypt(data, key):
    key_len = len(key)
    result = bytearray()

    for i in range(len(data)):
        result.append(data[i] ^ key[i % key_len])

    return bytes(result)


def obfuscate(data):
    try:
        data_bytes = data.encode('utf-8')
        encrypted_data = xor_encrypt_decrypt(data_bytes, BOIIIWD_ENC_KEY)
        return base64.b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        print(f"Encryption error: {e}")
        return ""


def unobfuscate(data):
    try:
        encrypted_data = base64.b64decode(data)
        decrypted_data = xor_encrypt_decrypt(encrypted_data, BOIIIWD_ENC_KEY)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""


def save_steam_creds(steam_username):
    save_config("13ead2e5e894dd32839df1d494056f7c", obfuscate(steam_username))


def load_steam_creds():
    user = unobfuscate(check_config("13ead2e5e894dd32839df1d494056f7c", ""))
    return user


def invalid_password_check(stdout_text: str) -> str | bool:
    if stdout_text:
        try:
            return_error_messages = [
                "FAILED (Invalid Password)", # 0
                "FAILED (Rate Limit Exceeded)", # 1
                "FAILED (Two-factor code mismatch)", # 2
                "FAILED (Invalid Login Auth Code)", # 3
                "Invalid Password", # 4
                "FAILED", # 5,
                "password:", # 6
                "Two-factor code:" #7
            ]

            for message in return_error_messages:
                if message in stdout_text:
                    save_config("login_cached", "off")
                    if message == (return_error_messages[6] or return_error_messages[7]):
                        return message + " - Password prompt detected, Cashed login is now off, try again!"
                    elif message == return_error_messages[1]:
                        return message + " - Rate limit exceeded, try again later!"
                    return message + " - Cashed login is now off, try again!"

            return False

        except Exception as e:
            print(f"Error in invalid_password_check: {e}")
            return False
    else:
        return False


def check_download_failed(stdout_text: str) -> bool:
    """Check if steamcmd output indicates download failure."""
    if stdout_text:
        if "ERROR!" in stdout_text and "Download item" in stdout_text and "failed" in stdout_text:
            return True
    return False


# will be reworked in the future
def initiate_login_process(command, console):
    print(f'[{get_current_datetime()}] [Logs] initiate_login_process invoked...')
    try:
        path = command.split('+login')[0].strip()
        username = command.split("+login")[1].strip().split(" ")[0]
        print(f"[{get_current_datetime()}] [Logs] Initializing login process for {username}...")

        # Linux: run in a new terminal window or directly
        terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']
        terminal_found = None
        for term in terminals:
            if shutil.which(term):
                terminal_found = term
                break

        if terminal_found:
            if terminal_found == 'gnome-terminal':
                subprocess.run([terminal_found, '--', path, '+login', username])
            elif terminal_found == 'konsole':
                subprocess.run([terminal_found, '-e', path, '+login', username])
            else:
                subprocess.run([terminal_found, '-e', f'{path} +login {username}'])
        else:
            # Fallback: run directly
            subprocess.run([path, '+login', username])

        save_config("login_cached", "on")
        return True
    except Exception as e:
        print(f"Error running command in new window: {e}")
        return False


def get_log_file_path():
    """Get the path to the application log file."""
    return os.path.join(CONFIG_DIR, "boiiiwd.log")

def open_log_file():
    """Open the log file in the default text editor."""
    log_file = get_log_file_path()

    # Create log file if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write(f"[{get_current_datetime()}] BOIIIWD Log File\n")
            f.write("Run BOIIIWD from terminal to see live output.\n")

    # Try multiple methods to open the file
    openers = [
        ['xdg-open'],           # Standard Linux
        ['wslview'],            # WSL with wslu installed
        ['sensible-editor'],    # Debian/Ubuntu fallback
        ['gedit'],              # GNOME
        ['kate'],               # KDE
        ['xed'],                # Linux Mint
        ['nano'],               # Terminal fallback (in xterm)
    ]

    for opener in openers:
        try:
            if opener[0] == 'nano':
                # Open nano in a terminal
                terminals = ['gnome-terminal', 'konsole', 'xfce4-terminal', 'xterm']
                for term in terminals:
                    if shutil.which(term):
                        if term == 'gnome-terminal':
                            open_external([term, '--', 'nano', log_file])
                        else:
                            open_external([term, '-e', f'nano {log_file}'])
                        print(f"[{get_current_datetime()}] Opened log file with {term} + nano")
                        return
            elif shutil.which(opener[0]):
                open_external(opener + [log_file])
                print(f"[{get_current_datetime()}] Opened log file with {opener[0]}")
                return
        except Exception:
            continue

    # Last resort: print the path
    print(f"[{get_current_datetime()}] Could not open log file automatically.")
    print(f"[{get_current_datetime()}] Log file location: {log_file}")
    show_message("Log File", f"Could not open automatically.\n\nLog file location:\n{log_file}", icon="info")

def show_console():
    """No-op on Linux - use open_log_file() instead."""
    pass

def hide_console():
    """No-op on Linux."""
    pass


def get_current_datetime():
    try:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"[Logs] Error in get_current_datetime: {e}")
        return ""

def kill_steamcmd():
    """Kill any running SteamCMD processes."""
    try:
        subprocess.run(['pkill', '-f', 'steamcmd'], capture_output=True)
    except Exception as e:
        print(f'[{get_current_datetime()}] [Logs] Error in kill_steamcmd: {e}')


def cleanup_steamcmd_data(workshop_id, delete_content=False):
    """Clean up SteamCMD temporary data after download.

    Args:
        workshop_id: The workshop item ID
        delete_content: If True, also delete the downloaded content folder (for failed downloads)
    """
    print(f'[{get_current_datetime()}] [Logs] cleanup_steamcmd_data invoked for {workshop_id}, delete_content={delete_content}')
    steam_base = get_steam_base_path()
    steamapps_path = os.path.join(steam_base, "steamapps")

    # Clean patch files
    try:
        if os.path.exists(steamapps_path):
            for filename in os.listdir(steamapps_path):
                if filename.startswith("state_311210_") and filename.endswith(".patch") and workshop_id in filename:
                    try:
                        file_path = os.path.join(steamapps_path, filename)
                        os.remove(file_path)
                        print(f'[{get_current_datetime()}] [Logs] Removed patch file: {file_path}')
                    except Exception as e:
                        print(f'[{get_current_datetime()}] [Logs] Could not remove patch file: {e}')
    except Exception as e:
        print(f'[{get_current_datetime()}] [Logs] Error cleaning patch files: {e}')

    # Clean manifest (this can cause issues with re-downloads, so only remove for specific item)
    # acf_file = os.path.join(steamapps_path, "workshop", "appworkshop_311210.acf")
    # We don't remove the acf file as it's shared between all workshop items

    # Clean temporary/download folders (NOT the final content folder unless specified)
    folders_to_clean = [
        os.path.join(steamapps_path, "workshop", "temp", "311210"),
        get_workshop_downloads_folder(workshop_id),
    ]

    # Only delete content folder if explicitly requested (e.g., for failed downloads)
    if delete_content:
        folders_to_clean.append(get_workshop_folder(workshop_id))

    for folder in folders_to_clean:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
                print(f'[{get_current_datetime()}] [Logs] Cleaned folder: {folder}')
            except Exception as e:
                print(f'[{get_current_datetime()}] [Logs] Could not clean folder {folder}: {e}')


def parse_steam_log_timestamp(line):
    """Parse timestamp from steam content_log line like '[2026-02-16 12:34:56]'"""
    try:
        # Extract timestamp between brackets
        match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
        if match:
            timestamp_str = match.group(1)
            return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    except:
        pass
    return None


def monitor_content_log_for_dump(steamcmd_path, workshop_id, download_start_time, stop_flag, result_holder):
    """
    Monitor content_log.txt for download start signal.
    When we see 'download X/Y', IMMEDIATELY clear the folder - that's our window before files get locked.
    """
    # On Linux, logs are in ~/Steam/logs
    content_log_path = os.path.join(get_steam_base_path(), "logs", "content_log.txt")
    downloads_folder = get_workshop_downloads_folder(workshop_id)

    print(f"[{get_current_datetime()}] [DumpMon] Started monitoring for workshop {workshop_id}")
    download_start_datetime = datetime.fromtimestamp(download_start_time).replace(microsecond=0)

    # Wait for log file to exist
    wait_count = 0
    while not os.path.exists(content_log_path) and wait_count < 30:
        if stop_flag():
            return
        time.sleep(0.5)
        wait_count += 1

    if not os.path.exists(content_log_path):
        print(f"[{get_current_datetime()}] [DumpMon] content_log.txt not found")
        return

    try:
        with open(content_log_path, 'r', encoding='utf-8', errors='ignore') as file:
            file.seek(0, 2)

            while not stop_flag():
                line = file.readline()
                if not line:
                    time.sleep(0.05)
                    continue

                if "AppID 311210" in line and "download" in line:
                    log_time = parse_steam_log_timestamp(line)
                    if log_time and log_time >= download_start_datetime:
                        print(f"[{get_current_datetime()}] [DumpMon] Got signal: {line.strip()[:80]}")

                        if os.path.exists(downloads_folder):
                            folder_size = get_folder_size(downloads_folder)
                            print(f"[{get_current_datetime()}] [DumpMon] Clearing {folder_size/1024/1024:.2f}MB NOW")
                            try:
                                shutil.rmtree(downloads_folder)
                                print(f"[{get_current_datetime()}] [DumpMon] Cleared!")
                                result_holder['cleared'] = True
                            except Exception as e:
                                print(f"[{get_current_datetime()}] [DumpMon] Clear failed: {e}")
                                result_holder['cleared'] = True  # Proceed anyway to avoid 15s wait
                        else:
                            # No folder to clear, proceed
                            result_holder['cleared'] = True
                        return

    except Exception as e:
        print(f"[{get_current_datetime()}] [DumpMon] Error: {e}")


# End helper functions
