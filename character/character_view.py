import customtkinter as ctk

class AddItemDialog(ctk.CTkToplevel):
    """A reusable modal dialog for adding an item from a master list."""
    def __init__(self, parent, all_items):
        super().__init__(parent)
        self.title("Add Item to Inventory")
        self.geometry("400x500")
        self.configure(fg_color="#2B2B2B")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.selected_item = None
        self.buttons = []

        ctk.CTkLabel(self, text="Select an Item to Add", font=ctk.CTkFont(size=16)).pack(pady=10)
        
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        if not all_items:
            ctk.CTkLabel(self.scroll_frame, text="No items created in this campaign yet.").pack()
        else:
            for item in all_items:
                btn = ctk.CTkButton(self.scroll_frame, text=f'{item["name"]} ({item["type"]})',
                                    command=lambda i=item: self._select(i), 
                                    fg_color="transparent", anchor="w", border_width=1, border_color="gray50")
                btn.pack(fill="x", pady=2)
                self.buttons.append((btn, item))

        self.confirm_button = ctk.CTkButton(self, text="Add Selected Item", command=self._on_confirm, state="disabled")
        self.confirm_button.pack(pady=10)

        self.transient(parent)
        self.update_idletasks()
        self.grab_set()
        self.wait_window()

    def _select(self, item):
        self.selected_item = item
        self.confirm_button.configure(state="normal")
        for btn, btn_item in self.buttons:
            if btn_item["id"] == item["id"]:
                btn.configure(fg_color="#3B8ED0", border_color="#3B8ED0")
            else:
                btn.configure(fg_color="transparent", border_color="gray50")

    def _on_confirm(self):
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self.selected_item = None
        self.grab_release()
        self.destroy()

    def get_selection(self):
        return self.selected_item

class CharacterView:
    """Manages the UI for the Character Creator and Character Sheet tabs."""
    def __init__(self, creator_tab, sheet_tab):
        self.creator_tab = creator_tab
        self.sheet_tab = sheet_tab
        self.char_creator_entries = {}
        self.char_sheet_entries = {}
        self.sheet_is_built = False

    def setup_creator_ui(self, controller):
        """Builds the UI for the Character Creator tab."""
        container = ctk.CTkFrame(self.creator_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(container, text="Create New Character", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        name_frame = ctk.CTkFrame(container)
        name_frame.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(name_frame, text="Character Name:", width=150, anchor="w").pack(side="left", padx=10, pady=5)
        self.char_name_entry = ctk.CTkEntry(name_frame)
        self.char_name_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=5)
        
        self.char_creator_fields_frame = ctk.CTkScrollableFrame(container, label_text="Stats")
        self.char_creator_fields_frame.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        
        ctk.CTkButton(container, text="Save Character", height=40, command=controller.save_new_character).grid(row=3, column=0, pady=20)

    def setup_sheet_ui(self, controller):
        """Builds the static parts of the sheet tab."""
        container = ctk.CTkFrame(self.sheet_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        load_frame = ctk.CTkFrame(container)
        load_frame.grid(row=0, column=0, pady=(10, 20), padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load Character:").pack(side="left", padx=(10,10))
        self.char_sheet_list = ctk.CTkComboBox(load_frame, values=["-"], state="readonly")
        self.char_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- FIX: Bind left-click on the entire widget to open the dropdown ---
        self.char_sheet_list.bind("<Button-1>", lambda event: self.char_sheet_list._open_dropdown_menu())

        ctk.CTkButton(load_frame, text="Load", command=controller.load_character_to_sheet).pack(side="left", padx=(10,10))
        
        self.sheet_content_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        
    def build_dynamic_fields(self, rule_set):
        """Builds stat fields in the creator."""
        for widget in self.char_creator_fields_frame.winfo_children():
            widget.destroy()
        self.char_creator_entries.clear()

        container = ctk.CTkFrame(self.char_creator_fields_frame, fg_color="transparent")

        ctk.CTkLabel(container, text="Attributes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5), padx=5)
        for attr in rule_set['attributes']:
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=attr, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.char_creator_entries[attr] = entry
            
        ctk.CTkLabel(container, text="Skills", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5), padx=5)
        for skill, base_attr in rule_set['skills'].items():
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            label = f"{skill} ({base_attr[:3]})"
            ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.char_creator_entries[skill] = entry
            
        container.pack(fill="both", expand=True)

    def build_sheet_ui(self, rule_set, controller):
        """Builds the recyclable sheet UI ONCE when a ruleset is loaded."""
        self.clear_sheet()
        self.char_sheet_entries.clear()

        self.sheet_content_wrapper = ctk.CTkFrame(self.sheet_content_frame, fg_color="transparent")
        self.sheet_content_wrapper.grid_columnconfigure(0, weight=1)
        self.sheet_content_wrapper.grid_rowconfigure(1, weight=1)

        self.sheet_name_label = ctk.CTkLabel(self.sheet_content_wrapper, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.sheet_name_label.grid(row=0, column=0, pady=5)
        
        sheet_pane = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        sheet_pane.grid(row=1, column=0, pady=10, sticky="nsew")
        sheet_pane.grid_columnconfigure((0, 1), weight=1)
        sheet_pane.grid_rowconfigure(0, weight=1)
        
        stats_frame = ctk.CTkScrollableFrame(sheet_pane, label_text="Stats & Skills")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        inv_frame = ctk.CTkFrame(sheet_pane)
        inv_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        inv_frame.grid_rowconfigure(1, weight=1)
        
        inv_header_frame = ctk.CTkFrame(inv_frame, fg_color="transparent")
        inv_header_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        ctk.CTkLabel(inv_header_frame, text="Inventory", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(inv_header_frame, text="Add Item", width=80, command=controller.show_add_item_dialog).pack(side="right")
        
        self.inventory_list_frame = ctk.CTkScrollableFrame(inv_frame)
        self.inventory_list_frame.grid(row=1, column=0, sticky="nsew")
        
        all_stat_keys = rule_set['attributes'] + list(rule_set['skills'].keys())
        for key in all_stat_keys:
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.char_sheet_entries[key] = entry
            entry.bind("<KeyRelease>", controller.mark_as_dirty)

        button_frame = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=10)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_character_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete Character", command=controller.delete_current_character, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)
        
        self.sheet_is_built = True

    def display_sheet_data(self, character, item_controller):
        """Populates the existing UI with new data, including calculated stats."""
        if not self.sheet_is_built: return

        self.sheet_name_label.configure(text=character.name)
        
        all_items_data = {item['id']: item for item in item_controller.all_items}
        effective_attrs = character.attributes.copy()
        
        for inv_entry in character.inventory:
            if inv_entry.get("equipped", False):
                item_id = inv_entry["item_id"]
                if item_id in all_items_data:
                    item_details = all_items_data[item_id]
                    for modifier in item_details.get("modifiers", []):
                        stat = modifier["stat"]
                        value = modifier["value"]
                        if stat in effective_attrs:
                            current_val = int(effective_attrs.get(stat, 0))
                            effective_attrs[stat] = str(current_val + value)

        for key, entry in self.char_sheet_entries.items():
            entry.delete(0, 'end')
            base_value = character.attributes.get(key) or character.skills.get(key) or ""
            effective_value = effective_attrs.get(key)
            
            display_text = base_value
            if effective_value and effective_value != base_value:
                 display_text = f"{effective_value} ({base_value})"
            
            entry.insert(0, display_text)

        self.display_inventory(character.inventory, item_controller)
        self.sheet_content_wrapper.pack(fill="both", expand=True)

    def display_inventory(self, inventory_list, item_controller):
        """Renders the character's inventory in the UI with an equipped checkbox."""
        for widget in self.inventory_list_frame.winfo_children():
            widget.destroy()

        all_items_data = {item['id']: item for item in item_controller.all_items}
        controller = item_controller.app_controller.character_controller

        for inv_entry in inventory_list:
            item_id = inv_entry["item_id"]
            if item_id in all_items_data:
                item_details = all_items_data[item_id]
                item_row = ctk.CTkFrame(self.inventory_list_frame)
                item_row.pack(fill="x", pady=2)
                
                equip_checkbox = ctk.CTkCheckBox(item_row, text="", width=20,
                                                 command=lambda i=inv_entry: controller.toggle_item_equipped(i))
                equip_checkbox.pack(side="left", padx=5)
                if inv_entry.get("equipped", False):
                    equip_checkbox.select()
                else:
                    equip_checkbox.deselect()

                label_text = f'{item_details["name"]} (x{inv_entry["quantity"]})'
                ctk.CTkLabel(item_row, text=label_text, anchor="w").pack(side="left", expand=True, fill="x")
                ctk.CTkButton(item_row, text="X", width=25, height=25, fg_color="#D2691E", hover_color="#B2590E",
                              command=lambda i=inv_entry: controller.remove_item_from_inventory(i)).pack(side="right", padx=5)

    def clear_sheet(self):
        """Hides the main content wrapper."""
        if hasattr(self, 'sheet_content_wrapper'):
            self.sheet_content_wrapper.pack_forget()

    def update_character_list(self, characters):
        """Updates the dropdown list of characters on the sheet tab."""
        characters = ["-"] + characters if characters else ["-"]
        self.char_sheet_list.configure(values=characters)
        self.char_sheet_list.set(characters[0])