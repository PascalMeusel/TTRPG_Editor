import customtkinter as ctk

class RulesView:
    """Manages the UI for both the rule set selection panel and the creation tab."""
    def __init__(self, left_panel_frame, creation_tab_frame):
        self.left_panel_frame = left_panel_frame
        self.creation_tab_frame = creation_tab_frame

    def setup_ui(self, controller):
        # --- Setup Left Panel (Selection) ---
        rules_frame = ctk.CTkFrame(self.left_panel_frame)
        rules_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(rules_frame, text="Game Rule Sets", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 0))
        
        status_frame = ctk.CTkFrame(rules_frame, fg_color="transparent")
        status_frame.pack(fill="x", padx=10, pady=(0, 5))
        ctk.CTkLabel(status_frame, text="Current:", font=ctk.CTkFont(size=12, weight="normal")).pack(side="left")
        self.status_label = ctk.CTkLabel(status_frame, text="None", font=ctk.CTkFont(size=12, weight="bold"))
        self.status_label.pack(side="left", padx=4)

        self.rule_set_listbox = ctk.CTkTextbox(rules_frame, height=150)
        self.rule_set_listbox.pack(pady=5, padx=10, fill="x")
        self.rule_set_listbox.bind("<Button-1>", controller.on_rule_set_select)
        ctk.CTkButton(rules_frame, text="Load Selected Rule Set", command=controller.load_selected_rule_set).pack(pady=10)
        
        # --- Setup Right Panel (Creation Tab) ---
        # --- FIX: Build the entire tab UI in a container first for smoothness ---
        tab = self.creation_tab_frame
        container = ctk.CTkFrame(tab, fg_color="transparent")
        container.grid_columnconfigure((0,1), weight=1)
        container.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(container, text="Create a New Rule Set", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
        ctk.CTkLabel(container, text="Rule Set Name:", anchor="w").grid(row=1, column=0, columnspan=2, padx=20, sticky="w")
        self.rules_name_entry = ctk.CTkEntry(container)
        self.rules_name_entry.grid(row=1, column=0, columnspan=2, padx=20, pady=(0,10), sticky="ew")
        
        ctk.CTkLabel(container, text="Attributes (comma-separated):", anchor="w").grid(row=2, column=0, columnspan=2, padx=20, sticky="w")
        self.rules_attrs_entry = ctk.CTkEntry(container)
        self.rules_attrs_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0,10), sticky="ew")
        self.rules_attrs_entry.insert(0, "Strength, Dexterity, Hit Points")
        
        ctk.CTkLabel(container, text="Skills (Skill:Attribute, one per line):", anchor="w").grid(row=3, column=0, padx=(20,10), sticky="w")
        self.rules_skills_text = ctk.CTkTextbox(container)
        self.rules_skills_text.grid(row=4, column=0, padx=(20,10), pady=(0,10), sticky="nsew")
        self.rules_skills_text.insert("1.0", "Athletics:Strength\nStealth:Dexterity")
        
        ctk.CTkLabel(container, text="Formulas (Name:Formula, one per line):", anchor="w").grid(row=3, column=1, padx=(10,20), sticky="w")
        self.rules_formulas_text = ctk.CTkTextbox(container)
        self.rules_formulas_text.grid(row=4, column=1, padx=(10,20), pady=(0,10), sticky="nsew")
        self.rules_formulas_text.insert("1.0", "Dodge Chance:Dexterity * 2 + 10")
        
        ctk.CTkButton(container, text="Save Rule Set", command=controller.save_new_rule_set).grid(row=5, column=0, columnspan=2, pady=20)
        
        # --- FIX: Pack the finished container to display it all at once ---
        container.pack(fill="both", expand=True)

    def populate_rule_set_list(self, rule_sets):
        self.rule_set_listbox.configure(state="normal")
        self.rule_set_listbox.delete("1.0", "end")
        if not rule_sets:
            self.rule_set_listbox.insert("end", "No rule sets found.")
        else:
            for name in rule_sets:
                self.rule_set_listbox.insert("end", f"{name}\n")
        self.rule_set_listbox.configure(state="disabled")

    def highlight_selection(self):
        self.rule_set_listbox.tag_remove("selected", "1.0", "end")
        self.rule_set_listbox.tag_add("selected", "current linestart", "current lineend")
        self.rule_set_listbox.tag_config("selected", background="#343638", foreground="#DCE4EE")

    def update_status(self, rule_set_name):
        """Updates the status label with the name of the current rule set."""
        if rule_set_name:
            self.status_label.configure(text=rule_set_name)
        else:
            self.status_label.configure(text="None")