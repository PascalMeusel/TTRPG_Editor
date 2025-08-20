import customtkinter as ctk
from ui_extensions import AutoWidthComboBox
from quest.quest_controller import QuestController

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
    def __init__(self, parent_frame):
        self.frame = ctk.CTkTabview(parent_frame, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.creator_tab = self.frame.add("Creator")
        self.sheet_tab = self.frame.add("Sheet")
        
        self.char_creator_entries = {}
        self.char_sheet_entries = {}
        self.sheet_is_built = False

    def setup_ui(self, controller):
        self.setup_creator_ui(controller)
        self.setup_sheet_ui(controller)

    def setup_creator_ui(self, controller):
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
        container = ctk.CTkFrame(self.sheet_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        load_frame = ctk.CTkFrame(container)
        load_frame.grid(row=0, column=0, pady=(10, 20), padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load Character:").pack(side="left", padx=(10,10))
        self.char_sheet_list = AutoWidthComboBox(load_frame, values=["-"], state="readonly")
        self.char_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        self.char_sheet_list.bind("<Button-1>", lambda event: self.char_sheet_list._open_dropdown_menu())
        ctk.CTkButton(load_frame, text="Load", command=controller.load_character_to_sheet).pack(side="left", padx=(10,10))
        self.sheet_content_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        
    def build_dynamic_fields(self, rule_set):
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
        self.clear_sheet()
        self.char_sheet_entries.clear()
        self.sheet_content_wrapper = ctk.CTkFrame(self.sheet_content_frame, fg_color="transparent")
        self.sheet_content_wrapper.grid_columnconfigure((0, 1), weight=1)
        self.sheet_content_wrapper.grid_rowconfigure(1, weight=1)
        self.sheet_name_label = ctk.CTkLabel(self.sheet_content_wrapper, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.sheet_name_label.grid(row=0, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        
        stats_frame = ctk.CTkScrollableFrame(self.sheet_content_wrapper, label_text="Stats & Skills")
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        hp_frame = ctk.CTkFrame(stats_frame, fg_color="gray20")
        hp_frame.pack(fill="x", padx=5, pady=5)
        hp_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(hp_frame, text="Current HP:", anchor="w").grid(row=0, column=0, padx=5, pady=2)
        self.current_hp_entry = ctk.CTkEntry(hp_frame)
        self.current_hp_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        self.current_hp_entry.bind("<KeyRelease>", controller.mark_as_dirty)
        ctk.CTkLabel(hp_frame, text="Max HP:", anchor="w").grid(row=1, column=0, padx=5, pady=2)
        self.max_hp_label = ctk.CTkLabel(hp_frame, text="10", anchor="w")
        self.max_hp_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)

        right_column = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        right_column.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        right_column.grid_rowconfigure(1, weight=1)
        right_column.grid_rowconfigure(3, weight=1)
        
        inv_frame = ctk.CTkFrame(right_column)
        inv_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        inv_frame.grid_columnconfigure(0, weight=1)
        inv_frame.grid_rowconfigure(1, weight=1)
        inv_header_frame = ctk.CTkFrame(inv_frame, fg_color="transparent")
        inv_header_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        ctk.CTkLabel(inv_header_frame, text="Inventory", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(inv_header_frame, text="Add Item", width=80, command=controller.show_add_item_dialog).pack(side="right")
        self.inventory_list_frame = ctk.CTkScrollableFrame(inv_frame)
        self.inventory_list_frame.grid(row=1, column=0, sticky="nsew")

        quest_frame = ctk.CTkFrame(right_column)
        quest_frame.grid(row=2, column=0, rowspan=2, sticky="nsew", pady=(10, 0))
        quest_frame.grid_columnconfigure(0, weight=1)
        quest_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(quest_frame, text="Linked Quests", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.linked_quests_frame = ctk.CTkScrollableFrame(quest_frame, label_text="")
        self.linked_quests_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        
        all_stat_keys = rule_set['attributes'] + list(rule_set['skills'].keys())
        for key in all_stat_keys:
            if key == "Hit Points": continue
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.char_sheet_entries[key] = entry
            entry.bind("<KeyRelease>", controller.mark_as_dirty)

        button_frame = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_character_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete Character", command=controller.delete_current_character, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)
        self.sheet_is_built = True

    def display_sheet_data(self, character, item_controller, char_controller):
        if not self.sheet_is_built: return
        self.sheet_name_label.configure(text=character.name)
        
        effective_attrs = character.attributes.copy()
        
        # --- FIX: Check if item_controller exists before calculating stats ---
        if item_controller:
            all_items_data = {item['id']: item for item in item_controller.all_items}
            for inv_entry in character.inventory:
                if inv_entry.get("equipped", False):
                    item_id = inv_entry["item_id"]
                    if item_id in all_items_data:
                        item_details = all_items_data[item_id]
                        for modifier in item_details.get("modifiers", []):
                            stat = modifier["stat"]
                            value = modifier["value"]
                            if stat in effective_attrs:
                                try:
                                    current_val = int(effective_attrs.get(stat, 0))
                                    effective_attrs[stat] = str(current_val + value)
                                except ValueError: pass
        
        base_max_hp_str = character.attributes.get("Hit Points", "10")
        effective_max_hp_str = effective_attrs.get("Hit Points", base_max_hp_str)
        hp_display_text = base_max_hp_str
        if effective_max_hp_str != base_max_hp_str:
            hp_display_text = f"{effective_max_hp_str} ({base_max_hp_str})"
        self.max_hp_label.configure(text=hp_display_text)
        self.current_hp_entry.delete(0, 'end')
        self.current_hp_entry.insert(0, str(character.current_hp))
        
        for key, entry in self.char_sheet_entries.items():
            base_value = character.attributes.get(key) or character.skills.get(key) or ""
            effective_value = effective_attrs.get(key)
            display_text = base_value
            if effective_value and effective_value != base_value:
                 display_text = f"{effective_value} ({base_value})"
            entry.delete(0, 'end')
            entry.insert(0, display_text)
            
        quest_controller = char_controller.app_controller.get_loaded_controller(QuestController)
        self.display_linked_quests(character.name, quest_controller)
        self.display_inventory(character.inventory, item_controller, char_controller)
        self.sheet_content_wrapper.pack(fill="both", expand=True)

    def display_linked_quests(self, char_name, quest_controller):
        for widget in self.linked_quests_frame.winfo_children():
            widget.destroy()
            
        # --- FIX: Display a helpful message if the Quest pane isn't open ---
        if not quest_controller:
            ctk.CTkLabel(self.linked_quests_frame, text="Open 'Quests' pane\nto see links.", wraplength=150).pack(pady=10)
            return
            
        linked_quests = [q for q in quest_controller.get_all_quests() if char_name in q.get('linked_npcs', [])]
        if not linked_quests:
            ctk.CTkLabel(self.linked_quests_frame, text="Not linked to any quests.").pack(pady=10)
        else:
            for quest in linked_quests:
                quest_label = ctk.CTkLabel(self.linked_quests_frame, text=f"{quest['title']} ({quest['status']})", anchor="w")
                quest_label.pack(fill="x", pady=2)

    def display_inventory(self, inventory_list, item_controller, char_controller):
        for widget in self.inventory_list_frame.winfo_children():
            widget.destroy()
            
        # --- FIX: Display a helpful message if the Item pane isn't open ---
        if not item_controller:
            ctk.CTkLabel(self.inventory_list_frame, text="Open 'Items' pane\nto manage inventory.", wraplength=150).pack(pady=10)
            return

        all_items_data = {item['id']: item for item in item_controller.all_items}
        if not char_controller: return
        for inv_entry in inventory_list:
            item_id = inv_entry["item_id"]
            if item_id in all_items_data:
                item_details = all_items_data[item_id]
                item_row = ctk.CTkFrame(self.inventory_list_frame)
                item_row.pack(fill="x", pady=2)
                equip_checkbox = ctk.CTkCheckBox(item_row, text="", width=20,
                                                 command=lambda i=inv_entry: char_controller.toggle_item_equipped(i))
                equip_checkbox.pack(side="left", padx=5)
                if inv_entry.get("equipped", False):
                    equip_checkbox.select()
                else:
                    equip_checkbox.deselect()
                label_text = f'{item_details["name"]} (x{inv_entry["quantity"]})'
                ctk.CTkLabel(item_row, text=label_text, anchor="w").pack(side="left", expand=True, fill="x")
                ctk.CTkButton(item_row, text="X", width=25, height=25, fg_color="#D2691E", hover_color="#B2590E",
                              command=lambda i=inv_entry: char_controller.remove_item_from_inventory(i)).pack(side="right", padx=5)

    def clear_sheet(self):
        if hasattr(self, 'sheet_content_wrapper'):
            self.sheet_content_wrapper.pack_forget()

    def update_character_list(self, characters):
        values = ["-"] + (characters or [])
        self.char_sheet_list.configure(values=values)
        self.char_sheet_list.set(values[0])