from src.imports import *
from src.helpers import show_message, get_folder_size, convert_bytes_to_readable,\
    extract_json_data, get_workshop_file_size, extract_workshop_id, show_noti

class LibraryTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.added_items = set()
        self.grid_columnconfigure(0, weight=1)

        self.radiobutton_variable = ctk.StringVar()
        self.no_items_label = ctk.CTkLabel(self, text="", anchor="w")
        self.filter_entry = ctk.CTkEntry(self, placeholder_text="Your search query here, or type in mod or map to only see that")
        self.filter_entry.bind("<KeyRelease>", self.filter_items)
        self.filter_entry.grid(row=0, column=0,  padx=(10, 20), pady=(10, 20), sticky="we")
        filter_refresh_button_image = os.path.join(RESOURCES_DIR, "Refresh_icon.svg.png")
        self.filter_refresh_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(filter_refresh_button_image)), command=self.refresh_items, width=20, height=20,
                                                   fg_color="transparent", text="")
        self.filter_refresh_button.grid(row=0, column=1, padx=(10, 20), pady=(10, 20), sticky="enw")
        self.label_list = []
        self.button_list = []
        self.button_view_list = []
        self.filter_type = True
        self.clipboard_has_content = False

    def add_item(self, item, image=None, item_type="map", workshop_id=None, folder=None):
        label = ctk.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text="Remove", width=60, height=24, fg_color="#3d3f42")
        button_view = ctk.CTkButton(self, text="Details", width=55, height=24, fg_color="#3d3f42")
        button.configure(command=lambda: self.remove_item(item, folder))
        button_view.configure(command=lambda: self.show_map_info(workshop_id))
        button_view_tooltip = CTkToolTip(button_view, message="Opens up a window that shows basic details")
        button_tooltip = CTkToolTip(button, message="Removes the map/mod from your game")
        label.grid(row=len(self.label_list) + 1, column=0, pady=(0, 10), padx=(5, 10), sticky="w")
        button.grid(row=len(self.button_list) + 1, column=1, pady=(0, 10), padx=(50, 10), sticky="e")
        button_view.grid(row=len(self.button_view_list) + 1, column=1, pady=(0, 10), padx=(10, 75), sticky="w")
        self.label_list.append(label)
        self.button_list.append(button)
        self.button_view_list.append(button_view)
        label.bind("<Enter>", lambda event, label=label: self.on_label_hover(label, enter=True))
        label.bind("<Leave>", lambda event, label=label: self.on_label_hover(label, enter=False))
        label.bind("<Button-1>", lambda event, label=label: self.copy_to_clipboard(label, workshop_id, event))
        label.bind("<Control-Button-1>", lambda event, label=label: self.copy_to_clipboard(label, workshop_id, event, append=True))
        label.bind("<Button-2>", lambda event: self.open_folder_location(folder, event))
        label.bind("<Button-3>", lambda event, label=label: self.copy_to_clipboard(label, folder, event))

    def on_label_hover(self, label, enter):
        if enter:
            label.configure(fg_color="#272727")
        else:
            label.configure(fg_color="transparent")

    def copy_to_clipboard(self, label, something, event=None, append=False):
        try:
            if append:
                if self.clipboard_has_content:
                    label.clipboard_append(f"\n{something}")
                    show_noti(label, "Appended to clipboard", event, 1.0)
                else:
                    label.clipboard_clear()
                    label.clipboard_append(something)
                    self.clipboard_has_content = True
                    show_noti(label, "Copied to clipboard", event, 1.0)
            else:
                label.clipboard_clear()
                label.clipboard_append(something)
                self.clipboard_has_content = True
                show_noti(label, "Copied to clipboard", event, 1.0)
        except:
            pass

    def open_folder_location(self, folder, event=None):
        if os.path.exists(folder):
            os.startfile(folder)
            show_noti(self, "Opening folder", event, 1.0)

    def filter_items(self, event):
        filter_text = self.filter_entry.get().lower()
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            item_text = label.cget("text").lower()
            if filter_text in item_text:
                label.grid()
                button.grid()
                button_view_list.grid()
            else:
                label.grid_remove()
                button_view_list.grid_remove()
                button.grid_remove()

    def load_items(self, boiiiFolder):
        maps_folder = Path(boiiiFolder) / "mods"
        mods_folder = Path(boiiiFolder) / "usermaps"
        mod_img = os.path.join(RESOURCES_DIR, "mod_image.png")
        map_img = os.path.join(RESOURCES_DIR, "map_image.png")

        folders_to_process = [mods_folder, maps_folder]

        for folder_path in folders_to_process:
            for zone_path in folder_path.glob("**/zone"):
                json_path = zone_path / "workshop.json"
                if json_path.exists():
                    name = extract_json_data(json_path, "Title").replace(">", "").replace("^", "")
                    name = name[:45] + "..." if len(name) > 45 else name
                    item_type = extract_json_data(json_path, "Type")
                    workshop_id = extract_json_data(json_path, "PublisherID")
                    folder_name = extract_json_data(json_path, "FolderName")
                    size = convert_bytes_to_readable(get_folder_size(zone_path.parent))
                    text_to_add = f"{name} | Type: {item_type.capitalize()}"
                    mode_type = "ZM" if item_type == "map" and folder_name.startswith("zm") else "MP" if folder_name.startswith("mp") and item_type == "map" else None
                    if mode_type:
                        text_to_add += f" | Mode: {mode_type}"
                    text_to_add += f" | ID: {workshop_id} | Size: {size}"
                    if text_to_add not in self.added_items:
                        self.added_items.add(text_to_add)
                        image_path = mod_img if item_type == "mod" else map_img

                        self.add_item(text_to_add, image=ctk.CTkImage(Image.open(image_path)), item_type=item_type, workshop_id=workshop_id, folder=zone_path.parent)

        if not self.added_items:
            self.show_no_items_message()
        else:
            self.hide_no_items_message()

    def remove_item(self, item, folder):
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            if item == label.cget("text"):
                try:
                    shutil.rmtree(folder)
                except Exception as e:
                    show_message("Error" ,f"Error removing folder '{folder}': {e}", icon="cancel")
                    return
                label.destroy()
                button.destroy()
                button_view_list.destroy()
                self.label_list.remove(label)
                self.button_list.remove(button)
                self.added_items.remove(label.cget("text"))
                self.button_view_list.remove(button_view_list)

    def refresh_items(self):
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            label.destroy()
            button.destroy()
            button_view_list.destroy()
        self.label_list.clear()
        self.button_list.clear()
        self.button_view_list.clear()
        self.added_items.clear()
        from src.main import master_win
        self.load_items(master_win.edit_destination_folder.get().strip())

    def view_item(self, workshop_id):
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        webbrowser.open(url)

    def show_no_items_message(self):
        self.no_items_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="n")
        self.no_items_label.configure(text="No items found in the selected folder. \nMake sure you have a mod/map downloaded and or have the right boiii folder selected.")

    def hide_no_items_message(self):
        self.no_items_label.configure(text="")
        self.no_items_label.forget()

    # i know i know ,please make a pull request i cant be bother
    def show_map_info(self, workshop):
        for button_view in self.button_view_list:
            button_view.configure(state="disabled")

        def show_map_thread():
            workshop_id = workshop

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        show_message("Warning", "Not a valid Workshop ID.")
                except:
                    show_message("Warning", "Not a valid Workshop ID.")
                    return
            try:
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                response = requests.get(url)
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
                    stars_div = soup.find("div", class_="fileRatingDetails")
                    starts = stars_div.find("img")["src"]
                except:
                    show_message("Warning", "Not a valid Workshop ID\nCouldn't get information.")
                    for button_view in self.button_view_list:
                        button_view.configure(state="normal")
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
                        for button_view in self.button_view_list:
                            button_view.configure(state="normal")
                        return

                starts_image_response = requests.get(starts)
                stars_image = Image.open(io.BytesIO(starts_image_response.content))
                stars_image_size = stars_image.size

                image_response = requests.get(workshop_item_image_url)
                image_response.raise_for_status()
                image = Image.open(io.BytesIO(image_response.content))
                image_size = image.size

                self.toplevel_info_window(map_name, map_mod_type, map_size, image, image_size, date_created,
                                        date_updated, stars_image, stars_image_size, ratings_text, url)

            except requests.exceptions.RequestException as e:
                show_message("Error", f"Failed to fetch map information.\nError: {e}", icon="cancel")
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
                return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size, ratings_text, url):
        def main_thread():
            try:
                top = ctk.CTkToplevel(self)
                if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                    top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
                top.title("Map/Mod Information")
                top.attributes('-topmost', 'true')

                def close_window():
                    top.destroy()

                def view_map_mod():
                    webbrowser.open(url)

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

                type_label = ctk.CTkLabel(info_frame, text=f"Type: {map_mod_type}")
                type_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                size_label = ctk.CTkLabel(info_frame, text=f"Size (Workshop): {map_size}")
                size_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                date_created_label = ctk.CTkLabel(info_frame, text=f"Posted: {date_created}")
                date_created_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=5)

                date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}")
                date_updated_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=5)

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

            finally:
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
        self.after(0, main_thread)
