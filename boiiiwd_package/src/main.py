from turtle import title
from src.update_window import check_for_updates_func
from src.helpers import *

from src.library_tab import LibraryTab
from src.settings_tab import SettingsTab


class BOIIIWD(ctk.CTk):
    def __init__(self):
        super().__init__()
        # self.app_instance = BOIIIWD()

        # configure window
        self.title("BOIII Workshop Downloader - Main")

        try:
            geometry_file = os.path.join(application_path, "boiiiwd_dont_touch.conf")
            if os.path.isfile(geometry_file):
                with open(geometry_file, "r") as conf:
                    self.geometry(conf.read())
            else:
                self.geometry(f"{910}x{560}")
        except:
            self.geometry(f"{910}x{560}")

        if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
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

        self.help_button = ctk.CTkButton(master=self.qeueuframe, text="Help", command=self.help_queue_text_func, width=10, height=10, fg_color="#585858")
        self.help_button.grid(row=0, column=0, padx=(352, 0), pady=(23, 0), sticky="en")
        self.help_restore_content = None

        self.queuetextarea = ctk.CTkTextbox(master=self.qeueuframe, font=("", 15))
        self.queuetextarea.grid(row=1, column=0, columnspan=4, padx=(20, 20), pady=(0, 20), sticky="nwse")

        self.status_text = ctk.CTkLabel(self.qeueuframe, text="Status: Standby!")
        self.status_text.grid(row=3, column=0, padx=(20, 20), pady=(0, 20), sticky="ws")

        self.skip_boutton = ctk.CTkButton(master=self.qeueuframe, text="Skip", command=self.skip_current_queue_item, width=10, height=10, fg_color="#585858")

        self.qeueuframe.grid_remove()

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
        self.settings_tab = SettingsTab(self)
        self.library_tab = LibraryTab(self, corner_radius=3)

        # create sidebar frame with widgets
        font = "Comic Sans MS"
        if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.png")):
            ryuks_icon = os.path.join(RESOURCES_DIR, "ryuk.png")
            self.sidebar_icon = ctk.CTkImage(light_image=Image.open(ryuks_icon), dark_image=Image.open(ryuks_icon), size=(40, 40))
        else:
            self.sidebar_icon = None
        self.sidebar_frame = ctk.CTkFrame(self, width=100, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, padx=(10, 20), pady=(10, 10), sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text='',image=self.sidebar_icon)
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.txt_label = ctk.CTkLabel(self.sidebar_frame, text="- Sidebar -", font=(font, 17))
        self.txt_label.grid(row=1, column=0, padx=20, pady=(20, 10))
        self.sidebar_main = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_main.grid(row=2, column=0, padx=10, pady=(20, 6))
        self.sidebar_queue = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_queue.grid(row=3, column=0, padx=10, pady=6)
        self.sidebar_library = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_library.grid(row=4, column=0, padx=10, pady=6, sticky="n")
        self.sidebar_settings = ctk.CTkButton(self.sidebar_frame, height=28)
        self.sidebar_settings.grid(row=5, column=0, padx=10, pady=6, sticky="n")

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

        self.label_speed = ctk.CTkLabel(master=self.slider_progressbar_frame, text="Awaiting Download!")
        self.label_speed.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")
        self.elapsed_time = ctk.CTkLabel(master=self.slider_progressbar_frame, text="", anchor="center")
        self.elapsed_time.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="nsew")  # Use "nsew" to center label
        self.label_file_size = ctk.CTkLabel(master=self.slider_progressbar_frame, text="File size: 0KB")
        self.label_file_size.grid(row=1, column=2, padx=(0, 20), pady=(0, 10), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(master=self.slider_progressbar_frame, mode="determinate", height=20, corner_radius=7)
        self.progress_bar.grid(row=2, column=0, padx=20, pady=(0, 10), columnspan=3, sticky="ew")

        self.progress_text = ctk.CTkLabel(self.progress_bar, text="0%", font=("Helvetica", 12), fg_color="transparent", text_color="white", height=0, width=0, corner_radius=0)
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

        self.label_destination_folder = ctk.CTkLabel(master=self.optionsframe, text='Enter Your boiii folder:')
        self.label_destination_folder.grid(row=3, column=1, padx=20, pady=(0, 0), columnspan=4, sticky="ws")

        self.edit_destination_folder = ctk.CTkEntry(master=self.optionsframe, placeholder_text="Your boiii Instalation folder")
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
        self.is_downloading = False
        self.item_skipped = False
        self.fail_threshold = 0

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

        # context_menus
        self.create_context_menu(self.edit_workshop_id)
        self.create_context_menu(self.edit_destination_folder)
        self.create_context_menu(self.edit_steamcmd_path)
        self.create_context_menu(self.queuetextarea, textbox=True)
        self.create_context_menu(self.library_tab.filter_entry, textbox=False, library=True)
        # valid event required for filter_items()
        self.cevent = Event()
        self.cevent.x = 0
        self.cevent.y = 0

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
            self.settings_tab.load_settings("reset_on_fail", "10")
            self.settings_tab.load_settings("show_fails", "on")
            self.settings_tab.load_settings("skip_already_installed", "on")
        except: pass

        if not check_steamcmd():
            self.show_steam_warning_message()

        # items check for update, ill change all the variables to work this way at a later date
        if self.settings_tab.check_items_var.get():
            self.library_tab.check_for_updates(on_launch=True)

    def do_popup(self, event, frame):
        try: frame.tk_popup(event.x_root, event.y_root)
        finally: frame.grab_release()

    def create_context_menu(self, text_widget, textbox=False, library=False):
        context_menu = Menu(text_widget, tearoff=False, background='#565b5e', fg='white', borderwidth=0, bd=0)
        context_menu.add_command(label="Paste", command=lambda: self.clipboard_paste(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Copy", command=lambda: self.clipboard_copy(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Cut", command=lambda: self.clipboard_cut(text_widget, textbox, library))
        context_menu.add_separator()
        context_menu.add_command(label="Select All", command=lambda: self.select_all(text_widget, textbox))
        text_widget.bind("<Button-3>", lambda event: self.do_popup(event, frame=context_menu))

    def clipboard_copy(self, text, textbox=False, library=False):
        text.clipboard_clear()
        try:
            text.clipboard_append(text.selection_get())
        except:
            if textbox:
                text.clipboard_append(text.get("1.0", END))
            else:
                text.clipboard_append(text.get())
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

    def clipboard_paste(self, text, textbox=False, library=False):
        try:
            if textbox:
                text_cont = text.get("1.0", END)
            else:
                text_cont = text.get()
            if textbox:
                if text.tag_ranges("sel"):
                    text.delete("sel.first", "sel.last")
            else:
                if text.selection_get() in text_cont:
                    start_index = text_cont.index(text.selection_get())
                    end_index = start_index + len(text.selection_get())
                    text.delete(start_index, end_index)
            text.insert(ctk.INSERT, text.clipboard_get())
        except:
            text.insert(ctk.INSERT, text.clipboard_get())
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

    def select_all(self, text_widget, textbox=False):
        if textbox:
            text_widget.tag_add("sel", "1.0", "end")
            text_widget.focus()
        else:
            text_widget.select_range(0, END)
            text_widget.focus()

    def clipboard_cut(self, text, textbox=False, library=False):
        text.clipboard_clear()
        if textbox:
            text_cont = text.get(1.0, END)
        else:
            text_cont = text.get()
        try:
            if textbox:
                if text.tag_ranges("sel"):
                    selected_text = text.get("sel.first", "sel.last")
                    text.clipboard_append(selected_text)
                    text.delete("sel.first", "sel.last")
                else:
                    raise
            else:
                text.clipboard_append(text.selection_get())
                if text.selection_get() in text_cont:
                    start_index = text_cont.index(text.selection_get())
                    end_index = start_index + len(text.selection_get())
                    text.delete(start_index, end_index)
        except:
            if textbox:
                text.clipboard_append(text.get("1.0", END))
                text.delete(1.0, "end")
            else:
                text.clipboard_append(text.get())
                text.delete(0, "end")
        finally:
            if library:
                self.library_tab.filter_items(self.cevent)

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
        self.title("BOIII Workshop Downloader - Library  ➜  Loading... ⏳")
        status = self.library_tab.load_items(self.edit_destination_folder.get())
        self.library_tab.grid(row=0, rowspan=3, column=1, padx=(0, 20), pady=(20, 20), sticky="nsew")
        self.title(f"BOIII Workshop Downloader - Library  ➜  {status}")

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
            steamcmd_path = check_config("SteamCMDPath", application_path)
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
            self.edit_steamcmd_path.insert(0, application_path)
            create_default_config()

    def help_queue_text_func(self, event=None):
        textarea_content = self.queuetextarea.get("1.0", "end").strip()
        help_text = "3010399939,2976006537,2118338989,...\nor:\n3010399939\n2976006537\n2113146805\n..."
        if any(char.strip() for char in textarea_content):
            if help_text in textarea_content:
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press help to see examples:")
                self.help_button.configure(text="Help")
                self.queuetextarea.configure(state="normal")
                self.queuetextarea.delete(1.0, "end")
                self.queuetextarea.insert(1.0, "")
                if self.help_restore_content:
                    self.queuetextarea.insert(1.0, self.help_restore_content.strip())
                else:
                    self.queuetextarea.insert(1.0, "")
            else:
                if not help_text in textarea_content:
                        self.help_restore_content = textarea_content
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press help to see examples:")
                self.help_button.configure(text="Restore")
                self.queuetextarea.configure(state="normal")
                self.queuetextarea.delete(1.0, "end")
                self.queuetextarea.insert(1.0, "")
                self.workshop_queue_label.configure(text="Workshop IDs/Links => press restore to remove examples:")
                self.queuetextarea.insert(1.0, help_text)
                self.queuetextarea.configure(state="disabled")
        else:
            self.help_restore_content = textarea_content
            self.workshop_queue_label.configure(text="Workshop IDs/Links => press restore to remove examples:")
            self.help_button.configure(text="Restore")
            self.queuetextarea.insert(1.0, help_text)
            self.queuetextarea.configure(state="disabled")

    def open_BOIII_browser(self):
        selected_folder = ctk.filedialog.askdirectory(title="Select boiii Folder")
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

    def show_steam_warning_message(self):
        def callback():
            msg = CTkMessagebox(title="Warning", message="steamcmd.exe was not found in the specified directory.\nPress Download to get it or Press Cancel and select it from there!.",
                                icon="warning", option_1="Cancel", option_2="Download", sound=True)
            response = msg.get()
            if response == "Cancel":
                return
            elif response == "Download":
                self.download_steamcmd()
        self.after(0, callback)

    def open_browser(self):
        link = "https://steamcommunity.com/app/311210/workshop/"
        webbrowser.open(link)

    @if_internet_available
    def download_steamcmd(self):
        self.edit_steamcmd_path.delete(0, "end")
        self.edit_steamcmd_path.insert(0, application_path)
        save_config("DestinationFolder" ,self.edit_destination_folder.get())
        save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())
        steamcmd_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        steamcmd_zip_path = os.path.join(application_path, "steamcmd.zip")

        try:
            response = requests.get(steamcmd_url)
            response.raise_for_status()

            with open(steamcmd_zip_path, "wb") as zip_file:
                zip_file.write(response.content)

            with zipfile.ZipFile(steamcmd_zip_path, "r") as zip_ref:
                zip_ref.extractall(application_path)

            if check_steamcmd():
                os.remove(fr"{steamcmd_zip_path}")
                def inti_steam():
                    msg = CTkMessagebox(title="Success", message="SteamCMD has been downloaded ,Press ok to initialize it.", icon="info", option_1="No", option_2="Ok", sound=True)
                    response = msg.get()
                    if response == "No":
                        pass
                    elif response == "Ok":
                        initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                        initialize_steam_thread.start()
                    else:
                        pass
                self.after(0, inti_steam)
            else:
                show_message("Error", "Failed to find steamcmd.exe after extraction.\nMake you sure to select the correct SteamCMD path (by default current BOIIIWD path)", icon="cancel")
                os.remove(fr"{steamcmd_zip_path}")
        except requests.exceptions.RequestException as e:
            show_message("Error", f"Failed to download SteamCMD: {e}", icon="cancel")
            os.remove(fr"{steamcmd_zip_path}")
        except zipfile.BadZipFile:
            show_message("Error", "Failed to extract SteamCMD. The downloaded file might be corrupted.", icon="cancel")
            os.remove(fr"{steamcmd_zip_path}")

    @if_internet_available
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
                headers = {'Cache-Control': 'no-cache'}
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                response = requests.get(url, headers=headers)
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
                    try:
                            description = soup.find('div', class_='workshopItemDescription').get_text(separator='\n')
                    except:
                        description = "Not available"

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
                                        date_updated, stars_image, stars_image_size, ratings_text, url, workshop_id, description)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")
                return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size,
                             ratings_text, url, workshop_id, description):
        def main_thread():
            top = ctk.CTkToplevel(self)
            top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            top.title("Map/Mod Information")
            top.attributes('-topmost', 'true')

            def close_window():
                top.destroy()

            def view_map_mod():
                webbrowser.open(url)

            def show_description(event):
                def main_thread():
                    description_window = ctk.CTkToplevel(None)

                    if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                        description_window.after(210, lambda: description_window.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))

                    description_window.attributes('-topmost', 'true')
                    description_window.title(f"Description - {map_name}")
                    x_pos = event.x_root - 300
                    y_pos = event.y_root - 200
                    calc_req_width = len(description) * 6 + 5
                    win_width = calc_req_width if calc_req_width < 500 else 500
                    description_window.geometry(f"{win_width + 5}x300+{x_pos}+{y_pos}")

                    if check_config("theme", "boiiiwd_theme.json") == "boiiiwd_obsidian.json":
                        description_label = ctk.CTkTextbox(description_window, activate_scrollbars=True, scrollbar_button_color="#5b6c7f")
                    else:
                        description_label = ctk.CTkTextbox(description_window, activate_scrollbars=True)
                    description_label.insert("1.0", description)
                    description_label.pack(fill=ctk.BOTH, expand=True, padx=(10, 10), pady=(10, 10))
                    description_label.configure(state="disabled")

                    self.create_context_menu(description_label, textbox=True)
                    description_window.after(50, description_window.focus_set)

                self.after(0, main_thread)

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

            desc_threshold = 30
            shortened_description = re.sub(r'\n', '', description).strip()
            shortened_description = re.sub(r'([^a-zA-Z0-9\s:().])', '', shortened_description)
            shortened_description = f"{shortened_description[:desc_threshold]}... (View)"\
                                    if len(shortened_description) > desc_threshold else shortened_description
            description_lab = ctk.CTkLabel(info_frame, text=f"Description: {shortened_description}")
            description_lab.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)
            if len(description) > desc_threshold:
                description_lab_tooltip = CTkToolTip(description_lab, message="View description", topmost=True)
                description_lab.configure(cursor="hand2")
                description_lab.bind("<Button-1>", lambda e: show_description(e))

            type_label = ctk.CTkLabel(info_frame, text=f"Type: {map_mod_type}")
            type_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            size_label = ctk.CTkLabel(info_frame, text=f"Size: {map_size}")
            size_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            date_created_label = ctk.CTkLabel(info_frame, text=f"Posted: {date_created}")
            date_created_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=5)

            if date_updated != "Not updated":
                date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated} 🔗")
                date_updated_label_tooltip = CTkToolTip(date_updated_label, message="View changelogs", topmost=True)
                date_updated_label.configure(cursor="hand2")
                date_updated_label.bind("<Button-1>", lambda e:
                    webbrowser.open(f"https://steamcommunity.com/sharedfiles/filedetails/changelog/{workshop_id}"))
            else:
                date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}")

            date_updated_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=5)

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

        self.after(0, main_thread)

    def check_steamcmd_stdout(self, log_file_path, target_item_id):
        temp_file_path = log_file_path + '.temp'
        shutil.copy2(log_file_path, temp_file_path)

        try:
            with open(temp_file_path, 'r') as log_file:
                log_file.seek(0, os.SEEK_END)
                file_size = log_file.tell()

                position = file_size
                lines_found = 0

                while lines_found < 7 and position > 0:
                    position -= 1
                    log_file.seek(position, os.SEEK_SET)

                    char = log_file.read(1)

                    if char == '\n':
                        lines_found += 1

                lines = log_file.readlines()[-7:]

                for line in reversed(lines):
                    line = line.lower().strip()
                    if f"download item {target_item_id.strip()}" in line:
                        return True

            return False
        finally:
            os.remove(temp_file_path)

    def skip_current_queue_item(self):
        if self.button_download._state == "normal":
            self.skip_boutton.grid_remove()
            self.after(1, self.status_text.configure(text=f"Status: Standby!"))
            return
        self.settings_tab.stopped = True
        self.item_skipped = True
        self.settings_tab.steam_fail_counter = 0
        self.is_pressed = False
        self.is_downloading = False
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW)
        self.skip_boutton.grid_remove()
        self.after(2, self.status_text.configure(text=f"Status: Skipping..."))
        self.label_speed.configure(text="Network Speed: 0 KB/s")
        self.progress_text.configure(text="0%")
        self.progress_bar.set(0.0)

    # the real deal
    def run_steamcmd_command(self, command, map_folder, wsid, queue=None):
        steamcmd_path = get_steamcmd_path()
        stdout_path = os.path.join(steamcmd_path, "logs", "workshop_log.txt")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

        os.makedirs(os.path.dirname(stdout_path), exist_ok=True)

        try:
            with open(stdout_path, 'w') as file:
                file.write('')
        except:
            os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

        show_console = subprocess.CREATE_NO_WINDOW
        if self.settings_tab.console:
            show_console = subprocess.CREATE_NEW_CONSOLE

        if os.path.exists(map_folder):
            try:
                try:
                    os.remove(map_folder)
                except:
                    os.rename(map_folder, os.path.join(map_folder, os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", f"couldntremove_{timestamp}")))
            except Exception as e:
                self.settings_tab.stopped = True
                self.queue_stop_button = True
                show_message("Error", f"Couldn't remove {map_folder}, please do so manually\n{e}", icon="cancel")
                self.stop_download()
                return

        if self.settings_tab.continuous:
            start_time = 0
            while not os.path.exists(map_folder) and not self.settings_tab.stopped:
                process = subprocess.Popen(
                    [steamcmd_path + "\steamcmd.exe"] + command.split(),
                    stdout=None if self.settings_tab.console else subprocess.PIPE,
                    stderr=None if self.settings_tab.console else subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=show_console
                )

                #wait for process
                while True:
                    if not self.is_downloading:
                        if self.check_steamcmd_stdout(stdout_path, wsid):
                            start_time = time.time()
                            self.is_downloading = True
                    elapsed_time = time.time() - start_time
                    if process.poll() != None:
                        break
                    time.sleep(1)

                # print("Broken freeeee!")
                self.is_downloading = False
                try:
                    with open(stdout_path, 'w') as file:
                        file.write('')
                except:
                    os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

                if not self.settings_tab.stopped:
                    self.settings_tab.steam_fail_counter = self.settings_tab.steam_fail_counter + 1
                    if elapsed_time < 20 and elapsed_time > 0 and not os.path.exists(map_folder):
                        self.fail_threshold = self.fail_threshold + 1

                if self.settings_tab.steam_fail_counter_toggle:
                    try:
                        if self.fail_threshold >= int(self.settings_tab.steam_fail_number):
                            reset_steamcmd(no_warn=True)
                            self.settings_tab.steamcmd_reset = True
                            self.settings_tab.steam_fail_counter = 0
                            self.fail_threshold = 0
                    except:
                        if self.fail_threshold >= 25:
                            reset_steamcmd(no_warn=True)
                            self.settings_tab.steam_fail_counter = 0
                            self.fail_threshold = 0
        else:
            process = subprocess.Popen(
                [steamcmd_path + "\steamcmd.exe"] + command.split(),
                stdout=None if self.settings_tab.console else subprocess.PIPE,
                stderr=None if self.settings_tab.console else subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                creationflags=show_console
            )

            while True:
                if not self.is_downloading:
                    if self.check_steamcmd_stdout(stdout_path, wsid):
                        self.is_downloading = True
                if process.poll() != None:
                    break
                time.sleep(1)

            # print("Broken freeeee!")
            self.is_downloading = False
            try:
                with open(stdout_path, 'w') as file:
                    file.write('')
            except:
                os.rename(stdout_path, os.path.join(map_folder, os.path.join(stdout_path, f"workshop_log_couldntremove_{timestamp}.txt")))

            if not os.path.exists(map_folder):
                show_message("SteamCMD has terminated", "SteamCMD has been terminated\nAnd failed to download the map/mod, try again or enable continuous download in settings")

        self.settings_tab.stopped = True
        if not queue:
            self.button_download.configure(state="normal")
            self.button_stop.configure(state="disabled")

        return process.returncode

    def show_init_message(self):
        def callback():
            msg = CTkMessagebox(title="Warning", message="SteamCMD is not initialized, Press OK to do so!\nProgram may go unresponsive until SteamCMD is finished downloading.", icon="info", option_1="No", option_2="Ok", sound=True)
            response = msg.get()
            if response == "No":
                return
            elif response == "Ok":
                initialize_steam_thread = threading.Thread(target=lambda: initialize_steam(self))
                initialize_steam_thread.start()
            else:
                return
        self.after(0, callback)

    def show_complete_message(self, message):
        def callback():
            msg = CTkMessagebox(title="Downloads Complete", message=message, icon="info", option_1="Launch", option_2="Ok", sound=True)
            response = msg.get()
            if response=="Launch":
                launch_boiii_func(self.edit_destination_folder.get().strip())
            if response=="Ok":
                return
        self.after(0, callback)

    @if_internet_available
    def download_map(self, update=False):
        self.is_downloading = False
        self.fail_threshold = 0
        if not self.is_pressed:
            self.after(1, self.label_speed.configure(text=f"Loading..."))
            self.is_pressed = True
            self.library_tab.load_items(self.edit_destination_folder.get())
            if self.queue_enabled:
                self.item_skipped = False
                start_down_thread = threading.Thread(target=self.queue_download_thread, args=(update,))
                start_down_thread.start()
            else:
                start_down_thread = threading.Thread(target=self.download_thread, args=(update,))
                start_down_thread.start()
        else:
            show_message("Warning", "Already pressed, Please wait.")

    def queue_download_thread(self, update=None):
        self.stopped = False
        self.queue_stop_button = False
        try:
            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_steam_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                self.show_init_message()
                return

            text = self.queuetextarea.get("1.0", "end")
            items = []
            if "," in text:
                items = [n.strip() for n in text.split(",")]
            else:
                items = [n.strip() for n in text.split("\n") if n.strip()]

            if not items:
                show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                self.stop_download()
                return

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder => in the main tab!.")
                self.stop_download()
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path => in the main tab!.")
                self.stop_download()
                return

            self.total_queue_size = 0
            self.already_installed = []
            for item in items:
                self.fail_threshold = 0
                item.strip()
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download()
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download()
                        return
                if not valid_id(workshop_id):
                    show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                    self.stop_download()
                    return

                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.total_queue_size += ws_file_size

                if file_size is None:
                    show_message("Error", "Failed to retrieve file size.", icon="cancel")
                    self.stop_download()
                    return

                if any(workshop_id in item for item in self.library_tab.added_items):
                    self.already_installed.append(workshop_id)

            if not update:
                if self.already_installed:
                    item_ids = ", ".join(self.already_installed)
                    if self.settings_tab.skip_already_installed:
                        for item in self.already_installed:
                            if item in items:
                                items.remove(item)
                        show_message("Heads up!, map/s skipped => skip is on in settings", f"These item IDs may already be installed and are skipped:\n{item_ids}", icon="info")
                        if not any(isinstance(item, int) for item in items):
                            self.stop_download()
                            return
                    else:
                        show_message("Heads up! map/s not skipped => skip is off in settings", f"These item IDs may already be installed:\n{item_ids}", icon="info")

            self.after(1, self.status_text.configure(text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)}"))
            start_time = time.time()
            for index, item in enumerate(items):
                self.settings_tab.steam_fail_counter = 0
                current_number = index + 1
                total_items = len(items)
                if self.queue_stop_button:
                    self.stop_download()
                    break
                item.strip()
                self.settings_tab.stopped = False
                workshop_id = item
                if not workshop_id.isdigit():
                    try:
                        if extract_workshop_id(workshop_id).strip().isdigit():
                            workshop_id = extract_workshop_id(workshop_id).strip()
                        else:
                            show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                            self.stop_download()
                            return
                    except:
                        show_message("Warning", "Please enter valid Workshop IDs/Links.", icon="warning")
                        self.stop_download()
                        return
                ws_file_size = get_workshop_file_size(workshop_id)
                file_size = ws_file_size
                self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
                download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
                map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
                if not os.path.exists(download_folder):
                    os.makedirs(download_folder)

                def check_and_update_progress():
                    previous_net_speed = 0
                    est_downloaded_bytes = 0
                    file_size = ws_file_size
                    item_name = get_item_name(workshop_id) if get_item_name(workshop_id) else "Error getting name"

                    while not self.settings_tab.stopped:
                        if self.settings_tab.steamcmd_reset:
                            self.settings_tab.steamcmd_reset = False
                            previous_net_speed = 0
                            est_downloaded_bytes = 0

                        if self.item_skipped:
                            if index > 0:
                                prev_item_size = None
                                previous_item = items[index - 1]
                                prev_item_path = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", previous_item)
                                prev_item_path_2 = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", previous_item)
                                if os.path.exists(prev_item_path):
                                    prev_item_size = sum(os.path.getsize(os.path.join(prev_item_path, f)) for f in os.listdir(prev_item_path))
                                elif os.path.exists(prev_item_path_2):
                                    prev_item_size = sum(os.path.getsize(os.path.join(prev_item_path_2, f)) for f in os.listdir(prev_item_path_2))
                                else:
                                    prev_item_size = get_workshop_file_size(previous_item)
                                if prev_item_size:
                                    self.total_queue_size -= prev_item_size
                            self.item_skipped = False

                        while not self.is_downloading and not self.settings_tab.stopped:
                            self.after(1, self.label_speed.configure(text=f"Waiting for steamcmd..."))
                            time_elapsed = time.time() - start_time
                            elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Waiting {current_number}/{total_items}"))
                            if len(items) > 1:
                                self.skip_boutton.grid(row=3, column=1, padx=(10, 20), pady=(0, 25), sticky="ws")
                                if index == len(items) - 1:
                                    self.skip_boutton.grid_remove()
                            time.sleep(1)
                            if self.is_downloading:
                                break

                        try:
                            current_size = sum(os.path.getsize(os.path.join(download_folder, f)) for f in os.listdir(download_folder))
                        except:
                            try:
                                current_size = sum(os.path.getsize(os.path.join(map_folder, f)) for f in os.listdir(map_folder))
                            except:
                                continue

                        progress = int(current_size / file_size * 100)

                        if progress > 100 and not self.settings_tab.stopped:
                            progress = int(current_size / current_size * 100)
                            self.total_queue_size -= file_size
                            file_size = current_size
                            self.total_queue_size += file_size
                            self.after(1, self.status_text.configure(
                                text=f"Status: Total size: ~{convert_bytes_to_readable(self.total_queue_size)} | ID: {workshop_id} | {item_name} | Downloading {current_number}/{total_items}"))
                            self.after(1, lambda p=progress: self.label_file_size.configure(text=f"Wrong size reported\nFile size: ~{convert_bytes_to_readable(current_size)}"))

                        if self.settings_tab.estimated_progress and not self.settings_tab.stopped:
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
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                            time.sleep(1)
                        else:
                            if not self.settings_tab.stopped:
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
                                if self.settings_tab.show_fails:
                                    self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                                else:
                                    self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                                time.sleep(1)

                command = f"+login anonymous app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
                steamcmd_thread = threading.Thread(target=lambda: self.run_steamcmd_command(command, map_folder, workshop_id, queue=True))
                steamcmd_thread.start()

                def wait_for_threads():
                    update_ui_thread = threading.Thread(target=check_and_update_progress)
                    update_ui_thread.daemon = True
                    update_ui_thread.start()
                    update_ui_thread.join()

                    self.progress_text.configure(text="0%")
                    self.progress_bar.set(0.0)

                    map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

                    json_file_path = os.path.join(map_folder, "workshop.json")

                    if os.path.exists(json_file_path):
                        self.label_speed.configure(text="Installing...")
                        mod_type = extract_json_data(json_file_path, "Type")
                        items_file = os.path.join(application_path, LIBRARY_FILE)
                        item_exixsts = self.library_tab.item_exists_in_file(items_file, workshop_id)

                        if item_exixsts:
                            get_folder_name = self.library_tab.get_item_by_id(items_file, workshop_id, return_option="folder_name")
                            if get_folder_name:
                                folder_name = get_folder_name
                            else:
                                try:
                                    folder_name = extract_json_data(json_file_path, self.settings_tab.folder_options.get())
                                except:
                                    folder_name = extract_json_data(json_file_path, "publisherID")
                        else:
                            try:
                                folder_name = extract_json_data(json_file_path, self.settings_tab.folder_options.get())
                            except:
                                folder_name = extract_json_data(json_file_path, "publisherID")

                        if mod_type == "mod":
                            path_folder = os.path.join(destination_folder, "mods")
                            folder_name_path = os.path.join(path_folder, folder_name, "zone")
                        elif mod_type == "map":
                            path_folder = os.path.join(destination_folder, "usermaps")
                            folder_name_path = os.path.join(path_folder, folder_name, "zone")
                        else:
                            show_message("Error", f"Invalid workshop type in workshop.json, are you sure this is a map or a mod?., skipping {workshop_id}...", icon="cancel")
                            return

                        if not item_exixsts:
                            while os.path.exists(os.path.join(path_folder, folder_name)):
                                folder_name += f"_{workshop_id}"
                                folder_name_path = os.path.join(path_folder, folder_name, "zone")

                        os.makedirs(folder_name_path, exist_ok=True)

                        try:
                            self.copy_with_progress(map_folder, folder_name_path)
                        except Exception as E:
                            show_message("Error", f"Error copying files: {E}", icon="cancel")

                        if self.settings_tab.clean_on_finish:
                            remove_tree(map_folder)
                            remove_tree(download_folder)

                        self.library_tab.update_item(self.edit_destination_folder.get(), workshop_id, mod_type, folder_name)

                        if index == len(items) - 1:
                            self.after(1, self.status_text.configure(text=f"Status: Done! => Please press stop only if you see no popup window (rare bug)"))
                            self.show_complete_message(message=f"All files were downloaded\nYou can run the game now!\nPS: You have to restart the game \n(pressing launch will launch/restarts)")
                            self.label_speed.configure(text="Awaiting Download!")
                    elif os.path.exists(json_file_path) and not self.settings_tab.stopped:
                        show_message("Error", "Failed to find workshop.json, please try again.", icon="cancel")
                        if index == len(items) - 1:
                            self.stop_download()
                        return

                self.button_download.configure(state="disabled")
                self.button_stop.configure(state="normal")
                update_wait_thread = threading.Thread(target=wait_for_threads)
                update_wait_thread.start()
                steamcmd_thread.join()
                update_wait_thread.join()

                if index == len(items) - 1:
                    self.button_download.configure(state="normal")
                    self.button_stop.configure(state="disabled")
                    self.after(1, self.status_text.configure(text=f"Status: Done!"))
                    self.skip_boutton.grid_remove()
                    self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
                    self.settings_tab.stopped = True
                    self.stop_download()
                    return
        finally:
            self.settings_tab.steam_fail_counter = 0
            self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))
            self.stop_download()
            self.is_pressed = False

    def download_thread(self, update=None):
        try:
            self.settings_tab.stopped = False

            save_config("DestinationFolder" ,self.edit_destination_folder.get())
            save_config("SteamCMDPath" ,self.edit_steamcmd_path.get())

            if not check_steamcmd():
                self.show_steam_warning_message()
                return

            steamcmd_path = get_steamcmd_path()

            if not is_steamcmd_initialized():
                self.show_init_message()
                return

            workshop_id = self.edit_workshop_id.get().strip()

            destination_folder = self.edit_destination_folder.get().strip()

            if not destination_folder or not os.path.exists(destination_folder):
                show_message("Error", "Please select a valid destination folder.")
                self.stop_download()
                return

            if not steamcmd_path or not os.path.exists(steamcmd_path):
                show_message("Error", "Please enter a valid SteamCMD path.")
                self.stop_download()
                return

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                        self.stop_download()
                        return
                except:
                    show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                    self.stop_download()
                    return

            ws_file_size = get_workshop_file_size(workshop_id)
            file_size = ws_file_size

            if not valid_id(workshop_id):
                show_message("Warning", "Please enter a valid Workshop ID/Link.", icon="warning")
                self.stop_download()
                return

            if file_size is None:
                show_message("Error", "Failed to retrieve file size.", icon="cancel")
                self.stop_download()
                return

            if not update:
                if any(workshop_id in item for item in self.library_tab.added_items):
                    if self.settings_tab.skip_already_installed:
                        show_message("Heads up!, map skipped => Skip is on in settings", f"This item may already be installed, Stopping: {workshop_id}", icon="info")
                        self.stop_download()
                        return
                    show_message("Heads up! map not skipped => Skip is off in settings", f"This item may already be installed: {workshop_id}", icon="info")

            self.after(1, lambda mid=workshop_id: self.label_file_size.configure(text=f"File size: {get_workshop_file_size(mid ,raw=True)}"))
            download_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "downloads", "311210", workshop_id)
            map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)
            if not os.path.exists(download_folder):
                os.makedirs(download_folder)

            def check_and_update_progress():
                previous_net_speed = 0
                est_downloaded_bytes = 0
                start_time = time.time()
                file_size = ws_file_size

                while not self.settings_tab.stopped:
                    if self.settings_tab.steamcmd_reset:
                        self.settings_tab.steamcmd_reset = False
                        previous_net_speed = 0
                        est_downloaded_bytes = 0

                    while not self.is_downloading and not self.settings_tab.stopped:
                        self.after(1, self.label_speed.configure(text=f"Waiting for steamcmd..."))
                        time_elapsed = time.time() - start_time
                        elapsed_hours, elapsed_minutes, elapsed_seconds = convert_seconds(time_elapsed)
                        if self.settings_tab.show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                        time.sleep(1)
                        if self.is_downloading:
                            break

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


                    if self.settings_tab.estimated_progress and not self.settings_tab.stopped:
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
                        if self.settings_tab.show_fails:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                        else:
                            self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))

                        time.sleep(1)
                    else:
                        if not self.settings_tab.stopped:
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
                            if self.settings_tab.show_fails:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d} - Fails: {self.fail_threshold}"))
                            else:
                                self.after(1, lambda h=elapsed_hours, m=elapsed_minutes, s=elapsed_seconds: self.elapsed_time.configure(text=f"Elapsed Time: {int(h):02d}:{int(m):02d}:{int(s):02d}"))
                            time.sleep(1)

            command = f"+login anonymous app_update 311210 +workshop_download_item 311210 {workshop_id} validate +quit"
            steamcmd_thread = threading.Thread(target=lambda: self.run_steamcmd_command(command, map_folder, workshop_id))
            steamcmd_thread.start()

            def wait_for_threads():
                update_ui_thread = threading.Thread(target=check_and_update_progress)
                update_ui_thread.daemon = True
                update_ui_thread.start()
                update_ui_thread.join()

                self.settings_tab.stopped = True
                self.progress_text.configure(text="0%")
                self.progress_bar.set(0.0)

                map_folder = os.path.join(get_steamcmd_path(), "steamapps", "workshop", "content", "311210", workshop_id)

                json_file_path = os.path.join(map_folder, "workshop.json")

                if os.path.exists(json_file_path):
                    self.label_speed.configure(text="Installing...")
                    mod_type = extract_json_data(json_file_path, "Type")
                    items_file = os.path.join(application_path, LIBRARY_FILE)
                    item_exixsts = self.library_tab.item_exists_in_file(items_file, workshop_id)

                    if item_exixsts:
                        get_folder_name = self.library_tab.get_item_by_id(items_file, workshop_id, return_option="folder_name")
                        if get_folder_name:
                            folder_name = get_folder_name
                        else:
                            try:
                                folder_name = extract_json_data(json_file_path, self.settings_tab.folder_options.get())
                            except:
                                folder_name = extract_json_data(json_file_path, "publisherID")
                    else:
                        try:
                            folder_name = extract_json_data(json_file_path, self.settings_tab.folder_options.get())
                        except:
                            folder_name = extract_json_data(json_file_path, "publisherID")

                    if mod_type == "mod":
                        path_folder = os.path.join(destination_folder, "mods")
                        folder_name_path = os.path.join(path_folder, folder_name, "zone")
                    elif mod_type == "map":
                        path_folder = os.path.join(destination_folder, "usermaps")
                        folder_name_path = os.path.join(path_folder, folder_name, "zone")
                    else:
                        show_message("Error", "Invalid workshop type in workshop.json, are you sure this is a map or a mod?.", icon="cancel")
                        self.stop_download()
                        return

                    if not item_exixsts:
                        while os.path.exists(os.path.join(path_folder, folder_name)):
                            folder_name += f"_{workshop_id}"
                            folder_name_path = os.path.join(path_folder, folder_name, "zone")

                    os.makedirs(folder_name_path, exist_ok=True)

                    try:
                        self.copy_with_progress(map_folder, folder_name_path)
                    except Exception as E:
                        show_message("Error", f"Error copying files: {E}", icon="cancel")

                    if self.settings_tab.clean_on_finish:
                        remove_tree(map_folder)
                        remove_tree(download_folder)

                    self.library_tab.update_item(self.edit_destination_folder.get(), workshop_id, mod_type, folder_name)
                    self.show_complete_message(message=f"{mod_type.capitalize()} files were downloaded\nYou can run the game now!\nPS: You have to restart the game \n(pressing launch will launch/restarts)")
                    self.button_download.configure(state="normal")
                    self.button_stop.configure(state="disabled")
                elif os.path.exists(json_file_path) and not self.settings_tab.stopped:
                    show_message("Error", "Failed to find workshop.json, please try again.", icon="cancel")
                    self.stop_download()
                    return

            update_wait_thread = threading.Thread(target=wait_for_threads)
            update_wait_thread.start()
            self.button_download.configure(state="disabled")
            self.button_stop.configure(state="normal")
            steamcmd_thread.join()
            update_wait_thread.join()

        finally:
            self.settings_tab.steam_fail_counter = 0
            self.stop_download()
            self.is_pressed = False

    def copy_with_progress(self, src, dst):
        try:
            total_files = sum([len(files) for root, dirs, files in os.walk(src)])
            progress = 0

            def copy_progress(src, dst):
                nonlocal progress
                shutil.copy2(src, dst)
                progress += 1
                self.progress_text.configure(text=f"Copying files: {progress}/{total_files}")
                value = (progress / total_files) * 100
                valuep = value / 100
                self.progress_bar.set(valuep)

            try:
                shutil.copytree(src, dst, dirs_exist_ok=True, copy_function=copy_progress)
            except Exception as E:
                show_message("Error", f"Error copying files: {E}", icon="cancel")
        finally:
            self.progress_text.configure(text="0%")
            self.progress_bar.set(0.0)

    def stop_download(self, on_close=None):
        self.settings_tab.stopped = True
        self.queue_stop_button = True
        self.settings_tab.steam_fail_counter = 0
        self.is_pressed = False
        self.is_downloading = False
        self.after(1, self.label_file_size.configure(text=f"File size: 0KB"))

        if on_close:
            subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
            return

        subprocess.run(['taskkill', '/F', '/IM', 'steamcmd.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)

        self.button_download.configure(state="normal")
        self.button_stop.configure(state="disabled")
        self.progress_text.configure(text="0%")
        self.elapsed_time.configure(text=f"")
        self.progress_bar.set(0.0)
        self.after(50, self.status_text.configure(text=f"Status: Standby!"))
        self.after(1, self.label_speed.configure(text=f"Awaiting Download!"))
        self.skip_boutton.grid_remove()
