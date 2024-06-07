from src.imports import *
from src.helpers import *

import src.shared_vars as main_app


class LibraryTab(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):

        super().__init__(master, **kwargs)
        self.added_items = set()
        self.to_update = set()
        self.grid_columnconfigure(0, weight=1)

        self.radiobutton_variable = ctk.StringVar()
        self.no_items_label = ctk.CTkLabel(self, text="", anchor="w")
        self.filter_entry = ctk.CTkEntry(self, placeholder_text="Your search query here, or type in mod or map to only see that")
        self.filter_entry.bind("<KeyRelease>", self.filter_items)
        self.filter_entry.grid(row=0, column=0,  padx=(10, 20), pady=(10, 20), sticky="we")
        filter_refresh_button_image = os.path.join(RESOURCES_DIR, "Refresh_icon.svg.png")
        update_button_image = os.path.join(RESOURCES_DIR, "update_icon.png")
        self.filter_refresh_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(filter_refresh_button_image)), command=self.refresh_items, width=20, height=20,
                                                   fg_color="transparent", text="")
        self.filter_refresh_button.grid(row=0, column=1, padx=(10, 0), pady=(10, 20), sticky="nw")
        self.update_button = ctk.CTkButton(self, image=ctk.CTkImage(Image.open(update_button_image)), command=self.check_for_updates, width=65, height=20,
                                           text="", fg_color="transparent")
        self.update_button.grid(row=0, column=1, padx=(0, 20), pady=(10, 20), sticky="en")
        self.update_button.configure(state="disabled")
        self.update_tooltip = CTkToolTip(self.update_button, message="Check items for updates", topmost=True)
        filter_tooltip = CTkToolTip(self.filter_refresh_button, message="Refresh library", topmost=True)
        self.label_list = []
        self.button_list = []
        self.button_view_list = []
        self.file_cleaned = False
        self.filter_type = True
        self.clipboard_has_content = False
        self.item_block_list = set()
        self.added_folders = set()
        self.ids_added = set()
        self.refresh_next_time = False

    def add_item(self, item, image=None, workshop_id=None, folder=None, invalid_warn=False):
        label = ctk.CTkLabel(self, text=item, image=image, compound="left", padx=5, anchor="w")
        button = ctk.CTkButton(self, text="Remove", width=60, height=24, fg_color="#3d3f42")
        button_view = ctk.CTkButton(self, text="Details", width=55, height=24, fg_color="#3d3f42")
        button.configure(command=lambda: self.remove_item(item, folder, workshop_id))
        button_view.configure(command=lambda: self.show_map_info(workshop_id, folder ,invalid_warn))
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
        if invalid_warn:
            label_warn = CTkToolTip(label, message="Duplicated or Blocked item (Search item id in search)")

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

    def item_exists_in_file(self, items_file, workshop_id, folder_name=None):
        if not os.path.exists(items_file):
            return False, False

        with open(items_file, "r", encoding='utf-8', errors="ignore") as f:
            items_data = json.load(f)
            for item_info in items_data:
                if not folder_name and "id" in item_info and item_info["id"] == workshop_id:
                    return True, False

                if "id" in item_info and "folder_name" in item_info and "json_folder_name" in item_info:
                    if item_info["id"] == workshop_id and item_info["folder_name"] == folder_name:
                        if item_info["folder_name"] in self.added_folders:
                            continue
                        if item_info["folder_name"] in self.item_block_list:
                            return False ,None
                        return True, True
                    elif item_info["id"] == workshop_id:
                        if item_info["folder_name"] in self.added_folders:
                            continue
                        if item_info["folder_name"] in self.item_block_list:
                            return False ,None
                        return True, False

                elif "id" in item_info and item_info["id"] == workshop_id:
                    return True, False
        return False, False

    def remove_item_by_option(self, items_file, option, option_name="id"):

        if not os.path.exists(items_file):
            return

        with open(items_file, "r", encoding='utf-8', errors="ignore") as f:
            items_data = json.load(f)

        updated_items_data = [item for item in items_data if item.get(option_name) != option]

        if len(updated_items_data) < len(items_data):
            with open(items_file, "w", encoding='utf-8', errors="ignore") as f:
                json.dump(updated_items_data, f, indent=4)

    def get_item_by_id(self, items_file, item_id, return_option="all"):

        if not os.path.exists(items_file):
            return None

        with open(items_file, "r", encoding='utf-8', errors="ignore") as f:
            items_data = json.load(f)

        for item in items_data:
            if item.get("id") == item_id:
                if return_option == "all":
                    return item
                elif return_option == return_option:
                    return item.get(return_option)
        return None

    def get_item_index_by_id(self, items_data, item_id):
        for index, item in enumerate(items_data):
            if item.get("id") == item_id:
                return index
        return None

    def update_or_add_item_by_id(self, items_file, item_info, item_id):
        if not os.path.exists(items_file):
            with open(items_file, "w", encoding='utf-8', errors="ignore") as f:
                json.dump([item_info], f, indent=4)
        else:
            with open(items_file, "r+", encoding='utf-8', errors="ignore") as f:
                items_data = json.load(f)
                existing_item_index = self.get_item_index_by_id(items_data, item_id)
                if existing_item_index is not None:
                    items_data[existing_item_index] = item_info
                else:
                    items_data.append(item_info)
                f.seek(0)
                f.truncate()
                json.dump(items_data, f, indent=4)

    def clean_json_file(self, file):

        if not os.path.exists(file):
            show_message("Error", f"File '{file}' does not exist.")
            return

        with open(file, "r", encoding='utf-8', errors="ignore") as f:
            items_data = json.load(f)

        cleaned_items = [item for item in items_data if 'folder_name' in item and 'json_folder_name'
                         in item and item['folder_name'] not in self.item_block_list and item['folder_name']
                         in self.added_folders and item['id'] in self.ids_added]

        with open(file, 'w', encoding='utf-8', errors="ignore") as file:
            json.dump(cleaned_items, file, indent=4)

    def is_valid_json_format(self, file):
        try:
            with open(file, "r", encoding='utf-8', errors="ignore") as file:
                data = json.load(file)
            if not isinstance(data, list):
                return False

            for item in data:
                if not all(key in item for key in ("id", "text", "date", "folder_name", "json_folder_name")):
                    return False

            return True
        except:
            return False

    def rename_invalid_json_file(self, file_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        base_name, ext = os.path.splitext(file_path)
        new_file_path = f"{base_name}_{timestamp}{ext}"
        os.rename(file_path, new_file_path)

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

    def add_item_helper(self, text, image_path, workshop_id, folder, invalid_warn=False, item_type=None):
        image = ctk.CTkImage(Image.open(image_path))
        self.add_item(text, image=image, workshop_id=workshop_id, folder=folder, invalid_warn=invalid_warn)

    # sort by type then alphabet (name), index 5 is type 0 is name/text
    def sorting_key(self, item):
        item_type, item_name = item[5], item[0]
        return (0, item_name) if item_type == "map" else (1, item_name)

    def load_items(self, gameFolder, dont_add=False):
        if self.refresh_next_time and not dont_add:
            self.refresh_next_time = False
            status = self.refresh_items()
            return status

        if dont_add:
            self.added_items.clear()
            self.added_folders.clear()
            self.ids_added.clear()
            self.refresh_next_time = True

        maps_folder = Path(gameFolder) / "mods"
        mods_folder = Path(gameFolder) / "usermaps"
        mod_img = os.path.join(RESOURCES_DIR, "mod_image.png")
        map_img = os.path.join(RESOURCES_DIR, "map_image.png")
        b_mod_img = os.path.join(RESOURCES_DIR, "b_mod_image.png")
        b_map_img = os.path.join(RESOURCES_DIR, "b_map_image.png")
        map_count = 0
        mod_count = 0
        total_size = 0

        folders_to_process = [mods_folder, maps_folder]
        ui_items_to_add = []

        items_file = os.path.join(APPLICATION_PATH, LIBRARY_FILE)
        if not self.is_valid_json_format(items_file):
            try: self.rename_invalid_json_file(items_file)
            except: pass

        for folder_path in folders_to_process:
            for zone_path in folder_path.glob("*/zone"):
                json_path = zone_path / "workshop.json"
                if json_path.exists():

                    curr_folder_name = zone_path.parent.name
                    workshop_id = extract_json_data(json_path, "PublisherID") or "None"
                    name = re.sub(r'\^\d', '', extract_json_data(json_path, "Title")) or "None"
                    name = name[:60] + "..." if len(name) > 60 else name
                    item_type = extract_json_data(json_path, "Type") or "None"
                    folder_name = extract_json_data(json_path, "FolderName") or "None"
                    folder_size_bytes = get_folder_size(zone_path.parent)
                    size = convert_bytes_to_readable(folder_size_bytes)
                    total_size += folder_size_bytes
                    text_to_add = f"{name} | Type: {item_type.capitalize()}"
                    mode_type = "ZM" if item_type == "map" and folder_name.startswith("zm") else "MP" if folder_name.startswith("mp") and item_type == "map" else None
                    if mode_type:
                        text_to_add += f" | Mode: {mode_type}"
                    text_to_add += f" | ID: {workshop_id} | Size: {size}"

                    creation_timestamp = None
                    for ff_file in zone_path.glob("*.ff"):
                        if ff_file.exists():
                            creation_timestamp = ff_file.stat().st_mtime
                            break

                    if creation_timestamp is not None:
                        date_added = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")
                    else:
                        creation_timestamp = zone_path.stat().st_mtime
                        date_added = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")

                    map_count += 1 if item_type == "map" else 0
                    mod_count += 1 if item_type == "mod" else 0
                    if curr_folder_name not in self.added_folders:
                        image_path = mod_img if item_type == "mod" else map_img
                        if not (str(curr_folder_name).strip() == str(workshop_id).strip() or str(curr_folder_name).strip() == str(folder_name).strip()
                                or str(curr_folder_name).strip() == f"{folder_name}_{workshop_id}" or str(curr_folder_name).strip() == f"{folder_name}_duplicated"):
                            try: self.remove_item_by_option(items_file, curr_folder_name, "folder_name")
                            except: pass
                            self.item_block_list.add(curr_folder_name)
                            image_path = b_mod_img if item_type == "mod" else b_map_img
                            text_to_add = re.sub(r'ID:\s+(?:\d+|None)', f'Folder: {curr_folder_name}', text_to_add)
                            text_to_add += " | ⚠️"
                        elif (curr_folder_name not in self.added_folders and (workshop_id in self.ids_added or workshop_id == "None")):
                            try: self.remove_item_by_option(items_file, curr_folder_name, "folder_name")
                            except: pass
                            self.item_block_list.add(workshop_id)
                            text_to_add = re.sub(r'ID:\s+(?:\d+|None)', f'Folder: {curr_folder_name}', text_to_add)
                            image_path = b_mod_img if item_type == "mod" else b_map_img
                            text_to_add += " | ⚠️"

                        self.added_items.add(text_to_add)
                        if image_path is b_mod_img or image_path is b_map_img and not dont_add:
                            ui_items_to_add.append((text_to_add, image_path, workshop_id, zone_path.parent, True, item_type))
                        elif not dont_add:
                            ui_items_to_add.append((text_to_add, image_path, workshop_id, zone_path.parent, False, item_type))
                        id_found, folder_found = self.item_exists_in_file(items_file, workshop_id, curr_folder_name)
                        item_info = {
                                "id": workshop_id,
                                "text": text_to_add,
                                "date": date_added,
                                "folder_name": curr_folder_name,
                                "json_folder_name": folder_name
                            }
                        # when item is blocked item_exists_in_file() returns None for folder_found
                        if not id_found and folder_found == None:
                            self.remove_item_by_option(items_file, curr_folder_name, "folder_name")
                        elif not id_found and not folder_found and curr_folder_name not in self.item_block_list and workshop_id not in self.ids_added:
                            if not os.path.exists(items_file):
                                with open(items_file, "w", encoding='utf-8', errors="ignore") as f:
                                    json.dump([item_info], f, indent=4)
                            else:
                                with open(items_file, "r+", encoding='utf-8', errors="ignore") as f:
                                    items_data = json.load(f)
                                    items_data.append(item_info)
                                    f.seek(0)
                                    json.dump(items_data, f, indent=4)

                        if curr_folder_name not in self.item_block_list:
                            self.update_or_add_item_by_id(items_file, item_info, workshop_id)

                        # keep here cuz of item_exists_in_file() testing
                        self.added_folders.add(curr_folder_name)
                        # added that cuz it sometimes can add blocked ids first
                        # and legit ids will be blocked cuz theyll be added to "ids_added"
                        if not workshop_id in self.ids_added and curr_folder_name not in self.item_block_list and workshop_id!='None':
                            self.ids_added.add(workshop_id)

        # sort items by type then alphabet
        ui_items_to_add.sort(key=self.sorting_key)
        for item in ui_items_to_add:
            self.add_item_helper(*item)

        if os.path.exists(items_file):
            self.file_cleaned = True
            self.clean_json_file(items_file)

        if not self.added_items:
            self.show_no_items_message()
        else:
            self.hide_no_items_message()

        if all(item in self.item_block_list for item in self.added_folders):
            self.show_no_items_message(only_up=True)

        if map_count > 0 or mod_count > 0:
            return f"Maps: {map_count} - Mods: {mod_count} - Total size: {convert_bytes_to_readable(total_size)}"

        self.show_no_items_message(only_up=True)
        return "No items in current selected folder"

    def update_item(self, gameFolder, id, item_type, foldername):
        try:
            if item_type == "map":
                folder_path = Path(gameFolder) / "usermaps" / f"{foldername}"
            elif item_type == "mod":
                folder_path = Path(gameFolder) / "mods" / f"{foldername}"
            else:
                raise ValueError("Unsupported item_type. It must be 'map' or 'mod'.")

            for zone_path in folder_path.glob("*/zone"):
                json_path = zone_path / "workshop.json"
                if json_path.exists():
                    workshop_id = extract_json_data(json_path, "PublisherID")
                    if workshop_id == id:
                        name = extract_json_data(json_path, "Title").replace(">", "").replace("^", "")
                        name = name[:60] + "..." if len(name) > 60 else name
                        item_type = extract_json_data(json_path, "Type")
                        folder_name = extract_json_data(json_path, "FolderName")
                        size = convert_bytes_to_readable(get_folder_size(zone_path.parent))
                        text_to_add = f"{name} | Type: {item_type.capitalize()}"
                        mode_type = "ZM" if item_type == "map" and folder_name.startswith("zm") else "MP" if folder_name.startswith("mp") and item_type == "map" else None
                        if mode_type:
                            text_to_add += f" | Mode: {mode_type}"
                        text_to_add += f" | ID: {workshop_id} | Size: {size}"

                        creation_timestamp = None
                        for ff_file in zone_path.glob("*.ff"):
                            if ff_file.exists():
                                creation_timestamp = ff_file.stat().st_mtime
                                break

                        if creation_timestamp is not None:
                            date_added = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")
                        else:
                            creation_timestamp = zone_path.stat().st_mtime
                            date_added = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")

                        items_file = os.path.join(APPLICATION_PATH, LIBRARY_FILE)

                        item_info = {
                            "id": workshop_id,
                            "text": text_to_add,
                            "date": date_added,
                            "folder_name": foldername,
                            "json_folder_name": folder_name
                        }
                        self.update_or_add_item_by_id(items_file, item_info, id)
                        return

        except Exception as e:
            show_message("Error updating json file", f"Error while updating library json file\n{e}")

    def remove_item(self, item, folder, id):
        items_file = os.path.join(APPLICATION_PATH, LIBRARY_FILE)
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            if item == label.cget("text"):
                self.added_folders.remove(os.path.basename(folder))
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
                self.ids_added.remove(id)
                self.button_view_list.remove(button_view_list)
                self.remove_item_by_option(items_file, id)

    def refresh_items(self):
        main_app.app.title("BOIII Workshop Downloader - Library  ➜  Loading... ⏳")
        for label, button, button_view_list in zip(self.label_list, self.button_list, self.button_view_list):
            label.destroy()
            button.destroy()
            button_view_list.destroy()
        self.label_list.clear()
        self.button_list.clear()
        self.button_view_list.clear()
        self.added_items.clear()
        self.added_folders.clear()
        self.ids_added.clear()

        status = self.load_items( main_app.app.settings_tab.edit_destination_folder.get().strip())
        main_app.app.title(f"BOIII Workshop Downloader - Library  ➜  {status}")
        # main_app library event needs a return for status => when refresh_next_time is true
        return status

    def view_item(self, workshop_id):
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        webbrowser.open(url)

    def show_no_items_message(self, only_up=False):
        self.update_button.configure(state="disabled")
        self.update_tooltip.configure(message="Updater Disabled, No items found")
        if only_up:
            return
        self.no_items_label.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="n")
        self.no_items_label.configure(text="No items found in the selected folder. \nMake sure you have a mod/map downloaded and or have the right game folder selected.")

    def hide_no_items_message(self):
        self.update_tooltip.configure(message="Check items for updates")
        self.update_button.configure(state="normal")
        self.no_items_label.configure(text="")
        self.no_items_label.forget()

    def show_map_info(self, workshop, folder, invalid_warn=False):
        for button_view in self.button_view_list:
            button_view.configure(state="disabled")

        def show_map_thread():
            workshop_id = workshop
            online = if_internet_available("return")
            valid_id = None

            if not workshop_id.isdigit():
                try:
                    if extract_workshop_id(workshop_id).strip().isdigit():
                        workshop_id = extract_workshop_id(workshop_id).strip()
                    else:
                        raise
                except:
                    valid_id = False
                    # show_message("Warning", "Not a valid Workshop ID.")
                    for button_view in self.button_view_list:
                        button_view.configure(state="normal")
                    # return

            json_path = Path(folder) / "zone" / "workshop.json"
            folder_size_bytes = get_folder_size(json_path.parent.parent)
            map_size = convert_bytes_to_readable(folder_size_bytes)

            if online and valid_id!=False:
                try:
                    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
                    response = requests.get(url)
                    response.raise_for_status()
                    content = response.text

                    soup = BeautifulSoup(content, "html.parser")

                    try:
                        type_txt = soup.find("div", class_="rightDetailsBlock").text.strip()
                        map_mod_type = type_txt if "File Size" not in type_txt else "Not specified"
                        map_name = soup.find("div", class_="workshopItemTitle").text.strip()
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
                        show_message("Warning", "Couldn't get information.")
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
                                            date_updated, stars_image, stars_image_size, ratings_text,
                                            url, workshop_id, invalid_warn, folder, description, online)

                except Exception as e:
                    show_message("Error", f"Failed to fetch information.\nError: {e}", icon="cancel")
                    for button_view in self.button_view_list:
                        button_view.configure(state="normal")
                    return
            else:
                creation_timestamp = None
                for ff_file in json_path.parent.glob("*.ff"):
                    if ff_file.exists():
                        creation_timestamp = ff_file.stat().st_mtime
                        break
                if not creation_timestamp:
                    creation_timestamp = json_path.parent.stat().st_mtime

                if json_path.exists():
                    workshop_id = extract_json_data(json_path, "PublisherID") or "None"
                    name = re.sub(r'\^\w+', '', extract_json_data(json_path, "Title")) or "None"
                    map_name = name[:60] + "..." if len(name) > 60 else name
                    map_mod_type = extract_json_data(json_path, "Type") or "None"
                    preview_iamge = json_path.parent / "previewimage.png"
                    if preview_iamge.exists():
                        image = Image.open(preview_iamge)
                    else:
                        image = Image.open(os.path.join(RESOURCES_DIR, "default_library_img.png"))
                    image_size = image.size
                    offline_date = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")
                    date_updated = "Offline"
                    date_created = "Offline"
                    stars_image = Image.open(os.path.join(RESOURCES_DIR, "ryuk.png"))
                    stars_image_size = stars_image.size
                    ratings_text = "Offline"
                    description = re.sub(r'\^\w+', '', extract_json_data(json_path, "Description")) or "Not available"
                    description = re.sub(r'\[.*?\]', '', description)
                    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"

                    self.toplevel_info_window(map_name, map_mod_type, map_size, image, image_size, date_created,
                                            date_updated, stars_image, stars_image_size, ratings_text,
                                            url, workshop_id, invalid_warn, folder, description, online ,offline_date)
                else:
                    show_message("Warning", "Couldn't get offline information, Please connect to internet and try again")
                    for button_view in self.button_view_list:
                        button_view.configure(state="normal")
                    return

        info_thread = threading.Thread(target=show_map_thread)
        info_thread.start()

    def toplevel_info_window(self, map_name, map_mod_type_txt, map_size, image, image_size,
                             date_created ,date_updated, stars_image, stars_image_size, ratings_text,
                             url, workshop_id, invalid_warn, folder, description ,online,offline_date=None):
        def main_thread():
            try:
                items_file = os.path.join(APPLICATION_PATH, LIBRARY_FILE)
                top = ctk.CTkToplevel(self)
                if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                    top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
                top.title("Map/Mod Information")
                _, _, x, y = get_window_size_from_registry()
                top.geometry(f"+{x+50}+{y-50}")
                top.maxsize(450, 10000)
                top.minsize(300, 500)
                # top.attributes('-topmost', 'true')

                if offline_date:
                    down_date = offline_date
                elif invalid_warn:
                    try:
                        zone_path = Path(folder) / "zone"
                        for ff_file in zone_path.glob("*.ff"):
                            if ff_file.exists():
                                creation_timestamp = ff_file.stat().st_mtime
                                break
                        down_date = datetime.fromtimestamp(creation_timestamp).strftime("%d %b, %Y @ %I:%M%p")
                    except:
                        down_date = "Failed to get download date"
                else:
                    down_date = self.get_item_by_id(items_file, workshop_id, 'date')

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

                        main_app.app.create_context_menu(description_label, textbox=True)
                        description_window.after(50, description_window.focus_set)

                    main_app.app.after(0, main_thread)

                def check_for_updates():
                    try:

                        if check_item_date(down_date, date_updated, format=True):
                            if show_message("There is an update.", "Press download to redownload!", icon="info", _return=True, option_1="No", option_2="Download"):
                                if main_app.app.is_downloading:
                                    show_message("Error", "Please wait for the current download to finish or stop it then restart.", icon="cancel")
                                    return
                                main_app.app.edit_workshop_id.delete(0, "end")
                                main_app.app.edit_workshop_id.insert(0, workshop_id)
                                main_app.app.main_button_event()
                                if invalid_warn and check_config("update_invalid", "off") == "on":
                                    main_app.app.download_map(update=True, invalid_item_folder=os.path.basename(folder))
                                else:
                                    main_app.app.download_map(update=True)
                                top.destroy()
                                return
                        else:
                            show_message("Up to date!", "No updates found!", icon="info")
                    except:
                        show_message("Up to date!", "No updates found!", icon="info")

                def show_full_text(event, widget, full_text):
                    widget_text = type_label.cget("text")
                    label_type = widget_text.split(':')[0]
                    # + 30 which is desc_threshold + 5 is the ... dots and a white space
                    if len(widget_text) == len(label_type) + 30 + 5:
                        widget.configure(text=f"{label_type}: {full_text}")
                    else:
                        widget.configure(text=f"{label_type}: {full_text[:30]}...")

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
                name_label = ctk.CTkLabel(info_frame, text=f"Name: {map_name}", wraplength=420, justify="left")
                name_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                desc_threshold = 30
                shortened_description = re.sub(r'[\\/\n\r]', '', description).strip()
                shortened_description = re.sub(r'([^a-zA-Z0-9\s:().])', '', shortened_description)
                shortened_description = f"{shortened_description[:desc_threshold]}... (View)"\
                                        if len(shortened_description) > desc_threshold else shortened_description
                description_lab = ctk.CTkLabel(info_frame, text=f"Description: {shortened_description}")
                description_lab.grid(row=1, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)
                if len(description) > desc_threshold:
                    description_lab_tooltip = CTkToolTip(description_lab, message="View description", topmost=True)
                    description_lab.configure(cursor="hand2")
                    description_lab.bind("<Button-1>", lambda e: show_description(e))

                id_label = ctk.CTkLabel(info_frame, text=f"ID: {workshop_id} | Folder: {os.path.basename(folder)}")
                id_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                map_mod_type = map_mod_type_txt[:desc_threshold] + "..." if len(map_mod_type_txt) > desc_threshold else map_mod_type_txt
                type_label = ctk.CTkLabel(info_frame, text=f"Type: {map_mod_type}", wraplength=350, justify="left")
                type_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)
                if len(map_mod_type) > desc_threshold:
                    type_label_tooltip = CTkToolTip(type_label, message="View all types", topmost=True)
                    type_label.configure(cursor="hand2")
                    type_label.bind("<Button-1>", lambda e: show_full_text(e, type_label, map_mod_type_txt))

                size_label = ctk.CTkLabel(info_frame, text=f"Size: {map_size}")
                size_label.grid(row=4, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                date_created_label = ctk.CTkLabel(info_frame, text=f"Posted: {date_created}")
                date_created_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                if date_updated != "Not updated" and date_updated != "Offline":
                    date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}  🔗")
                    date_updated_label_tooltip = CTkToolTip(date_updated_label, message="View changelogs", topmost=True)
                    date_updated_label.configure(cursor="hand2")
                    date_updated_label.bind("<Button-1>", lambda e:
                        webbrowser.open(f"https://steamcommunity.com/sharedfiles/filedetails/changelog/{workshop_id}"))
                else:
                    date_updated_label = ctk.CTkLabel(info_frame, text=f"Updated: {date_updated}")
                date_updated_label.grid(row=6, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                date_updated_label = ctk.CTkLabel(info_frame, text=f"Downloaded: {down_date}")
                date_updated_label.grid(row=7, column=0, columnspan=2, sticky="w", padx=20, pady=2.5)

                stars_image_label = ctk.CTkLabel(stars_frame)
                stars_width, stars_height = stars_image_size
                stars_image_widget = ctk.CTkImage(stars_image, size=(int(stars_width), int(stars_height)))
                stars_image_label.configure(image=stars_image_widget, text="")
                stars_image_label.pack(side="left", padx=(10, 20), pady=(10, 10))

                ratings = ctk.CTkLabel(stars_frame)
                ratings.configure(text=ratings_text)
                ratings.pack(side="right", padx=(10, 20), pady=(10, 10))

                image_label = ctk.CTkLabel(image_frame)
                max_width = 300
                i_width, i_height = tuple([int(max_width/image_size[0] * x)  for x in image_size])
                # preview image is too big if offline, // to round floats

                image_widget = ctk.CTkImage(image, size=(int(i_width), int(i_height)))
                image_label.configure(image=image_widget, text="")
                image_label.pack(expand=True, fill="both", padx=(10, 20), pady=(10, 10))

                # Buttons
                view_button = ctk.CTkButton(buttons_frame, text="View", command=view_map_mod, width=130)
                view_button.grid(row=0, column=0, padx=(20, 20), pady=(10, 10), sticky="n")
                view_button_tooltip = CTkToolTip(view_button, message="View Workshop", topmost=True)

                update_btn = ctk.CTkButton(buttons_frame, text="Update", command=check_for_updates, width=130)
                update_btn.grid(row=0, column=1, padx=(10, 20), pady=(10, 10), sticky="n")
                update_btn_tooltip = CTkToolTip(update_btn, message="Checks and installs updates of the current selected item (redownload!)", topmost=True)

                close_button = ctk.CTkButton(buttons_frame, text="Close", command=close_window, width=130)
                close_button.grid(row=0, column=2, padx=(10, 20), pady=(10, 10), sticky="n")

                if not online:
                    view_button.configure(state="disabled")
                    update_btn.configure(state="disabled")
                    update_btn_tooltip.configure(message="Currently offline")
                    view_button_tooltip.configure(message="Currently offline")
                if check_config("update_invalid", "off") == "on":
                    update_btn_tooltip.configure(message="update_invalid is set to 'on' in config.ini")
                elif invalid_warn:
                    update_btn.configure(text="Update", state="disabled")
                    update_btn_tooltip.configure(message="Disabled due to item being blocked or duplicated")

                if not workshop_id.isdigit():
                    view_button.configure(text="View", state="disabled")
                    view_button_tooltip.configure(message="Not a valid Workshop ID")

                top.grid_rowconfigure(0, weight=0)
                top.grid_rowconfigure(1, weight=0)
                top.grid_rowconfigure(2, weight=1)
                top.grid_columnconfigure(0, weight=1)
                top.grid_columnconfigure(1, weight=1)

                buttons_frame.grid_rowconfigure(0, weight=1)
                buttons_frame.grid_rowconfigure(1, weight=1)
                buttons_frame.grid_rowconfigure(2, weight=1)
                buttons_frame.grid_columnconfigure(0, weight=1)
                buttons_frame.grid_columnconfigure(1, weight=1)
                buttons_frame.grid_columnconfigure(2, weight=1)

            finally:
                top.after(10, top.focus_force)
                for button_view in self.button_view_list:
                    button_view.configure(state="normal")
        main_app.app.after(0, main_thread)

    def check_for_updates(self, on_launch=False):
        online = if_internet_available("return")
        if not online:
            if not on_launch:
                show_message(
                        "Offline", "No internet connection. Please check your internet connection and try again.")
            return
        self.after(1, self.update_button.configure(state="disabled"))
        self.update_tooltip.configure(message='Still loading please wait...')
        cevent = Event()
        cevent.x_root = self.update_button.winfo_rootx()
        cevent.y_root = self.update_button.winfo_rooty()
        if not on_launch:
            show_noti(self.update_button, "Please wait, window will popup shortly", event=cevent, noti_dur=3.0, topmost=True)
        threading.Thread(target=self.check_items_func, args=(on_launch,)).start()

    def items_update_message(self, to_update_len):
        def main_thread():
            if show_message(f"{to_update_len} Item updates available", f"{to_update_len} Workshop Items have an update, Would you like to open the item updater window?", icon="info", _return=True):
                main_app.app.after(1, self.update_items_window)
            else: return
        main_app.app.after(0, main_thread)
        self.update_button.configure(state="normal", width=65, height=20)
        self.update_tooltip.configure(message='Check items for updates')
        return

    def check_items_func(self, on_launch):
        # Needed to refresh item that needs updates
        self.to_update.clear()

        def if_ids_need_update(item_ids, item_dates, texts):
            try:
                item_data = get_item_dates(item_ids)

                for item_id, date_updated in item_data.items():
                    if not date_updated:
                        try:
                            new_date = get_update_time_from_html(item_id)
                            date_updated = new_date if new_date else 1
                        except:
                            date_updated = 1
                    item_date = item_dates[str(item_id)] if str(item_id) in item_dates else ""
                    date_updated = datetime.fromtimestamp(date_updated)

                    if check_item_date(item_date, date_updated):
                        if item_date != "":
                            date_updated = date_updated.strftime("%d %b @ %I:%M%p, %Y")
                            self.to_update.add(texts[item_id] + f" | Updated: {date_updated}")

            except Exception as e:
                show_message("Error", f"Error occurred\n{e}", icon="cancel")

        def check_for_update():
            try:
                lib_data = None

                if not os.path.exists(os.path.join(APPLICATION_PATH, LIBRARY_FILE)):
                    show_message("Error checking for item updates! -> Setting is on", "Please visit library tab at least once with the correct game path! You also need to have at least 1 item!")
                    return

                with open(os.path.join(APPLICATION_PATH, LIBRARY_FILE), 'r', encoding='utf-8', errors="ignore") as file:
                    lib_data = json.load(file)

                item_ids = [item["id"] for item in lib_data]
                item_dates = {item["id"]: item["date"] for item in lib_data}
                texts = {item["id"]: item["text"] for item in lib_data}

                if_ids_need_update(item_ids, item_dates, texts)

            except:
                show_message("Error checking for item updates!", "Please visit the library tab at least once with the correct game path! You also need to have at least 1 item!")
                return

        check_for_update()

        to_update_len = len(self.to_update)
        if to_update_len > 0:
            self.items_update_message(to_update_len)
        else:
            self.update_button.configure(state="normal", width=65, height=20)
            self.update_tooltip.configure(message='Check items for updates')
            if not on_launch:
                show_message("No updates found!", "Items are up to date!", icon="info")

    def update_items_window(self):
        try:
            top = ctk.CTkToplevel(master=None)
            top.withdraw()
            if os.path.exists(os.path.join(RESOURCES_DIR, "ryuk.ico")):
                top.after(210, lambda: top.iconbitmap(os.path.join(RESOURCES_DIR, "ryuk.ico")))
            top.title("Item updater - List of Items with Updates - Click to select 1 or more")
            longest_text_length = max(len(text) for text in self.to_update)
            window_height = len(self.to_update) * 70
            window_width = longest_text_length * 6 + 5
            _, _, x, y = get_window_size_from_registry()
            top.geometry(f"{window_width}x{window_height}+{x}+{y}")
            top.maxsize(window_width + 100, 450)
            top.minsize(window_width - 5, 250)
            top.resizable(True, True)
            selected_id_list = []
            cevent = Event()
            self.select_all_bool = False

            listbox = CTkListbox(top, multiple_selection=True)
            listbox.grid(row=0, column=0, sticky="nsew")

            update_button = ctk.CTkButton(top, text="Update")
            update_button.grid(row=1, column=0, pady=10, padx=5, sticky='ns')

            select_button = ctk.CTkButton(top, text="Select All", width=5)
            select_button.grid(row=1, column=0, pady=10, padx=(230, 0), sticky='ns')

            def open_url(id_part, e=None):
                url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={id_part}"
                webbrowser.open(url)

            # you gotta use my modded CTkListbox originaly by Akascape
            def add_checkbox_item(index, item_text):
                parts = item_text.split('ID: ')
                id_part = parts[1].split('|')[0].strip()
                listbox.insert(index, item_text, keybind="<Button-3>", func=lambda e: open_url(id_part))

            def load_items():
                for index, item_text in enumerate(self.to_update):
                    if index == len(self.to_update) - 1:
                        add_checkbox_item("end", item_text)
                        top.deiconify()
                        return
                    add_checkbox_item(index, item_text)

            def update_list(selected_option):
                selected_id_list.clear()

                if selected_option:
                    for option in selected_option:
                        parts = option.split('ID: ')
                        if len(parts) > 1:
                            id_part = parts[1].split('|')[0].strip()
                            selected_id_list.append(id_part)

            def select_all():
                if self.select_all_bool:
                    listbox.deactivate("all")
                    update_list(listbox.get())
                    self.select_all_bool = False
                    return
                listbox.deactivate("all")
                listbox.activate("all")
                update_list(listbox.get())
                self.select_all_bool = True

            def update_btn_fun():
                if len(selected_id_list) == 1:
                    if main_app.app.is_downloading:
                        show_message("Error", "Please wait for the current download to finish or stop it then start.", icon="cancel")
                        return
                    main_app.app.edit_workshop_id.delete(0, "end")
                    main_app.app.edit_workshop_id.insert(0, selected_id_list[0])
                    main_app.app.main_button_event()
                    main_app.app.download_map(update=True)
                    top.destroy()
                    return

                elif len(selected_id_list) > 1:
                    if main_app.app.is_downloading:
                        show_message("Error", "Please wait for the current download to finish or stop it then start.", icon="cancel")
                        return
                    comma_separated_ids = ",".join(selected_id_list)
                    main_app.app.queuetextarea.delete("1.0", "end")
                    main_app.app.queuetextarea.insert("1.0", comma_separated_ids)
                    main_app.app.queue_button_event()
                    main_app.app.download_map(update=True)
                    top.destroy()
                    return

                else:
                    cevent.x_root = update_button.winfo_rootx()
                    cevent.y_root = update_button.winfo_rooty()
                    show_noti(update_button ,"Please select 1 or more items", event=cevent, noti_dur=0.8, topmost=True)


            listbox.configure(command=update_list)
            update_button.configure(command=update_btn_fun)
            select_button.configure(command=select_all)

            top.grid_rowconfigure(0, weight=1)
            top.grid_columnconfigure(0, weight=1)

            load_items()

        except Exception as e:
            show_message("Error", f"{e}", icon="cancel")

        finally:
            main_app.app.after(150, lambda: top.focus_force())
            self.update_button.configure(state="normal", width=65, height=20)
            self.update_tooltip.configure(message='Check items for updates')
