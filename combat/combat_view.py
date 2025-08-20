import customtkinter as ctk

class CombatView:
    """Manages the UI for the new Combat Tracker feature."""
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.roster_buttons = {}
        # This will be assigned in setup_ui
        self.frame = None

    def setup_ui(self, controller):
        """Builds the initial UI layout."""
        # --- FIX: Assign self.frame and configure the parent grid ---
        self.frame = self.parent_frame
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        # --- FIX: Create all widgets as children of self.frame ---
        self.main_pane = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.main_pane.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.main_pane.grid_columnconfigure(0, weight=1)
        self.main_pane.grid_columnconfigure(1, weight=2)
        self.main_pane.grid_rowconfigure(0, weight=1)

        self.setup_pane = ctk.CTkFrame(self.main_pane)
        self.setup_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        self.setup_pane.grid_rowconfigure(1, weight=1)
        self.setup_pane.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.setup_pane, text="Available Combatants", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=5)
        self.available_list = ctk.CTkScrollableFrame(self.setup_pane)
        self.available_list.grid(row=1, column=0, sticky="nsew", padx=5)

        ctk.CTkLabel(self.setup_pane, text="Encounter Roster", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, pady=5)
        self.roster_list = ctk.CTkScrollableFrame(self.setup_pane)
        self.roster_list.grid(row=3, column=0, sticky="nsew", padx=5)

        ctk.CTkButton(self.setup_pane, text="Start Combat", command=controller.start_combat).grid(row=4, column=0, pady=10)

        self.tracker_pane = ctk.CTkFrame(self.main_pane)
        self.tracker_pane.grid_rowconfigure(0, weight=1)
        self.tracker_pane.grid_columnconfigure(0, weight=1)

        self.tracker_list = ctk.CTkScrollableFrame(self.tracker_pane, label_text="Turn Order")
        self.tracker_list.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.action_frame = ctk.CTkFrame(self.tracker_pane, fg_color="transparent")
        self.action_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        self.bottom_frame = ctk.CTkFrame(self.tracker_pane, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=10)

    def update_available_list(self, available_combatants, controller):
        for widget in self.available_list.winfo_children():
            widget.destroy()
        for model in available_combatants:
            btn = ctk.CTkButton(self.available_list, text=f"+ {model.name}", anchor="w",
                                command=lambda m=model: controller.add_to_roster(m))
            btn.pack(fill="x", pady=2)

    def update_roster_list(self, roster, controller):
        for widget in self.roster_list.winfo_children():
            widget.destroy()
        for combatant in roster.values():
            btn = ctk.CTkButton(self.roster_list, text=f"- {combatant['name']}", anchor="w", fg_color="#D2691E",
                                command=lambda cid=combatant['id']: controller.remove_from_roster(cid))
            btn.pack(fill="x", pady=2)

    def display_tracker_ui(self, controller):
        """
        --- One-time setup for the tracker UI. ---
        This is called only when combat starts.
        """
        self.setup_pane.grid_forget()
        self.tracker_pane.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self._display_actions(controller)
        self._display_bottom_buttons(controller)

    def update_turn_order_list(self, turn_order, combatants_data, current_turn_id, controller):
        """
        --- Dynamically redraws only the list of combatants. ---
        This is called every time the turn order changes.
        """
        for widget in self.tracker_list.winfo_children():
            widget.destroy()

        for index, combatant_id in enumerate(turn_order):
            combatant = combatants_data[combatant_id]
            is_current = (combatant_id == current_turn_id)
            row_color = "#3B8ED0" if is_current else "gray20"
            row = ctk.CTkFrame(self.tracker_list, fg_color=row_color, corner_radius=5)
            row.pack(fill="x", pady=3, padx=5)
            
            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            
            initiative_label = ctk.CTkLabel(row, text=f'{combatant["initiative"]}', font=ctk.CTkFont(size=16, weight="bold"), width=30)
            initiative_label.grid(row=0, column=0, rowspan=2, padx=10, pady=5)
            name_label = ctk.CTkLabel(row, text=f'{combatant["name"]}', anchor="w", font=ctk.CTkFont(size=14, weight="bold"))
            name_label.grid(row=0, column=1, sticky="w", padx=5)
            hp_text = f'HP: {combatant["current_hp"]} / {combatant["max_hp"]}'
            hp_label = ctk.CTkLabel(row, text=hp_text, anchor="w")
            hp_label.grid(row=1, column=1, sticky="w", padx=5)
            status_label = ctk.CTkLabel(row, text="Status / Notes:", anchor="w", font=ctk.CTkFont(size=12))
            status_label.grid(row=0, column=2, sticky="sw", padx=10, pady=(0,2))
            status_entry = ctk.CTkEntry(row)
            status_entry.grid(row=1, column=2, padx=10, pady=(0, 5), sticky="ew")
            status_entry.insert(0, combatant["status"])
            status_entry.bind("<FocusOut>", lambda event, cid=combatant_id, w=status_entry: controller.set_status(cid, w.get()))

            move_button_frame = ctk.CTkFrame(row, fg_color="transparent")
            move_button_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5)
            up_button = ctk.CTkButton(move_button_frame, text="▲", width=25,
                                      command=lambda cid=combatant_id: controller.move_combatant_up(cid))
            up_button.pack(pady=(2,1))
            down_button = ctk.CTkButton(move_button_frame, text="▼", width=25,
                                        command=lambda cid=combatant_id: controller.move_combatant_down(cid))
            down_button.pack(pady=(1,2))

            if index == 0:
                up_button.configure(state="disabled")
            if index == len(turn_order) - 1:
                down_button.configure(state="disabled")

    def _display_actions(self, controller):
        for widget in self.action_frame.winfo_children():
            widget.destroy()
        self.action_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.action_frame, text="Value:").grid(row=0, column=0, padx=5)
        self.action_value_entry = ctk.CTkEntry(self.action_frame)
        self.action_value_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(self.action_frame, text="Apply Damage", command=controller.apply_damage).grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.action_frame, text="Apply Healing", command=controller.apply_healing).grid(row=0, column=3, padx=5)

    def _display_bottom_buttons(self, controller):
        for widget in self.bottom_frame.winfo_children():
            widget.destroy()
        ctk.CTkButton(self.bottom_frame, text="Next Turn >", command=controller.next_turn).pack(side="left", padx=10, pady=5)
        ctk.CTkButton(self.bottom_frame, text="End Combat", command=controller.end_combat, fg_color="#D2691E").pack(side="right", padx=10, pady=5)

    def clear_view(self):
        self.tracker_pane.grid_forget()
        self.setup_pane.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        for w in self.tracker_list.winfo_children(): w.destroy()