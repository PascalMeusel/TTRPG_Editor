import customtkinter as ctk

class NpcView:
    """Manages the UI for the NPC creator, manager, and sheet tabs."""
    def __init__(self, creator_tab, sheet_tab):
        self.creator_tab = creator_tab
        self.sheet_tab = sheet_tab
        self.npc_creator_entries = {}
        self.npc_sheet_entries = {}

    def setup_ui(self, controller):
        """Builds all UI elements for both NPC tabs."""
        self._setup_creator_ui(controller)
        self.setup_sheet_ui(controller)

    def _setup_creator_ui(self, controller):
        tab = self.creator_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(tab, text="Create & Manage NPCs", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20, padx=20)
        main_pane = ctk.CTkFrame(tab, fg_color="transparent")
        main_pane.pack(fill="both", expand=True, padx=20)
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
        gm_fields_frame.grid_columnconfigure((0,1), weight=1)
        ctk.CTkLabel(gm_fields_frame, text="GM Notes:", anchor="w").grid(row=0, column=0, sticky="w")
        self.npc_notes_text = ctk.CTkTextbox(gm_fields_frame, height=80)
        self.npc_notes_text.grid(row=1, column=0, sticky="ew", padx=(0,5))
        ctk.CTkLabel(gm_fields_frame, text="Loot (one per line):", anchor="w").grid(row=0, column=1, sticky="w", padx=(5,0))
        self.npc_loot_text = ctk.CTkTextbox(gm_fields_frame, height=80)
        self.npc_loot_text.grid(row=1, column=1, sticky="ew", padx=(5,0))
        ctk.CTkButton(create_frame, text="Save NPC", command=controller.save_new_npc).grid(row=4, column=0, pady=10)
        manage_frame = ctk.CTkFrame(main_pane)
        manage_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(manage_frame, text="Existing NPCs", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        self.npc_management_list = ctk.CTkTextbox(manage_frame)
        self.npc_management_list.pack(fill="both", expand=True, padx=10)
        self.npc_management_list.bind("<Button-1>", controller.on_npc_select)
        ctk.CTkButton(manage_frame, text="Delete Selected NPC", command=controller.delete_selected_npc, fg_color="#D2691E", hover_color="#B2590E").pack(pady=10)

    def setup_sheet_ui(self, controller):
        """Builds the UI for the NPC Sheet viewer tab."""
        tab = self.sheet_tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1)
        load_frame = ctk.CTkFrame(tab)
        load_frame.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        ctk.CTkLabel(load_frame, text="Load NPC:").pack(side="left", padx=(10,10))
        self.npc_sheet_list = ctk.CTkComboBox(load_frame, values=["-"], state="readonly")
        self.npc_sheet_list.pack(side="left", padx=5, fill="x", expand=True)
        ctk.CTkButton(load_frame, text="Load", command=controller.load_npc_to_sheet).pack(side="left", padx=(10,10))
        self.sheet_content_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.sheet_content_frame.grid(row=1, column=0, pady=10, padx=20, sticky="nsew")

    def build_dynamic_fields(self, rule_set):
        """Builds stat fields in a hidden container first for smooth rendering."""
        for widget in self.npc_creator_fields_frame.winfo_children():
            widget.destroy()
        self.npc_creator_entries.clear()

        # --- FIX: Build in a temporary container ---
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
            
        # --- FIX: Show the container all at once ---
        container.pack(fill="both", expand=True)

    def update_npc_management_list(self, npcs):
        self.npc_management_list.configure(state="normal")
        self.npc_management_list.delete("1.0", "end")
        if npcs:
            for npc in npcs: self.npc_management_list.insert("end", f"{npc}\n")
        self.npc_management_list.configure(state="disabled")
        
    def update_npc_sheet_list(self, npcs):
        npcs = npcs or ["-"]
        self.npc_sheet_list.configure(values=npcs)
        self.npc_sheet_list.set(npcs[0])

    def highlight_selection(self):
        self.npc_management_list.tag_remove("selected", "1.0", "end")
        self.npc_management_list.tag_add("selected", "current linestart", "current lineend")
        self.npc_management_list.tag_config("selected", background="#343638", foreground="#DCE4EE")

    def clear_sheet(self):
        for widget in self.sheet_content_frame.winfo_children():
            widget.destroy()

    def display_sheet_data(self, npc, controller):
        """Populates the NPC sheet UI in a hidden container for smooth rendering."""
        self.clear_sheet()
        self.npc_sheet_entries.clear()

        # --- FIX: Build all widgets in this temporary wrapper first ---
        content_wrapper = ctk.CTkFrame(self.sheet_content_frame, fg_color="transparent")
        content_wrapper.grid_columnconfigure(0, weight=1)
        content_wrapper.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(content_wrapper, text=npc.name, font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, pady=5)
        
        sheet_pane = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        sheet_pane.grid(row=1, column=0, pady=10, sticky="nsew")
        sheet_pane.grid_columnconfigure(0, weight=1)
        sheet_pane.grid_rowconfigure(0, weight=1)
        
        stats_frame = ctk.CTkScrollableFrame(sheet_pane, label_text="Stats & Skills")
        stats_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        gm_pane = ctk.CTkFrame(sheet_pane, fg_color="transparent")
        gm_pane.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        gm_pane.grid_rowconfigure(1, weight=1)
        gm_pane.grid_rowconfigure(3, weight=1)
        
        for key, value in {**npc.attributes, **npc.skills}.items():
            frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
            frame.pack(fill="x", padx=5, pady=4)
            ctk.CTkLabel(frame, text=key, width=150, anchor="w").pack(side="left")
            entry = ctk.CTkEntry(frame)
            entry.insert(0, value)
            entry.pack(side="left", fill="x", expand=True)
            self.npc_sheet_entries[key] = entry

        ctk.CTkLabel(gm_pane, text="GM Notes", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", pady=(0,5))
        self.sheet_notes_text = ctk.CTkTextbox(gm_pane)
        self.sheet_notes_text.grid(row=1, column=0, sticky="nsew")
        self.sheet_notes_text.insert("1.0", npc.gm_notes)

        ctk.CTkLabel(gm_pane, text="Loot", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", pady=(10,5))
        self.sheet_loot_text = ctk.CTkTextbox(gm_pane)
        self.sheet_loot_text.grid(row=3, column=0, sticky="nsew")
        self.sheet_loot_text.insert("1.0", "\n".join(npc.loot))

        button_frame = ctk.CTkFrame(content_wrapper, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=20)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_npc_sheet).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Delete NPC", command=controller.delete_current_npc, fg_color="#D2691E", hover_color="#B2590E").pack(side="left", padx=10)

        # --- FIX: Make the fully built UI visible all at once ---
        content_wrapper.pack(fill="both", expand=True)