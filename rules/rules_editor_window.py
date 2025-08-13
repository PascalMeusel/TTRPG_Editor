import customtkinter as ctk

class RulesEditorWindow(ctk.CTkToplevel):
    """A standalone, modal Toplevel window for creating and editing a rule set."""
    def __init__(self, parent):
        super().__init__(parent)
        self.controller = None

        self.title("Rule Set Editor")
        self.geometry("800x600")
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_columnconfigure((0,1), weight=1)
        container.grid_rowconfigure(4, weight=1)
        
        ctk.CTkLabel(container, text="Rule Set Editor", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=20)
        
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
        
        self.save_button = ctk.CTkButton(container, text="Save Rule Set")
        self.save_button.grid(row=5, column=0, columnspan=2, pady=20)

        self.grab_set() # Make window modal

    def set_controller(self, controller):
        """Connects the controller to this view."""
        self.controller = controller
        # Now that the controller is set, we can assign the command
        self.save_button.configure(command=self.controller.save_new_rule_set)