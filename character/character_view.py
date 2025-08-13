import customtkinter as ctk

class CharacterView:
    """Manages the UI for the Character Creator and Character Sheet tabs."""
    def __init__(self, creator_tab, sheet_tab):
        self.creator_tab = creator_tab
        self.sheet_tab = sheet_tab
        self.char_creator_entries = {}
        self.char_sheet_entries = {}
        self.sheet_is_built = False # Flag to check if the recycled UI exists

    def setup_creator_ui(self, controller):
        """Builds the UI for the Character Creator tab."""
        # --- REFINED LAYOUT: Main container now expands ---
        container = ctk.CTkFrame(self.creator_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)
        
        ctk.CTkLabel(container, text="Create New Character", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        # --- REFINED LAYOUT: Added frame for outline and padding ---
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
        # --- REFINED LAYOUT: Main container now expands ---
        container = ctk.CTkFrame(self.sheet_tab, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        
        load_frame = ctk.CTkFrame(container)
        load_frame.grid(row=0, column=0, pady=(10, 20), padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load Character:").pack(side="left", padx=(10,10))
        self.char_sheet_list = ctk.CTkComboBox(load_frame, values=["-"], state="readonly")
        self.char_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(load_frame, text="Load", command=controller.load_character_to_sheet).pack(side="left", padx=(10,10))
        
        self.sheet_content_frame = ctk.CTkFrame(container, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        
    def build_dynamic_fields(self, rule_set):
        """Builds stat fields in the creator in a hidden container for smooth rendering."""
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
        
        inv_frame = ctk.CTkScrollableFrame(sheet_pane, label_text="Inventory")
        inv_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        all_stat_keys = rule_set['attributes'] + list(rule_set['skills'].keys())
        for key in all_stat_keys:
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.char_sheet_entries[key] = entry
            entry.bind("<KeyRelease>", controller.mark_as_dirty)
            
        self.inv_textbox = ctk.CTkTextbox(inv_frame)
        self.inv_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.inv_textbox.bind("<KeyRelease>", controller.mark_as_dirty)

        button_frame = ctk.CTkFrame(self.sheet_content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=10)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_character_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete Character", command=controller.delete_current_character, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)
        
        self.sheet_is_built = True

    def display_sheet_data(self, character):
        """Populates the existing UI with new data instead of rebuilding it."""
        if not self.sheet_is_built: return

        self.sheet_name_label.configure(text=character.name)
        
        for key, entry in self.char_sheet_entries.items():
            entry.delete(0, 'end')
            value = character.attributes.get(key) or character.skills.get(key) or ""
            entry.insert(0, value)

        self.inv_textbox.delete("1.0", "end")
        self.inv_textbox.insert("1.0", "\n".join([f"{item.get('name', 'N/A')}: {item.get('description', '')}" for item in character.inventory]))
        
        self.sheet_content_wrapper.pack(fill="both", expand=True)

    def clear_sheet(self):
        """Hides the main content wrapper instead of destroying widgets."""
        if hasattr(self, 'sheet_content_wrapper'):
            self.sheet_content_wrapper.pack_forget()

    def update_character_list(self, characters):
        """Updates the dropdown list of characters on the sheet tab."""
        characters = characters or ["-"]
        self.char_sheet_list.configure(values=characters)
        self.char_sheet_list.set(characters[0])