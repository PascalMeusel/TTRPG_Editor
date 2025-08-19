import customtkinter as ctk
from character.character_view import AddItemDialog
from ui_extensions import AutoWidthComboBox

class NpcView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.tab_view = ctk.CTkTabview(parent_frame, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        self.creator_tab = self.tab_view.add("Creator")
        self.sheet_tab = self.tab_view.add("Sheet")
        self.npc_creator_entries = {}
        self.npc_sheet_entries = {}
        self.sheet_is_built = False

    def setup_ui(self, controller):
        self._setup_creator_ui(controller)
        self.setup_sheet_ui(controller)

    def _setup_creator_ui(self, controller):
        # ... (This method is unchanged) ...
        container = ctk.CTkFrame(self.creator_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(container, text="Create & Manage NPCs", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=20, padx=20)
        main_pane = ctk.CTkFrame(container, fg_color="transparent")
        main_pane.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        main_pane.grid_columnconfigure(0, weight=2)
        main_pane.grid_columnconfigure(1, weight=1)
        main_pane.grid_rowconfigure(0, weight=1)
        create_frame = ctk.CTkFrame(main_pane)
        create_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        create_frame.grid_columnconfigure(0, weight=1)
        create_frame.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(create_frame, text="Create New NPC", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, pady=10)
        name_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        name_frame.grid(row=1, column=0, pady=5, padx=10, sticky="new")
        ctk.CTkLabel(name_frame, text="NPC Name:", anchor="w").pack(side="left", padx=5)
        self.npc_name_entry = ctk.CTkEntry(name_frame)
        self.npc_name_entry.pack(side="left", fill="x", expand=True)
        self.npc_creator_fields_frame = ctk.CTkScrollableFrame(create_frame)
        self.npc_creator_fields_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        gm_fields_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        gm_fields_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")
        gm_fields_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(gm_fields_frame, text="GM Notes:", anchor="w").grid(row=0, column=0, sticky="w")
        self.npc_notes_text = ctk.CTkTextbox(gm_fields_frame, height=80)
        self.npc_notes_text.grid(row=1, column=0, sticky="ew", padx=(0, 5))
        ctk.CTkLabel(gm_fields_frame, text="Generated Items:", anchor="w").grid(row=0, column=1, sticky="w", padx=(5,0))
        self.generated_items_list = ctk.CTkTextbox(gm_fields_frame, height=80, state="disabled", fg_color="gray20")
        self.generated_items_list.grid(row=1, column=1, sticky="ew", padx=(5, 0))
        creator_button_frame = ctk.CTkFrame(create_frame, fg_color="transparent")
        creator_button_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")
        creator_button_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(creator_button_frame, text="Save NPC", command=controller.save_new_npc).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        ctk.CTkButton(creator_button_frame, text="Generate Random", command=controller.generate_random_npc).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        manage_frame = ctk.CTkFrame(main_pane)
        manage_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(manage_frame, text="Existing NPCs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.npc_management_list = AutoWidthComboBox(manage_frame, state="readonly")
        self.npc_management_list.pack(fill="x", padx=10, pady=5)
        self.npc_management_list.bind("<Button-1>", lambda event: self.npc_management_list._open_dropdown_menu())
        ctk.CTkButton(manage_frame, text="Delete Selected NPC", command=controller.delete_selected_npc, fg_color="#D2691E", hover_color="#B2590E").pack(pady=10)

    def populate_creator_fields(self, npc_data):
        self.npc_name_entry.delete(0, 'end')
        self.npc_name_entry.insert(0, npc_data["name"])
        for key, entry in self.npc_creator_entries.items():
            entry.delete(0, 'end')
            if key in npc_data["stats"]:
                entry.insert(0, npc_data["stats"][key])
        self.npc_notes_text.delete("1.0", "end")
        self.npc_notes_text.insert("1.0", npc_data["gm_notes"])
        self.generated_items_list.configure(state="normal")
        self.generated_items_list.delete("1.0", "end")
        item_names = [item['name'] for item in npc_data.get("items_to_create", [])]
        self.generated_items_list.insert("1.0", "\n".join(item_names))
        self.generated_items_list.configure(state="disabled")

    def clear_creator_fields(self):
        self.npc_name_entry.delete(0, 'end')
        for entry in self.npc_creator_entries.values():
            entry.delete(0, 'end')
        self.npc_notes_text.delete("1.0", "end")
        self.generated_items_list.configure(state="normal")
        self.generated_items_list.delete("1.0", "end")
        self.generated_items_list.configure(state="disabled")

    def setup_sheet_ui(self, controller):
        container = ctk.CTkFrame(self.sheet_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        load_frame = ctk.CTkFrame(container)
        load_frame.grid(row=0, column=0, pady=(10, 20), padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load NPC:").pack(side="left", padx=(10,10))
        self.npc_sheet_list = AutoWidthComboBox(load_frame, values=["-"], state="readonly")
        self.npc_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        self.npc_sheet_list.bind("<Button-1>", lambda event: self.npc_sheet_list._open_dropdown_menu())
        ctk.CTkButton(load_frame, text="Load", command=controller.load_npc_to_sheet).pack(side="left", padx=(10,10))
        self.sheet_content_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")

    def build_dynamic_fields(self, rule_set):
        for widget in self.npc_creator_fields_frame.winfo_children():
            widget.destroy()
        self.npc_creator_entries.clear()
        container = ctk.CTkFrame(self.npc_creator_fields_frame, fg_color="transparent")
        ctk.CTkLabel(container, text="Attributes", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5), padx=5)
        for attr in rule_set['attributes']:
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=attr, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.npc_creator_entries[attr] = entry
        ctk.CTkLabel(container, text="Skills", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10,5), padx=5)
        for skill, base_attr in rule_set['skills'].items():
            frame = ctk.CTkFrame(container, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            label = f"{skill} ({base_attr[:3]})"
            ctk.CTkLabel(frame, text=label, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.npc_creator_entries[skill] = entry
        container.pack(fill="both", expand=True)

    def build_sheet_ui(self, rule_set, controller):
        self.clear_sheet()
        self.npc_sheet_entries.clear()
        self.sheet_content_wrapper = ctk.CTkFrame(self.sheet_content_frame, fg_color="transparent")
        self.sheet_content_wrapper.grid_columnconfigure((0,1), weight=1)
        self.sheet_content_wrapper.grid_rowconfigure(1, weight=1)
        self.sheet_name_label = ctk.CTkLabel(self.sheet_content_wrapper, text="", font=ctk.CTkFont(size=20, weight="bold"))
        self.sheet_name_label.grid(row=0, column=0, columnspan=2, pady=5, sticky="w", padx=10)
        
        stats_frame = ctk.CTkScrollableFrame(self.sheet_content_wrapper, label_text="Stats & Skills")
        stats_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        
        # Dedicated HP section
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

        gm_pane = ctk.CTkFrame(self.sheet_content_wrapper)
        gm_pane.grid(row=1, column=1, sticky="nsew", padx=(10, 0))
        gm_pane.grid_columnconfigure(0, weight=1)
        gm_pane.grid_rowconfigure(1, weight=2)
        gm_pane.grid_rowconfigure(3, weight=1)
        
        all_stat_keys = rule_set['attributes'] + list(rule_set['skills'].keys())
        for key in all_stat_keys:
            if key == "Hit Points": continue
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.npc_sheet_entries[key] = entry
            entry.bind("<KeyRelease>", controller.mark_as_dirty)
        ctk.CTkLabel(gm_pane, text="GM Notes", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        self.sheet_notes_text = ctk.CTkTextbox(gm_pane)
        self.sheet_notes_text.grid(row=1, column=0, sticky="nsew")
        self.sheet_notes_text.bind("<KeyRelease>", controller.mark_as_dirty)
        inv_header_frame = ctk.CTkFrame(gm_pane, fg_color="transparent")
        inv_header_frame.grid(row=2, column=0, sticky="ew", pady=(10,5))
        ctk.CTkLabel(inv_header_frame, text="Inventory / Loot", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")
        ctk.CTkButton(inv_header_frame, text="Add Item", width=80, command=controller.show_add_item_dialog).pack(side="right")
        self.inventory_list_frame = ctk.CTkScrollableFrame(gm_pane)
        self.inventory_list_frame.grid(row=3, column=0, sticky="nsew")
        button_frame = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_npc_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete NPC", command=controller.delete_current_npc, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)
        self.sheet_is_built = True

    def display_sheet_data(self, npc, item_controller, npc_controller):
        if not self.sheet_is_built: return
        self.sheet_name_label.configure(text=npc.name)
        all_items_data = {item['id']: item for item in item_controller.all_items}
        effective_attrs = npc.attributes.copy()
        for inv_entry in npc.inventory:
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
        
        base_max_hp_str = npc.attributes.get("Hit Points", "10")
        effective_max_hp_str = effective_attrs.get("Hit Points", base_max_hp_str)
        hp_display_text = base_max_hp_str
        if effective_max_hp_str != base_max_hp_str:
            hp_display_text = f"{effective_max_hp_str} ({base_max_hp_str})"
        self.max_hp_label.configure(text=hp_display_text)
        self.current_hp_entry.delete(0, 'end')
        self.current_hp_entry.insert(0, str(npc.current_hp))
        
        for key, entry in self.npc_sheet_entries.items():
            base_value = npc.attributes.get(key) or npc.skills.get(key) or ""
            effective_value = effective_attrs.get(key)
            display_text = base_value
            if effective_value and effective_value != base_value:
                 display_text = f"{effective_value} ({base_value})"
            entry.delete(0, 'end')
            entry.insert(0, display_text)
        self.sheet_notes_text.delete("1.0", "end")
        self.sheet_notes_text.insert("1.0", npc.gm_notes)
        self.display_inventory(npc.inventory, item_controller, npc_controller)
        self.sheet_content_wrapper.pack(fill="both", expand=True)

    def display_inventory(self, inventory_list, item_controller, npc_controller):
        for widget in self.inventory_list_frame.winfo_children():
            widget.destroy()
        all_items_data = {item['id']: item for item in item_controller.all_items}
        if not npc_controller: return
        for inv_entry in inventory_list:
            item_id = inv_entry["item_id"]
            if item_id in all_items_data:
                item_details = all_items_data[item_id]
                item_row = ctk.CTkFrame(self.inventory_list_frame)
                item_row.pack(fill="x", pady=2)
                equip_checkbox = ctk.CTkCheckBox(item_row, text="", width=20,
                                                 command=lambda i=inv_entry: npc_controller.toggle_item_equipped(i))
                equip_checkbox.pack(side="left", padx=5)
                if inv_entry.get("equipped", False):
                    equip_checkbox.select()
                else:
                    equip_checkbox.deselect()
                label_text = f'{item_details["name"]} (x{inv_entry["quantity"]})'
                ctk.CTkLabel(item_row, text=label_text, anchor="w").pack(side="left", expand=True, fill="x")
                ctk.CTkButton(item_row, text="X", width=25, height=25, fg_color="#D2691E", hover_color="#B2590E",
                              command=lambda i=inv_entry: npc_controller.remove_item_from_inventory(i)).pack(side="right", padx=5)

    def clear_sheet(self):
        if hasattr(self, 'sheet_content_wrapper'):
            self.sheet_content_wrapper.pack_forget()

    def update_npc_management_list(self, npcs):
        values = ["-"] + (npcs or [])
        self.npc_management_list.configure(values=values)
        self.npc_management_list.set(values[0])
        
    def update_npc_sheet_list(self, npcs):
        values = ["-"] + (npcs or [])
        self.npc_sheet_list.configure(values=values)
        self.npc_sheet_list.set(values[0])

    def highlight_selection(self):
        pass