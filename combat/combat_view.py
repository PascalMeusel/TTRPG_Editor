import customtkinter as ctk

class CombatView:
    """
    Manages the UI for the Combat Simulator tab.
    Its primary responsibility is to build the simulator interface once a rule set is loaded.
    """
    def __init__(self, tab_frame):
        self.tab_frame = tab_frame

    def setup_ui(self, controller):
        """Sets up the initial, static part of the UI."""
        tab = self.tab_frame
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_rowconfigure(1, weight=1) # Allow content frame to expand
        
        ctk.CTkLabel(tab, text="Combat Assistant", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=20)

        # This frame will hold either the initial message or the full simulator
        self.content_frame = ctk.CTkFrame(tab, fg_color="transparent")
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # This label is shown by default and is destroyed when the simulator is built.
        self.initial_label = ctk.CTkLabel(self.content_frame, text="Load a rule set to use the simulator.")
        self.initial_label.pack(pady=20)

    def show_simulator(self, controller):
        """Builds the full simulator UI smoothly after a rule set is loaded."""
        # Clear any existing content (like the initial message)
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Build the new UI in a temporary container for a smooth, single-frame update
        container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        
        combatant_frame = ctk.CTkFrame(container, fg_color="transparent")
        combatant_frame.pack(fill="x", pady=5)
        combatant_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(combatant_frame, text="Attacker:").grid(row=0, column=0, padx=(0,10), sticky="w")
        self.attacker_list = ctk.CTkComboBox(combatant_frame, state="readonly")
        self.attacker_list.grid(row=1, column=0, padx=(0,10), sticky="ew")
        ctk.CTkLabel(combatant_frame, text="Defender:").grid(row=0, column=1, padx=(10,0), sticky="w")
        self.defender_list = ctk.CTkComboBox(combatant_frame, state="readonly")
        self.defender_list.grid(row=1, column=1, padx=(10,0), sticky="ew")

        input_frame = ctk.CTkFrame(container, fg_color="transparent")
        input_frame.pack(fill="x", pady=15)
        input_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(input_frame, text="Dice Roll:").grid(row=0, column=0, padx=(0,10), sticky="w")
        self.roll_entry = ctk.CTkEntry(input_frame)
        self.roll_entry.grid(row=1, column=0, padx=(0,10), sticky="ew")
        ctk.CTkLabel(input_frame, text="Modifier:").grid(row=0, column=1, padx=(10,0), sticky="w")
        self.mod_entry = ctk.CTkEntry(input_frame)
        self.mod_entry.grid(row=1, column=1, padx=(10,0), sticky="ew")
        self.mod_entry.insert(0, "0")

        action_frame = ctk.CTkFrame(container, fg_color="transparent")
        action_frame.pack(pady=10)
        ctk.CTkButton(action_frame, text="Calculate Hit", command=controller.run_combat_hit).pack(side="left", padx=10)
        ctk.CTkButton(action_frame, text="Calculate Damage", command=controller.run_combat_damage).pack(side="left", padx=10)

        output_frame = ctk.CTkScrollableFrame(container, label_text="Result Log")
        output_frame.pack(fill="both", expand=True, pady=10)
        self.output_text = ctk.CTkTextbox(output_frame, state="disabled", wrap="word", fg_color="transparent")
        self.output_text.pack(fill="both", expand=True)

        # Show the fully built container all at once
        container.pack(fill="both", expand=True)

    def update_combatant_lists(self, combatants):
        """Populates the attacker and defender dropdowns with a list of names."""
        combatants = combatants or ["-"]
        self.attacker_list.configure(values=combatants)
        self.defender_list.configure(values=combatants)
        self.attacker_list.set(combatants[0])
        self.defender_list.set(combatants[0])

    def write_to_log(self, message):
        """Appends a message to the combat log text box."""
        self.output_text.configure(state="normal")
        self.output_text.insert("end", message + "\n\n")
        self.output_text.see("end")
        self.output_text.configure(state="disabled")