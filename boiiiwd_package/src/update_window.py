import src.shared_vars as main_app
from src.imports import *
from src.helpers import *


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

class UpdateWindow(ctk.CTkToplevel):
    def __init__(self, master, update_url):
        super().__init__(master)
        self.title("BOIIIWD Self-Updater")
        _, _, x, y = get_window_size_from_registry()
        try: self.geometry(f"400x150+{x}+{y}")
        except: self.geometry("400x150")
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
            update_dir = os.path.join(APPLICATION_PATH, UPDATER_FOLDER)
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

                try: main_app.app.attributes('-alpha', 1.0)
                except: pass
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
