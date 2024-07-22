from xml.sax.xmlreader import InputSource
from src import library_tab
from src.update_window import check_for_updates_func
from src.imports import *
from src.helpers import *

import src.shared_vars as main_app


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
        left_frame.grid(row=0, column=0, columnspan=2, padx=(20, 20), pady=(20, 0), sticky="nsew")
        left_frame.grid_columnconfigure(1, weight=1)
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=2, padx=(0, 20), pady=(20, 0), sticky="nsew")
        right_frame.grid_columnconfigure(1, weight=1)
        self.update_idletasks()

        # Save button
        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_settings, state='disabled')
        self.save_button.grid(row=3, column=1, padx=40, pady=(20, 20), sticky="ne")

        # Check for updates checkbox
        self.check_updates_var = ctk.BooleanVar()
        self.check_updates_var.trace_add("write", self.enable_save_button)
        self.check_updates_checkbox = ctk.CTkSwitch(left_frame, text="Check for updates on launch", variable=self.check_updates_var)
        self.check_updates_checkbox.grid(row=0, column=1, padx=20 , pady=(20, 0), sticky="nw")
        self.check_updates_var.set(self.load_settings("checkforupdates"))

        # Show console checkbox
        self.console_var = ctk.BooleanVar()
        self.console_var.trace_add("write", self.enable_save_button)
        self.checkbox_show_console = ctk.CTkSwitch(left_frame, text="Display console", variable=self.console_var, command=self.toggle_console_window)
        self.checkbox_show_console.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.checkbox_show_console_tooltip = CTkToolTip(self.checkbox_show_console, message="Toggle a console window\nPlease don't close the Console If you want to stop press the Stop button")
        self.console_var.set(self.load_settings("console"))

        # Show continuous checkbox
        self.continuous_var = ctk.BooleanVar()
        self.continuous_var.trace_add("write", self.enable_save_button)
        self.checkbox_continuous = ctk.CTkSwitch(left_frame, text="Continuous download", variable=self.continuous_var)
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
        self.estimated_progress_cb = ctk.CTkSwitch(left_frame, text="Estimated progress bar", variable=self.estimated_progress_var)
        self.estimated_progress_cb.grid(row=4, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.estimated_progress_var_tooltip = CTkToolTip(self.estimated_progress_cb, message="This will change how to progress bar works by estimating how long the download will take\
            \nThis is not accurate ,it's better than with it off which is calculating the downloaded folder size which steamcmd dumps the full size mostly")
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))

        # Show fails checkbox
        self.show_fails_var = ctk.BooleanVar()
        self.show_fails_var.trace_add("write", self.enable_save_button)
        self.show_fails_cb = ctk.CTkSwitch(left_frame, text="Show fails", variable=self.show_fails_var)
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
        self.check_items_ch = ctk.CTkSwitch(left_frame, text="Check library items on launch", variable=self.check_items_var)
        self.check_items_ch.grid(row=7, column=1, padx=20, pady=(20, 0), sticky="nw")
        self.check_items_tooltip = CTkToolTip(self.check_items_ch, message="This will show a window on launch of items that have pending updates -> you can open it manually from library tab")
        self.check_items_var.set(self.load_settings("check_items", "off"))


        # TODO: get windows size to padx for the following checkboxes

        # update invalid
        self.invalid_items_var = ctk.BooleanVar()
        self.invalid_items_var.trace_add("write", self.enable_save_button)
        self.invalid_items_ch = ctk.CTkSwitch(left_frame, text="Update invalid items", variable=self.invalid_items_var)
        self.invalid_items_ch.grid(row=0, column=1, padx=(300,0), pady=(20, 0), sticky="nw")
        self.invalid_items_tooltip = CTkToolTip(self.invalid_items_ch, message="Allow updating invalid items from the details tab")
        self.invalid_items_var.set(self.load_settings("update_invalid", "off"))

        # skip invalid
        self.skip_items_var = ctk.BooleanVar()
        self.skip_items_var.trace_add("write", self.enable_save_button)
        self.skip_items_ch = ctk.CTkSwitch(left_frame, text="Skip invalid items", variable=self.skip_items_var)
        self.skip_items_ch.grid(row=1, column=1, padx=(300,0), pady=(20, 0), sticky="nw")
        self.skip_items_tooltip = CTkToolTip(self.skip_items_ch, message="Skip invalid items")
        self.skip_items_var.set(self.load_settings("skip_invalid", "off"))

        # USING CREDENTIALS
        self.use_steam_creds = ctk.BooleanVar()
        self.use_steam_creds.trace_add("write", self.enable_save_button)
        self.use_steam_creds_sw = ctk.CTkSwitch(left_frame, text="Use Steam Credentials", variable=self.use_steam_creds, command=self.use_steam_creds_inputs)
        self.use_steam_creds_sw.grid(row=2, column=1, padx=(300,0), pady=(20, 0), sticky="nw")
        self.use_steam_creds_tooltip = CTkToolTip(self.use_steam_creds_sw, message="Use your steam login to download (better dowload stability)")
        self.use_steam_creds.set(self.load_settings("use_steam_creds", "off"))

        # text input fields
        self.label_destination_folder = ctk.CTkLabel(left_frame, text='Enter Game folder:')
        self.label_destination_folder.grid(row=8, column=1, padx=20, pady=(20, 0), columnspan=1, sticky="ws")

        self.entry_var1 = ctk.StringVar(value="")
        self.edit_destination_folder = ctk.CTkEntry(left_frame, placeholder_text="game installation folder", textvariable=self.entry_var1)
        self.edit_destination_folder.grid(row=9, column=1, padx=20, pady=(0, 10), columnspan=1, sticky="ewn")
        self.entry_var1.trace_add("write", self.enable_save_button)

        self.button_BOIII_browse = ctk.CTkButton(left_frame, text="Select", command=self.open_BOIII_browser)
        self.button_BOIII_browse.grid(row=9, column=2, padx=(0, 20), pady=(0, 10), sticky="ewn")

        self.label_steamcmd_path = ctk.CTkLabel(left_frame, text="Enter SteamCMD path:")
        self.label_steamcmd_path.grid(row=10, column=1, padx=20, pady=(0, 0), columnspan=1, sticky="wn")

        self.entry_var2 = ctk.StringVar(value="")
        self.edit_steamcmd_path = ctk.CTkEntry(left_frame, placeholder_text="Enter SteamCMD path", textvariable=self.entry_var2)
        self.edit_steamcmd_path.grid(row=11, column=1, padx=20, pady=(0, 10), columnspan=1, sticky="ewn")
        self.entry_var2.trace_add("write", self.enable_save_button)

        self.button_steamcmd_browse = ctk.CTkButton(left_frame, text="Select", command=self.open_steamcmd_path_browser)
        self.button_steamcmd_browse.grid(row=11, column=2, padx=(0, 20), pady=(0, 10), sticky="ewn")

        self.label_launch_args = ctk.CTkLabel(left_frame, text='Launch Parameters:')
        self.label_launch_args.grid(row=12, column=1, padx=20, pady=(0, 0), columnspan=1, sticky="ws")

        self.edit_startup_exe = ctk.CTkEntry(left_frame, placeholder_text="exe")
        self.edit_startup_exe.grid(row=13, column=1, padx=(20,0), pady=(0, 20), columnspan=1, sticky="we")

        self.edit_launch_args = ctk.CTkEntry(left_frame, placeholder_text="launch arguments")
        self.edit_launch_args.grid(row=13, column=1, padx=(140,20), pady=(0, 20), columnspan=2, sticky="we")

        # Check for updates button n Launch game
        self.check_for_updates = ctk.CTkButton(right_frame, text="Check for updates", command=self.settings_check_for_updates)
        self.check_for_updates.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="n")

        # self.launch_game = ctk.CTkButton(right_frame, text="Launch game", command=self.settings_launch_game)
        # self.launch_game.grid(row=2, column=1, padx=20, pady=(10, 0), sticky="n")

        self.reset_steamcmd = ctk.CTkButton(right_frame, text="Reset SteamCMD", command=self.settings_reset_steamcmd)
        self.reset_steamcmd.grid(row=3, column=1, padx=20, pady=(10, 0), sticky="n")
        self.reset_steamcmd_tooltip = CTkToolTip(self.reset_steamcmd, message="This will remove steamapps folder + all the maps that are potentioaly corrupted\nor not so use at ur own risk (could fix some issues as well)")

        self.workshop_to_gamedir = ctk.CTkButton(right_frame, text="Workshop Transfer", command=self.workshop_to_gamedir_toplevel)
        self.workshop_to_gamedir.grid(row=4, column=1, padx=20, pady=(10, 0), sticky="n")
        self.workshop_to_gamedir_tooltip = CTkToolTip(self.workshop_to_gamedir, message="Copy/Move maps and mods from Workshop to the game directory (opens up a window)")

        # appearance
        self.appearance_mode_label = ctk.CTkLabel(right_frame, text="Appearance:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=1, padx=20, pady=(150, 0), sticky="nw")
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(right_frame, values=["Light", "Dark", "System"],
                                                                       command=master.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.scaling_label = ctk.CTkLabel(right_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.scaling_optionemenu = ctk.CTkOptionMenu(right_frame, values=["60%", "70%", "80%", "90%", "100%", "110%"],
                                                               command=master.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=1, padx=20, pady=(0, 0), sticky="nw")

        # self.custom_theme = ctk.CTkButton(right_frame, text="Custom theme", command=self.boiiiwd_custom_theme)
        # self.custom_theme.grid(row=9, column=1, padx=20, pady=(20, 0), sticky="n")

        self.theme_options_label = ctk.CTkLabel(right_frame, text="Theme:", anchor="w")
        self.theme_options_label.grid(row=9, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.theme_options = ctk.CTkOptionMenu(right_frame, values=["Default", "Blue", "Grey", "Obsidian", "Ghost","NeonBanana", "Custom"],
                                                               command=self.theme_options_func)
        self.theme_options.grid(row=10, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.theme_options.set(value=self.load_settings("theme", "Default"))

        # Reset steam on many fails
        self.reset_steamcmd_on_fail_var = ctk.IntVar()
        self.reset_steamcmd_on_fail_var.trace_add("write", self.enable_save_button)
        self.reset_steamcmd_on_fail_text = ctk.CTkLabel(right_frame, text=f"Download Attempts:", anchor="w")
        self.reset_steamcmd_on_fail_text.grid(row=11, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.reset_steamcmd_on_fail = ctk.CTkOptionMenu(right_frame, values=["5", "10", "15", "20", "Custom", "Disable"], variable=self.reset_steamcmd_on_fail_var, command=self.reset_steamcmd_on_fail_func)
        self.reset_steamcmd_on_fail.grid(row=12, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.reset_steamcmd_on_fail_tooltip = CTkToolTip(self.reset_steamcmd_on_fail, message="Number of failed download attempts before resetting SteamCMD")
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))

        # item folder naming
        self.folder_options_label_var = ctk.IntVar()
        self.folder_options_label_var.trace_add("write", self.enable_save_button)
        self.folder_options_label = ctk.CTkLabel(right_frame, text="Items Folder Naming:", anchor="w")
        self.folder_options_label.grid(row=13, column=1, padx=(20,0), pady=(0, 0), sticky="nw")
        self.folder_options = ctk.CTkOptionMenu(right_frame, values=["PublisherID", "FolderName"], command=self.change_folder_naming,
                                                variable=self.folder_options_label_var)
        self.folder_options.grid(row=14, column=1, padx=20, pady=(0, 0), sticky="nw")
        self.folder_options.set(value=self.load_settings("folder_naming", "PublisherID"))

        #version
        self.version_info = ctk.CTkLabel(self, text=f"{VERSION}")
        self.version_info.grid(row=3, column=2, padx=20, pady=(20, 20), sticky="e")

    def open_BOIII_browser(self):
        selected_folder = ctk.filedialog.askdirectory(title="Select Game Folder")
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
                        os.system(f"notepad {os.path.join(APPLICATION_PATH, 'config.ini')}")
                    else:
                        return
                self.after(0, callback)
            except:
                show_message("Couldn't open config.ini" ,"you can do so by yourself and change reset_on_fail value to whatever you want")
        else:
            return

    def theme_options_func(self, option: str):
        theme_mapping = {
            "Default": "boiiiwd_theme.json",
            "Blue": "boiiiwd_blue.json",
            "Grey": "boiiiwd_grey.json",
            "Ghost": "boiiiwd_ghost.json",
            "Obsidian": "boiiiwd_obsidian.json",
            "NeonBanana": "boiiiwd_neonbanana.json",
            "Custom": "boiiiwd_theme.json",
        }

        theme_file = theme_mapping.get(option)

        if option == "Custom":
            self.boiiiwd_custom_theme()
            save_config("theme", "boiiiwd_theme.json")
            return

        if theme_file:
            self.boiiiwd_custom_theme(disable_only=True)
            save_config("theme", theme_file)
        else:
            return

        if option != "Custom":
            if show_message("Restart to take effect!", f"{option} theme has been set, please restart to take effect", icon="info", _return=True, option_1="Ok", option_2="Restart"):
                try:
                    p = psutil.Process(os.getpid())
                    for handler in p.open_files() + p.connections():
                        os.close(handler.fd)
                except Exception:
                    pass
                python = sys.executable
            os.execl(python, python, *sys.argv)

    def enable_save_button(self, *args):
        try: self.save_button.configure(state='normal')
        except: pass

    def save_settings(self):
        self.save_button.configure(state='disabled')

        save_config("GameExecutable", str(self.edit_startup_exe.get()) if not isNullOrWhiteSpace(self.edit_startup_exe.get()) else "BlackOps3")
        save_config("LaunchParameters", str(self.edit_launch_args.get()) if not isNullOrWhiteSpace(self.edit_launch_args.get()) else " ")

        if self.folder_options.get() == "PublisherID":
            save_config("folder_naming", "0")
        else:
            save_config("folder_naming", "1")

        if self.check_items_var.get():
            save_config("check_items", "on")
        else:
            save_config("check_items", "off")

        if self.invalid_items_var.get():
            save_config("update_invalid", "on")
        else:
            save_config("update_invalid", "off")

        if self.skip_items_var.get():
            save_config("skip_invalid", "on")
        else:
            save_config("skip_invalid", "off")

        if self.check_updates_checkbox.get():
            save_config("checkforupdates", "on")
        else:
            save_config("checkforupdates", "off")

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
        if setting == "folder_naming":
            if check_config(setting, fallback) == "1":
                return "FolderName"
            else:
                return "PublisherID"

        if setting == "console":
            if check_config(setting, fallback) == "on":
                show_console()
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
            theme_config = check_config("theme", "boiiiwd_theme.json")

            if os.path.exists(os.path.join(APPLICATION_PATH, theme_config)):
                return "Custom"

            if theme_config == "boiiiwd_theme.json":
                return "Default"

            match = re.match(r'boiiiwd_(\w+)\.json', theme_config)
            if match:
                theme_name = match.group(1).capitalize()
                return theme_name
        else:
            return 1 if check_config(setting, fallback) == "on" else 0

    def boiiiwd_custom_theme(self, disable_only=None):
        file_to_rename = os.path.join(APPLICATION_PATH, "boiiiwd_theme.json")
        if os.path.exists(file_to_rename):
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            name = f"boiiiwd_theme_{timestamp}.json"
            os.rename(file_to_rename, os.path.join(APPLICATION_PATH, name))

            if not disable_only:
                show_message("Preset file renamed", "Custom preset disabled, file has been renmaed\n* Restart the app to take effect", icon="info")
        else:
            if disable_only:
                return
            try:
                shutil.copy(os.path.join(RESOURCES_DIR, check_config("theme", "boiiiwd_theme.json")), os.path.join(APPLICATION_PATH, "boiiiwd_theme.json"))
            except:
                shutil.copy(os.path.join(RESOURCES_DIR, "boiiiwd_theme.json"), os.path.join(APPLICATION_PATH, "boiiiwd_theme.json"))
            show_message("Preset file created", "You can now edit boiiiwd_theme.json in the current directory to your liking\n* Edits will apply next time you open boiiiwd\n* Program will always take boiiiwd_theme.json as the first theme option if found\n* Click on this button again to disable your custom theme or just rename boiiiwd_theme.json", icon="info")

    def settings_check_for_updates(self):
        check_for_updates_func(self, ignore_up_todate=False)

    # make this rename to {id}_duplicate as a fallback
    def rename_all_folders(self, option):
        gameFolder = self.edit_destination_folder.get()
        mods_folder = os.path.join(gameFolder, "mods")
        maps_folder = os.path.join(gameFolder, "usermaps")

        folders_to_process = []

        if os.path.exists(mods_folder):
            folders_to_process.append(mods_folder)

        if os.path.exists(maps_folder):
            folders_to_process.append(maps_folder)

        if not os.path.exists(maps_folder) and not os.path.exists(mods_folder):
            show_message("Warning -> Check game path",
                         f"You don't have any items yet, from now on item's folders will be named as their {option}")
            return 0

        processed_names = set()

        files = Path(folders_to_process[0]).glob("*/zone/workshop.json")
        items = dict()
        ignored_folders = []

        for idx, file in enumerate(files):
            curr_folder_name = os.path.relpath(file, folders_to_process[0]).split("\\", 1)[0]

            with open(file, 'r', errors="ignore") as json_file:
                data = json.load(json_file)
                _item = {
                    'PublisherID': data.get('PublisherID'),
                    'Name': data.get(option),
                    'current_folder': curr_folder_name
                }
                if _item.get('PublisherID')!="" and int(_item.get('PublisherID'))>0:
                    items[idx] = _item
                else:
                    ignored_folders.append(curr_folder_name)

        IDs = [x['PublisherID'] for x in items.values()]
        Names = [x['Name'] for x in items.values()]
        currFolder = [x['current_folder'] for x in items.values()]

        def indices(lst, item):
            return [i for i, x in enumerate(lst) if item in x]

        def find_duplicate_items_in_list(list, items):
            return dict((x, indices(list, x)) for x in [y for y in items if items.count(y) > 1])

        def prep_rename(changelist, orig, new):
            return changelist.append((os.path.join(folders_to_process[0], orig),  os.path.join(folders_to_process[0], new)))

        duplicates = find_duplicate_items_in_list(Names, Names)
        duplicates_IDs = find_duplicate_items_in_list(IDs, IDs)

        duplicate_idx = concatenate_sublists(duplicates.values())

        changelist = []

        for i in range(len(IDs)):
            if i not in duplicate_idx:
                prep_rename(changelist, currFolder[i], Names[i])

        for v in duplicates.values():
            if len(v) == 2:
                if IDs[v[0]] == IDs[v[1]]:
                    prep_rename(changelist, currFolder[v[0]], Names[v[0]])
                    prep_rename(
                        changelist, currFolder[v[1]], Names[v[1]]+"_duplicate")
                else:
                    prep_rename(
                        changelist, currFolder[v[0]], Names[v[0]]+f"_{IDs[v[0]]}")
                    prep_rename(
                        changelist, currFolder[v[1]], Names[v[1]]+f"_{IDs[v[1]]}")

            if len(v) > 2:
                for j, i in enumerate(v):
                    if i in (duplicates_IDs.get(f'{IDs[i]}') if duplicates_IDs.get(f'{IDs[i]}') is not None else []):
                        if i == v[0]:
                            if Names[i].startswith(IDs[i]):
                                prep_rename(
                                    changelist, currFolder[i], Names[i])
                            else:
                                prep_rename(
                                    changelist, currFolder[i], Names[i]+f"_{IDs[i]}")
                        else:
                            if Names[i].startswith(IDs[i]):
                                newname = Names[i]+f"_duplicate"
                            else:
                                newname = Names[i]+f"_{IDs[i]}"

                            if j > 0:
                                newname += '_' + str(j)

                            prep_rename(changelist, currFolder[i], newname)
                    else:
                        prep_rename(
                            changelist, currFolder[i], Names[i]+f"_{IDs[i]}")

        for n in changelist:
            safe_name = nextnonexistentdir(*tuple(reversed(os.path.split(n[1]))))
            if safe_name[0] in ignored_folders and safe_name[1] > 0:
                os.rename(n[0], os.path.join(n[0], '{}_{}'.format(*safe_name)))
            else:
                os.rename(n[0], n[1])

        return 1

    def change_folder_naming(self, option):
        main_app.app.title("BOIII Workshop Downloader - Settings  ➜  Loading... ⏳")
        try:
            if os.path.exists(self.edit_destination_folder.get()):
                lib = main_app.app.library_tab.load_items(self.edit_destination_folder.get(), dont_add=True)
                if not "No items" in lib:
                    if show_message("Renaming", "Would you like to rename all your exisiting item folders now?", _return=True):
                        main_app.app.title("BOIII Workshop Downloader - Settings  ➜  Renaming... ⏳")
                        try : ren_return = self.rename_all_folders(option)
                        except Exception as er: show_message("Error!", f"Error occured when renaming\n{er}"); return
                        if ren_return == 0:
                            return 0
                        else:
                            show_message("Done!", "All folders have been renamed", icon="info")
                            main_app.app.library_tab.load_items(self.edit_destination_folder.get(), dont_add=True)
                    else:
                        show_message("Heads up!", "Only newly downloaded items will be affected", icon="info")
                else:
                    show_message("Warning -> Check game path", f"You don't have any items yet ,from now on item's folders will be named as their {option}")
            else:
                show_message("Warning -> Check game path", f"You don't have any items yet ,from now on item's folders will be named as their {option}")
        except Exception as e:
            show_message("Error", f"Error occured \n{e}")
        finally:
            main_app.app.title("BOIII Workshop Downloader - Settings")
            self.save_settings()

    def load_on_switch_screen(self):
        self.check_updates_var.set(self.load_settings("checkforupdates"))
        self.console_var.set(self.load_settings("console"))
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))
        self.estimated_progress_var.set(self.load_settings("estimated_progress", "on"))
        self.clean_checkbox_var.set(self.load_settings("clean_on_finish", "on"))
        self.continuous_var.set(self.load_settings("continuous_download"))
        self.show_fails_var.set(self.load_settings("show_fails", "on"))
        self.skip_already_installed_var.set(self.load_settings("skip_already_installed", "on"))

        # keep last cuz of trace_add()
        self.save_button.configure(state='disabled')

    def settings_launch_game(self):
        launch_game_func(check_config("destinationfolder"), self.edit_startup_exe.get(), self.edit_launch_args.get())

    def settings_reset_steamcmd(self):
        reset_steamcmd()

    def workshop_to_gamedir_toplevel(self):
        try:
            # to make sure json file is up to date
            main_app.app.library_tab.load_items(self.edit_destination_folder.get(), dont_add=True)
            top = ctk.CTkToplevel(self)
            if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            top.title("Workshop Transfer")
            _, _, x, y = get_window_size_from_registry()
            top.geometry(f"+{x}+{y}")
            # top.attributes('-topmost', 'true')
            top.resizable(False, False)
            # Create input boxes
            center_frame = ctk.CTkFrame(top)

            # Create input boxes
            steam_folder_label = ctk.CTkLabel(center_frame, text="Steam Folder:")
            steam_folder_entry = ctk.CTkEntry(center_frame, width=225)
            button_steam_browse = ctk.CTkButton(center_frame, text="Select", width=10)
            game_folder_label = ctk.CTkLabel(center_frame, text="Game Folder:")
            game_folder_entry = ctk.CTkEntry(center_frame, width=225)
            button_BOIII_browse = ctk.CTkButton(center_frame, text="Select", width=10)

            # Create option to choose between cut or copy
            operation_label = ctk.CTkLabel(center_frame, text="Choose operation:")
            copy_var = ctk.BooleanVar()
            cut_var = ctk.BooleanVar()
            copy_check = ctk.CTkCheckBox(center_frame, text="Copy", variable=copy_var)
            cut_check = ctk.CTkCheckBox(center_frame, text="Cut", variable=cut_var)

            # Create progress bar
            progress_bar = ctk.CTkProgressBar(center_frame, mode="determinate", height=20, corner_radius=7)
            progress_text = ctk.CTkLabel(progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", text_color="white", height=0, width=0, corner_radius=0)
            copy_button = ctk.CTkButton(center_frame, text="Start (Copy)")

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

            def open_game_browser():
                selected_folder = ctk.filedialog.askdirectory(title="Select Game Folder")
                if selected_folder:
                    game_folder_entry.delete(0, "end")
                    game_folder_entry.insert(0, selected_folder)

            def open_steam_browser():
                selected_folder = ctk.filedialog.askdirectory(title="Select Steam Folder (ex: C:/Program Files (x86)/Steam)")
                if selected_folder:
                    steam_folder_entry.delete(0, "end")
                    steam_folder_entry.insert(0, selected_folder)
                    save_config("steam_folder" ,steam_folder_entry.get())

            def start_copy_operation():
                def start_thread():
                    try:
                        if not cut_var.get() and not copy_var.get():
                            show_message("Choose operation!", "Please choose an operation, Copy or Cut files from Steam!")
                            return

                        copy_button.configure(state="disabled")
                        steam_folder = steam_folder_entry.get()
                        ws_folder = os.path.join(steam_folder, "steamapps/workshop/content/311210")
                        game_folder = game_folder_entry.get()

                        if not os.path.exists(steam_folder) and not os.path.exists(ws_folder):
                            show_message("Not found", "Either you have no items downloaded from Steam or wrong path, please recheck path (ex: C:/Program Files (x86)/Steam)")
                            return

                        if not os.path.exists(game_folder):
                            show_message("Not found", "game folder not found, please recheck path")
                            return

                        top.after(0, progress_text.configure(text="Loading..."))

                        map_folder = os.path.join(ws_folder)

                        subfolders = [f for f in os.listdir(map_folder) if os.path.isdir(os.path.join(map_folder, f))]
                        total_folders = len(subfolders)

                        if not subfolders:
                            show_message("No items found", f"No items found in \n{map_folder}")
                            return

                        for i, dir_name in enumerate(subfolders, start=1):
                            json_file_path = os.path.join(map_folder, dir_name, "workshop.json")
                            copy_button.configure(text=f"Working on -> {i}/{total_folders}")

                            if os.path.exists(json_file_path):
                                workshop_id = extract_json_data(json_file_path, "PublisherID")
                                mod_type = extract_json_data(json_file_path, "Type")
                                items_file = os.path.join(APPLICATION_PATH, LIBRARY_FILE)
                                item_exists,_ = main_app.app.library_tab.item_exists_in_file(items_file, workshop_id)

                                if item_exists:
                                    get_folder_name = main_app.app.library_tab.get_item_by_id(items_file, workshop_id, return_option="folder_name")
                                    if get_folder_name:
                                        folder_name = get_folder_name
                                    else:
                                        try:
                                            folder_name = extract_json_data(json_file_path, main_app.app.settings_tab.folder_options.get())
                                        except:
                                            folder_name = extract_json_data(json_file_path, "publisherID")
                                else:
                                    try:
                                        folder_name = extract_json_data(json_file_path, main_app.app.settings_tab.folder_options.get())
                                    except:
                                        folder_name = extract_json_data(json_file_path, "publisherID")

                                if mod_type == "mod":
                                    path_folder = os.path.join(game_folder, "mods")
                                    folder_name_path = os.path.join(path_folder, folder_name, "zone")
                                elif mod_type == "map":
                                    path_folder = os.path.join(game_folder, "usermaps")
                                    folder_name_path = os.path.join(path_folder, folder_name, "zone")
                                else:
                                    show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                                    continue

                                if not item_exists:
                                    while os.path.exists(os.path.join(path_folder, folder_name)):
                                        folder_name += f"_{workshop_id}"
                                        folder_name_path = os.path.join(path_folder, folder_name, "zone")

                                os.makedirs(folder_name_path, exist_ok=True)

                                try:
                                    copy_with_progress(os.path.join(map_folder, dir_name), folder_name_path)
                                except Exception as E:
                                    show_message("Error", f"Error copying files: {E}", icon="cancel")
                                    continue

                                if cut_var.get():
                                    remove_tree(os.path.join(map_folder, dir_name))

                                main_app.app.library_tab.update_item(self.edit_destination_folder.get(), workshop_id, mod_type, folder_name)
                            else:
                                # if its last folder to check
                                if i == total_folders:
                                    show_message("Error", f"workshop.json not found in {dir_name}", icon="cancel")
                                    main_app.app.library_tab.load_items(self.edit_destination_folder.get(), dont_add=True)
                                    return
                                continue

                        if subfolders:
                            main_app.app.library_tab.load_items(self.edit_destination_folder.get(), dont_add=True)
                            main_app.app.show_complete_message(message=f"All items were moved\nYou can run the game now!\nPS: You have to restart the game\n(pressing launch will launch/restarts)")

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
            center_frame.grid(row=0, column=0, padx=20, pady=20)
            button_steam_browse.grid(row=1, column=2, padx=(0, 20), pady=(10, 10), sticky="wnes")
            steam_folder_label.grid(row=0, column=0, padx=(20, 20), pady=(10, 0), sticky='w')
            steam_folder_entry.grid(row=1, column=0, columnspan=2, padx=(0, 20), pady=(10, 10), sticky='nes')
            game_folder_label.grid(row=2, column=0, padx=(20, 20), pady=(10, 0), sticky='w')
            game_folder_entry.grid(row=3, column=0, columnspan=2, padx=(0, 20), pady=(10, 10), sticky='nes')
            button_BOIII_browse.grid(row=3, column=2, padx=(0, 20), pady=(10, 10), sticky="wnes")
            operation_label.grid(row=4, column=0, padx=(20, 20), pady=(10, 10), sticky='wnes')
            copy_check.grid(row=4, column=1, padx=(0, 10), pady=(10, 10), sticky='wnes')
            cut_check.grid(row=4, column=2, padx=(0, 10), pady=(10, 10), sticky='nes')
            progress_bar.grid(row=5, column=0, columnspan=3, padx=(20, 20), pady=(10, 10), sticky='wnes')
            progress_text.place(relx=0.5, rely=0.5, anchor="center")
            copy_button.grid(row=6, column=0, columnspan=3,padx=(20, 20), pady=(10, 10), sticky='wnes')
            progress_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "progress_bar_fill_color")
            progress_bar.configure(progress_color=progress_color)
            steam_folder_entry.insert(1, check_config("steam_folder", ""))
            game_folder_entry.insert(1, self.edit_destination_folder.get())
            button_BOIII_browse.configure(command=open_game_browser)
            button_steam_browse.configure(command=open_steam_browser)
            copy_button.configure(command=start_copy_operation)
            cut_check.configure(command = lambda: check_status(cut_var, copy_var))
            copy_check.configure(command = lambda: check_status(copy_var, cut_var))
            main_app.app.create_context_menu(steam_folder_entry)
            main_app.app.create_context_menu(game_folder_entry)
            copy_var.set(True)
            progress_bar.set(0)
            top.after(150, top.focus_force)

        except Exception as e:
            show_message("Error", f"{e}", icon="cancel")

    def use_steam_creds_inputs(self):
        try:
            if self.use_steam_creds_sw.get() == 0:
                save_config("use_steam_creds", "off")
                save_config("login_cashed", "off")
                return
            top = ctk.CTkToplevel(self)
            if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            _, _, x, y = get_window_size_from_registry()
            top.geometry(f"+{x}+{y}")
            top.title("Input your Steam Username")
            top.geometry("280x130")
            top.resizable(False, False)

            center_frame = ctk.CTkFrame(top)
            center_frame.pack(expand=True, fill=ctk.BOTH, padx=20, pady=20)

            username_label = ctk.CTkLabel(center_frame, text="Username:")
            username_label.grid(row=0, column=0, padx=10, pady=10, sticky='w')
            username_entry = ctk.CTkEntry(center_frame, width=200)
            username_entry.grid(row=0, column=1, padx=10, pady=10, sticky='e')

            config_username_value = load_steam_creds()

            if config_username_value:
                username_entry.insert(0, config_username_value)

            def save_creds():
                username_value = username_entry.get()
                if username_value.strip():
                    save_config("use_steam_creds", "on")
                    save_steam_creds(username_value)
                    top.destroy()

            save_button = ctk.CTkButton(center_frame, text="Save", command=save_creds)
            save_button.grid(row=2, column=0, columnspan=2, pady=20)
            top.after(150, top.focus_force)
            top.after(250, top.focus_force)

        except Exception as e:
            print(f"Error: {e}")

    def toggle_console_window(self):
        if not self.checkbox_show_console.get():
            self.console = False
            hide_console()
            save_config("console", "off")
        else:
            self.console = True
            save_config("console", "on")
            show_console()
