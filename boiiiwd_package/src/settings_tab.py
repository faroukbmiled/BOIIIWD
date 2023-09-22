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
        self.reset_steamcmd_on_fail_text = ctk.CTkLabel(left_frame, text=f"Reset steamcmd: (n of fails):", anchor="w")
        self.reset_steamcmd_on_fail_text.grid(row=8, column=1, padx=20, pady=(10, 0), sticky="nw")
        self.reset_steamcmd_on_fail = ctk.CTkOptionMenu(left_frame, values=["5", "10", "20", "30", "40", "Custom", "Disable"], variable=self.reset_steamcmd_on_fail_var, command=self.reset_steamcmd_on_fail_func)
        self.reset_steamcmd_on_fail.grid(row=8, column=1, padx=(190, 0), pady=(10, 0), sticky="nw")
        self.reset_steamcmd_on_fail_tooltip = CTkToolTip(self.reset_steamcmd_on_fail, message="This actually fixes steamcmd when its crashing way too much")
        self.reset_steamcmd_on_fail.set(value=self.load_settings("reset_on_fail", "10"))

        # item folder naming
        self.folder_options_label_var = ctk.IntVar()
        self.folder_options_label_var.trace_add("write", self.enable_save_button)
        self.folder_options_label = ctk.CTkLabel(left_frame, text="Items Folder Naming:", anchor="nw")
        self.folder_options_label.grid(row=10, column=1, padx=20, pady=(10, 0), sticky="nw")
        self.folder_options = ctk.CTkOptionMenu(left_frame, values=["PublisherID", "FolderName"], command=self.change_folder_naming,
                                                variable=self.folder_options_label_var)
        self.folder_options.grid(row=10, column=1, padx=(150, 0), pady=(3, 0), sticky="nw")
        self.folder_options.set(value=self.load_settings("folder_naming", "PublisherID"))

        # Check for updates button n Launch boiii
        self.check_for_updates = ctk.CTkButton(right_frame, text="Check for updates", command=self.settings_check_for_updates)
        self.check_for_updates.grid(row=1, column=1, padx=20, pady=(20, 0), sticky="n")

        self.launch_boiii = ctk.CTkButton(right_frame, text="Launch boiii", command=self.settings_launch_boiii)
        self.launch_boiii.grid(row=2, column=1, padx=20, pady=(20, 0), sticky="n")

        self.reset_steamcmd = ctk.CTkButton(right_frame, text="Reset SteamCMD", command=self.settings_reset_steamcmd)
        self.reset_steamcmd.grid(row=3, column=1, padx=20, pady=(20, 0), sticky="n")
        self.reset_steamcmd_tooltip = CTkToolTip(self.reset_steamcmd, message="This will remove steamapps folder + all the maps that are potentioaly corrupted\nor not so use at ur own risk (could fix some issues as well)")

        self.steam_to_boiii = ctk.CTkButton(right_frame, text="Steam to boiii", command=self.from_steam_to_boiii_toplevel)
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
                        os.system(f"notepad {os.path.join(application_path, 'config.ini')}")
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
        try: self.save_button.configure(state='normal')
        except: pass

    def save_settings(self):
        self.save_button.configure(state='disabled')

        if self.folder_options.get() == "PublisherID":
            save_config("folder_naming", "0")
        else:
            save_config("folder_naming", "1")

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
        if setting == "folder_naming":
            if check_config(setting, fallback) == "1":
                return "FolderName"
            else:
                return "PublisherID"

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
            if os.path.exists(os.path.join(application_path, "boiiiwd_theme.json")):
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
        file_to_rename = os.path.join(application_path, "boiiiwd_theme.json")
        if os.path.exists(file_to_rename):
            timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            new_name = f"boiiiwd_theme_{timestamp}.json"
            os.rename(file_to_rename, os.path.join(application_path, new_name))

            if not disable_only:
                show_message("Preset file renamed", "Custom preset disabled, file has been renmaed\n* Restart the app to take effect", icon="info")
        else:
            if disable_only:
                return
            try:
                shutil.copy(os.path.join(RESOURCES_DIR, check_config("theme", "boiiiwd_theme.json")), os.path.join(application_path, "boiiiwd_theme.json"))
            except:
                shutil.copy(os.path.join(RESOURCES_DIR, "boiiiwd_theme.json"), os.path.join(application_path, "boiiiwd_theme.json"))
            show_message("Preset file created", "You can now edit boiiiwd_theme.json in the current directory to your liking\n* Edits will apply next time you open boiiiwd\n* Program will always take boiiiwd_theme.json as the first theme option if found\n* Click on this button again to disable your custom theme or just rename boiiiwd_theme.json", icon="info")

    def settings_check_for_updates(self):
        check_for_updates_func(self, ignore_up_todate=False)

    def rename_all_folders(self, option):
        boiiiFolder = main_app.app.edit_destination_folder.get()
        maps_folder = os.path.join(boiiiFolder, "mods")
        mods_folder = os.path.join(boiiiFolder, "usermaps")
        folders_to_process = [mods_folder, maps_folder]
        processed_names = set()
        for folder_path in folders_to_process:
            for folder_name in os.listdir(folder_path):
                zone_path = os.path.join(folder_path, folder_name, "zone")
                if not os.path.isdir(zone_path):
                    continue
                if folder_name in main_app.app.library_tab.item_block_list:
                    continue
                json_path = os.path.join(zone_path, "workshop.json")
                if os.path.exists(json_path):
                    folder_to_rename = os.path.join(folder_path, folder_name)
                    new_folder_name = extract_json_data(json_path, option)
                    while new_folder_name in processed_names:
                        new_folder_name += f"_{extract_json_data(json_path, 'PublisherID')}"
                    new_path = os.path.join(folder_path, new_folder_name)

                    while os.path.exists(new_path):
                        publisher_id = extract_json_data(json_path, 'PublisherID')
                        new_folder_name += f"_{publisher_id}"
                        new_path = os.path.join(folder_path, new_folder_name)

                    os.rename(folder_to_rename, new_path)
                    processed_names.add(new_folder_name)

    def change_folder_naming(self, option):
        main_app.app.title("BOIII Workshop Downloader - Settings  ➜  Loading... ⏳")
        try:
            if os.path.exists(main_app.app.edit_destination_folder.get()):
                lib = main_app.app.library_tab.load_items(main_app.app.edit_destination_folder.get(), dont_add=True)
                if not "No items" in lib:
                    if show_message("Renaming", "Would you like to rename all your exisiting item folders now?", _return=True):
                        main_app.app.title("BOIII Workshop Downloader - Settings  ➜  Renaming... ⏳")
                        try :self.rename_all_folders(option)
                        except Exception as er: show_message("Error!", f"Error occured when renaming\n{er}"); return
                        show_message("Done!", "All folders have been renamed", icon="info")
                    else:
                        show_message("Heads up!", "Only newly downloaded items will be affected", icon="info")
                else:
                    show_message("Warning -> Check boiii path", f"You don't have any items yet ,from now on item's folders will be named as their {option}")
            else:
                show_message("Warning -> Check boiii path", f"You don't have any items yet ,from now on item's folders will be named as their {option}")
        except Exception as e:
            show_message("Error", f"Error occured \n{e}")
        finally:
            main_app.app.title("BOIII Workshop Downloader - Settings")
            self.save_settings()

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

                boiii_folder_label = ctk.CTkLabel(center_frame, text="boiii Folder:")
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
                    selected_folder = ctk.filedialog.askdirectory(title="Select boiii Folder")
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
                                show_message("Not found", "boiii folder not found, please recheck path")
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
                                    items_file = os.path.join(application_path, LIBRARY_FILE)

                                    if main_app.app.library_tab.item_exists_in_file(items_file, workshop_id):
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
                progress_color = get_button_state_colors(check_custom_theme(check_config("theme", fallback="boiiiwd_theme.json")), "progress_bar_fill_color")
                progress_bar.configure(progress_color=progress_color)
                steam_folder_entry.insert(1, check_config("steam_folder", ""))
                boiii_folder_entry.insert(1, main_app.app.edit_destination_folder.get())
                button_BOIII_browse.configure(command=open_BOIII_browser)
                button_steam_browse.configure(command=open_steam_browser)
                copy_button.configure(command=start_copy_operation)
                cut_check.configure(command = lambda: check_status(cut_var, copy_var))
                copy_check.configure(command = lambda: check_status(copy_var, cut_var))
                main_app.app.create_context_menu(steam_folder_entry)
                main_app.app.create_context_menu(boiii_folder_entry)
                copy_var.set(True)
                progress_bar.set(0)

            except Exception as e:
                show_message("Error", f"{e}", icon="cancel")

        main_app.app.after(0, main_thread)
