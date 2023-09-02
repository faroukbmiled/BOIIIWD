from src.imports import *
from src.helpers import show_message, cwd, check_config,\
    save_config, reset_steamcmd, launch_boiii_func, get_latest_release_version

def check_for_updates_func(window, ignore_up_todate=False):
    try:
        latest_version = get_latest_release_version()
        current_version = VERSION
        int_latest_version = int(latest_version.replace("v", "").replace(".", ""))
        int_current_version = int(current_version.replace("v", "").replace(".", ""))

        if latest_version and int_latest_version > int_current_version:
            msg_box = CTkMessagebox(title="Update Available", message=f"An update is available! Install now?\n\nCurrent Version: {current_version}\nLatest Version: {latest_version}", option_1="View", option_2="No", option_3="Yes", fade_in_duration=int(1))

            result = msg_box.get()

            if result == "View":
                webbrowser.open(f"https://github.com/{GITHUB_REPO}/releases/latest")

            from src.update_window import UpdateWindow

            if result == "Yes":
                update_window = UpdateWindow(window, LATEST_RELEASE_URL)
                update_window.start_update()

            if result == "No":
                return

        elif int_latest_version < int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(title="Up to Date!", message=f"Unreleased version!\nCurrent Version: {current_version}\nLatest Version: {latest_version}", option_1="Ok")
            result = msg_box.get()
        elif int_latest_version == int_current_version:
            if ignore_up_todate:
                return
            msg_box = CTkMessagebox(title="Up to Date!", message="No Updates Available!", option_1="Ok")
            result = msg_box.get()

        else:
            show_message("Error!", "An error occured while checking for updates!\nCheck your internet and try again")

    except Exception as e:
        show_message("Error", f"Error while checking for updates: \n{e}", icon="cancel")

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
        self.show_fails_cb = ctk.CTkSwitch(left_frame, text="Show fails (on top of progress bar):", variable=self.show_fails_var)
        self.show_fails_cb.grid(row=5, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.show_fails_tooltip = CTkToolTip(self.show_fails_cb, message="Display how many times steamcmd has failed/crashed\nIf the number is getting high quickly then try pressing Reset SteamCMD and try again, otherwise its fine")
        self.estimated_progress_var.set(self.load_settings("show_fails", "on"))

        # Show skip_already_installed maps checkbox
        self.skip_already_installed_var = ctk.BooleanVar()
        self.skip_already_installed_var.trace_add("write", self.enable_save_button)
        self.skip_already_installed_ch = ctk.CTkSwitch(left_frame, text="Skip already installed maps:", variable=self.skip_already_installed_var)
        self.skip_already_installed_ch.grid(row=6, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.skip_already_installed_ch_tooltip = CTkToolTip(self.skip_already_installed_ch, message="If on it will not download installed maps,\nthis can miss sometimes if you remove maps manually and not from library tab while the app is running")
        self.skip_already_installed_var.set(self.load_settings("skip_already_installed", "on"))

        # Resetr steam on many fails
        self.reset_steamcmd_on_fail_var = ctk.IntVar()
        self.reset_steamcmd_on_fail_var.trace_add("write", self.enable_save_button)
        self.reset_steamcmd_on_fail_text = ctk.CTkLabel(left_frame, text=f"Reset steamcmd on % fails: (n of fails)", anchor="w")
        self.reset_steamcmd_on_fail_text.grid(row=7, column=1, padx=20, pady=(10, 0), sticky="nw")
        self.reset_steamcmd_on_fail = ctk.CTkOptionMenu(left_frame, values=["5", "10", "20", "30", "40", "Custom", "Disable"], variable=self.reset_steamcmd_on_fail_var, command=self.reset_steamcmd_on_fail_func)
        self.reset_steamcmd_on_fail.grid(row=8, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.reset_steamcmd_on_fail_tooltip = CTkToolTip(self.reset_steamcmd_on_fail, message="This actually fixes steamcmd when its crashing way too much")
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))

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
        self.theme_options = ctk.CTkOptionMenu(right_frame, values=["Default", "Blue", "Grey", "Obsidian", "Ghost","NeonBanana", "Custom"],
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
                save_config("reset_on_fail", "10")
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
            show_message("Restart to take effect!", f"{option} theme has been set ,please restart to take effect", icon="info")

    def enable_save_button(self, *args):
        try:
            self.save_button.configure(state='normal')
        except:
            pass

    def save_settings(self):
        self.save_button.configure(state='disabled')
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
