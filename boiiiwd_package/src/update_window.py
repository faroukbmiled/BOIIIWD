import src.shared_vars as main_app
from src.imports import *
from src.helpers import *


def check_for_updates_func(window, ignore_up_todate=False):
    try:
        latest_version = get_latest_release_version()
        current_version = VERSION
        int_latest_version = parse_version(latest_version)
        int_current_version = parse_version(current_version)

        if latest_version and int_latest_version > int_current_version:
            msg_box = CTkMessagebox(master=window, title="Update Available", message=f"An update is available! Install now?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}",
                                    option_1="View", option_2="No", option_3="Yes", fade_in_duration=int(1), sound=True,
                                    button_width=70, button_height=28)

            result = msg_box.get()

            if result == "View":
                safe_open_url(f"https://github.com/{GITHUB_REPO}/releases/latest")

            if result == "Yes":
                update_window = UpdateWindow(window, LATEST_RELEASE_URL)
                update_window.start_update()

            if result == "No":
                return

        elif int_latest_version < int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(master=window, title="Up to Date!", message=f"Unreleased version!\nCurrent Version: {current_version}\nLatest Version: {latest_version}",
                                    option_1="Ok", sound=True, button_width=80, button_height=28)
            result = msg_box.get()
        elif int_latest_version == int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(master=window, title="Up to Date!", message="No Updates Available!",
                                    option_1="Ok", sound=True, button_width=80, button_height=28)
            result = msg_box.get()

        else:
            show_message("Error!", "An error occured while checking for updates!\nCheck your internet and try again")

    except Exception as e:
        show_message("Error", f"Error while checking for updates: \n{e}", icon="cancel")

class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, update_url):
        super().__init__(master)
        self.title("BOIIIWD Self-Updater")
        _, _, x, y = get_window_size_from_registry()
        try: self.geometry(f"400x150+{x}+{y}")
        except: self.geometry("400x150")
        # Use PNG icon on Linux
        icon_path = os.path.join(RESOURCES_DIR, "ryuk.png")
        if os.path.exists(icon_path):
            try:
                from PIL import Image, ImageTk
                icon_image = ImageTk.PhotoImage(Image.open(icon_path))
                self.after(250, lambda: self.iconphoto(False, icon_image))
                self._icon_image = icon_image  # Keep reference
            except Exception:
                pass
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
        self._progress_determinate = True

    def _set_progress_mode(self, determinate):
        try:
            if determinate:
                self.progress_bar.stop()
                self.progress_bar.configure(mode="determinate")
                self.progress_bar.set(0)
            else:
                self.progress_bar.configure(mode="indeterminate")
                self.progress_label.configure(text="")
                self.progress_bar.start()
        except: pass

    def update_progress_bar(self):
        try:
            update_dir = os.path.join(APPLICATION_PATH, UPDATER_FOLDER)
            current_exe = sys.argv[0]
            program_name = os.path.basename(current_exe)
            # On Linux, use BOIIIWD without .exe extension
            new_exe = os.path.join(update_dir, "BOIIIWD")

            if not os.path.exists(update_dir):
                os.makedirs(update_dir)

            self._progress_determinate = False
            self.after(0, lambda: self._set_progress_mode(False))
            self.after(1, lambda: self.label_download.configure(text="Preparing download..."))
            zip_path = os.path.join(update_dir, "latest_version.zip")

            browser_ua = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            if os.path.exists(zip_path):
                os.remove(zip_path)

            self.total_size = 0
            try:
                head = requests.head(LATEST_RELEASE_URL, headers={"User-Agent": browser_ua}, allow_redirects=True, timeout=15)
                self.total_size = int(head.headers.get("content-length", 0))
            except:
                self.total_size = 0
            if self.total_size:
                self.after(1, lambda: self.label_size.configure(text=f"Size: {convert_bytes_to_readable(self.total_size)}"))

            complete = self._download_requests(zip_path, browser_ua)

            if not self.up_cancelled and not complete:
                raise Exception("Download failed after multiple attempts")

            if not self.up_cancelled:
                self.progress_bar.set(1.0)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(update_dir)
                self.label_download.configure(text="Update Downloaded successfully!")
                def update_msg():
                    msg = CTkMessagebox(master=main_app.app, title="Success!", message="Update downloaded successfully!\nPress Ok to install it.", icon="info", option_1="No", option_2="Ok", sound=True,
                                        button_width=80, button_height=28)
                    response = msg.get()
                    if response == "No":
                        self.destroy()
                        return
                    elif response == "Ok":
                        script_path = create_update_script(current_exe, new_exe, update_dir, program_name)
                        # On Linux, run the bash script directly
                        clean_env = {k: v for k, v in os.environ.items() if not k.startswith("_PYI_") and k not in ("_MEIPASS2", "LD_LIBRARY_PATH")}
                        subprocess.Popen(['bash', script_path], start_new_session=True, env=clean_env)
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

                try: main_app.app.attributes('-alpha', 1.0)
                except: pass
                show_message("Cancelled!", "Update cancelled by user", icon="warning")

        except Exception as e:
            self.progress_bar.set(0.0)
            self.label_download.configure(text="Update failed")
            show_message("Error", f"Error installing the update\n{e}", icon="cancel")

    def _download_requests(self, dest, user_agent):
        base_headers = {"User-Agent": user_agent, "Accept": "application/octet-stream,application/zip,*/*;q=0.8",
                        "Accept-Language": "en-US,en;q=0.9", "Accept-Encoding": "identity"}
        piece = 4 * 1024 * 1024

        if not self.total_size:
            try:
                head = requests.head(LATEST_RELEASE_URL, headers=base_headers, allow_redirects=True, timeout=15)
                self.total_size = int(head.headers.get("content-length", 0))
                if self.total_size:
                    self.after(1, lambda: self.label_size.configure(text=f"Size: {convert_bytes_to_readable(self.total_size)}"))
            except:
                self.total_size = 0

        downloaded = os.path.getsize(dest) if os.path.exists(dest) else 0
        session = requests.Session()
        session.headers.update(base_headers)
        try:
            with open(dest, "ab" if downloaded else "wb") as file:
                while (not self.total_size) or downloaded < self.total_size:
                    if self.up_cancelled:
                        return False
                    end = downloaded + piece - 1
                    if self.total_size:
                        end = min(end, self.total_size - 1)
                    range_headers = {"Range": f"bytes={downloaded}-{end}"}
                    data = b""
                    piece_ok = False
                    for attempt in range(12):
                        if self.up_cancelled:
                            return False
                        try:
                            response = session.get(LATEST_RELEASE_URL, headers=range_headers, timeout=30)
                            if response.status_code == 416:
                                self.total_size = downloaded
                                piece_ok = True
                                break
                            response.raise_for_status()
                            data = response.content
                            if not self.total_size:
                                content_range = response.headers.get("Content-Range", "")
                                if "/" in content_range:
                                    try:
                                        self.total_size = int(content_range.split("/")[-1])
                                        self.after(1, lambda: self.label_size.configure(text=f"Size: {convert_bytes_to_readable(self.total_size)}"))
                                    except:
                                        pass
                            file.write(data)
                            file.flush()
                            downloaded += len(data)
                            piece_ok = True
                            break
                        except requests.exceptions.RequestException:
                            try: session.close()
                            except: pass
                            session = requests.Session()
                            session.headers.update(base_headers)
                            pct = int((downloaded / self.total_size) * 100) if self.total_size else 0
                            self.after(1, lambda p=pct: self.label_download.configure(text=f"Downloading update... ({p}%)"))
                            time.sleep(min(0.4 * (attempt + 1), 3))
                    if not piece_ok:
                        return False
                    if self.total_size:
                        if not self._progress_determinate:
                            self._progress_determinate = True
                            self.after(0, lambda: self._set_progress_mode(True))
                        progress = min(int((downloaded / self.total_size) * 100), 100)
                        self.after(1, lambda: self.label_download.configure(text="Downloading update..."))
                        self.after(1, lambda v=progress / 100.0: self.progress_bar.set(v))
                        self.after(1, lambda p=progress: self.progress_label.configure(text=f"{p}%"))
                    if not self.total_size and len(data) < piece:
                        break
        finally:
            try: session.close()
            except: pass
        return (not self.total_size) or ((os.path.getsize(dest) if os.path.exists(dest) else 0) >= self.total_size)

    def start_update(self):
        self.thread = threading.Thread(target=self.update_progress_bar)
        self.thread.start()

    def cancel_update(self):
        self.up_cancelled = True
        self.withdraw()
