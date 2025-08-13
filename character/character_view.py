import customtkinter as ctk

class CharacterView:
    """Manages the UI for the Character Creator and Character Sheet tabs."""
    def __init__(self, creator_tab, sheet_tab):
        self.creator_tab = creator_tab
        self.sheet_tab = sheet_tab
        self.char_creator_entries = {}
        self.char_sheet_entries = {}

    def setup_creator_ui(self, controller):
        tab = self.creator_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(2, weight=1)
        ctk.CTkLabel(tab, text="Create New Character", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        name_frame = ctk.CTkFrame(tab, fg_color="transparent")
        name_frame.grid(row=1, column=0, pady=5, padx=20, sticky="ew")
        ctk.CTkLabel(name_frame, text="Character Name:", width=150, anchor="w").pack(side="left")
        self.char_name_entry = ctk.CTkEntry(name_frame)
        self.char_name_entry.pack(side="left", fill="x", expand=True)
        self.char_creator_fields_frame = ctk.CTkScrollableFrame(tab, label_text="Stats")
        self.char_creator_fields_frame.grid(row=2, column=0, pady=10, padx=20, sticky="nsew")
        ctk.CTkButton(tab, text="Save Character", command=controller.save_new_character).grid(row=3, column=0, pady=20)

    def setup_sheet_ui(self, controller):
        tab = self.sheet_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        load_frame = ctk.CTkFrame(tab)
        load_frame.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load Character:").pack(side="left", padx=(10,10))
        self.char_sheet_list = ctk.CTkComboBox(load_frame, values=["-"], state="readonly")
        self.char_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(load_frame, text="Load", command=controller.load_character_to_sheet).pack(side="left", padx=(10,10))
        self.sheet_content_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")
        
    def build_dynamic_fields(self, rule_set):
        """Builds stat fields in a hidden container first for smooth rendering."""
        # Clear old widgets
        for widget in self.char_creator_fields_frame.winfo_children():
            widget.destroy()
        self.char_creator_entries.clear()

        # --- FIX: Build in a temporary container ---
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
            
        # --- FIX: Show the container all at once ---
        container.pack(fill="both", expand=True)


    def update_character_list(self, characters):
        characters = characters or ["-"]
        self.char_sheet_list.configure(values=characters)
        self.char_sheet_list.set(characters[0])

    def clear_sheet(self):
        for widget in self.sheet_content_frame.winfo_children():
            widget.destroy()

    def display_sheet_data(self, character, controller):
        """Builds the character sheet UI in a hidden container for smooth rendering."""
        self.clear_sheet()
        self.char_sheet_entries.clear()
        
        # --- FIX: Build all widgets in this temporary wrapper first ---
        content_wrapper = ctk.CTkFrame(self.sheet_content_frame, fg_color="transparent")
        content_wrapper.grid_columnconfigure(0, weight=1)
        content_wrapper.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(content_wrapper, text=character.name, font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)
        
        sheet_pane = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        sheet_pane.grid(row=1, column=0, pady=10, sticky="nsew")
        sheet_pane.grid_columnconfigure((0, 1), weight=1)
        sheet_pane.grid_rowconfigure(0, weight=1)
        
        stats_frame = ctk.CTkScrollableFrame(sheet_pane, label_text="Stats & Skills")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        inv_frame = ctk.CTkScrollableFrame(sheet_pane, label_text="Inventory")
        inv_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        
        for key, value in {**character.attributes, **character.skills}.items():
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True)
            self.char_sheet_entries[key] = entry
            
        self.inv_textbox = ctk.CTkTextbox(inv_frame)
        self.inv_textbox.pack(fill="both", expand=True, padx=5, pady=5)
        for item in character.inventory:
            self.inv_textbox.insert("end", f"{item.get('name', 'N/A')}: {item.get('description', '')}\n")
        
        button_frame = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=10)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_character_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete Character", command=controller.delete_current_character, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)
        
        # --- FIX: Make the fully built UI visible all at once ---
        content_wrapper.pack(fill="both", expand=True)