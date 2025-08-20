import customtkinter as ctk

class ItemView:
    """Manages the UI for the self-contained Item feature."""
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.modifier_widgets = {}

    def setup_ui(self, controller):
        """Builds the UI widgets and connects them to the controller."""
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_columnconfigure(1, weight=2)
        self.parent_frame.grid_rowconfigure(0, weight=1)

        # Left Pane: List of existing items
        list_frame = ctk.CTkFrame(self.parent_frame)
        list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(list_frame, text="Campaign Items", font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=0, padx=10, pady=10)
        self.item_list_frame = ctk.CTkScrollableFrame(list_frame)
        self.item_list_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Right Pane: Editor for creating/editing an item
        editor_frame = ctk.CTkFrame(self.parent_frame)
        editor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        editor_frame.grid_columnconfigure(0, weight=1)
        editor_frame.grid_rowconfigure(4, weight=1)
        
        self.editor_label = ctk.CTkLabel(editor_frame, text="Create New Item", font=ctk.CTkFont(size=16, weight="bold"))
        self.editor_label.grid(row=0, column=0, pady=10, padx=10)

        ctk.CTkLabel(editor_frame, text="Item Name:", anchor="w").grid(row=1, column=0, sticky="ew", padx=10)
        self.name_entry = ctk.CTkEntry(editor_frame)
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10), columnspan=2)

        ctk.CTkLabel(editor_frame, text="Item Type:", anchor="w").grid(row=2, column=0, sticky="ew", padx=10)
        self.type_combo = ctk.CTkComboBox(editor_frame, values=["Weapon", "Armor", "Consumable", "Quest Item", "Miscellaneous"])
        self.type_combo.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10), columnspan=2)
        self.type_combo.set("Miscellaneous")

        ctk.CTkLabel(editor_frame, text="Description:", anchor="w").grid(row=3, column=0, sticky="ew", padx=10)
        self.desc_textbox = ctk.CTkTextbox(editor_frame, height=100)
        self.desc_textbox.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10), columnspan=2)

        self.modifier_list_frame = ctk.CTkScrollableFrame(editor_frame, label_text="Stat Modifiers (Optional)")
        self.modifier_list_frame.grid(row=4, column=0, sticky="nsew", padx=10, pady=5)

        self.button_frame = ctk.CTkFrame(editor_frame, fg_color="transparent")
        self.button_frame.grid(row=5, column=0, sticky="ew", pady=10, padx=10)

        self.save_new_button = ctk.CTkButton(self.button_frame, text="Save New Item", command=controller.save_new_item)
        self.save_new_button.pack(side="left", padx=5)
        self.save_changes_button = ctk.CTkButton(self.button_frame, text="Save Changes", command=controller.save_changes)
        self.delete_button = ctk.CTkButton(self.button_frame, text="Delete Item", command=controller.delete_item, fg_color="#D2691E", hover_color="#B2590E")
        self.clear_button = ctk.CTkButton(self.button_frame, text="Clear Form", command=controller.clear_editor_fields)
        self.clear_button.pack(side="right", padx=5)

    def build_modifier_fields(self, rule_set, controller):
        """Dynamically creates the stat modifier UI based on the loaded ruleset."""
        for widget in self.modifier_list_frame.winfo_children():
            widget.destroy()
        self.modifier_widgets.clear()

        all_stats = rule_set.get('attributes', []) + list(rule_set.get('skills', {}).keys())
        
        for stat_name in sorted(all_stats):
            row_frame = ctk.CTkFrame(self.modifier_list_frame, fg_color="transparent")
            row_frame.pack(fill="x", pady=2)

            ctk.CTkLabel(row_frame, text=stat_name, anchor="w").pack(side="left", expand=True, fill="x")
            
            minus_button = ctk.CTkButton(row_frame, text="-", width=30, command=lambda s=stat_name: controller.adjust_modifier(s, -1))
            minus_button.pack(side="left", padx=5)
            
            value_label = ctk.CTkLabel(row_frame, text="0", width=30, anchor="center")
            value_label.pack(side="left")
            
            plus_button = ctk.CTkButton(row_frame, text="+", width=30, command=lambda s=stat_name: controller.adjust_modifier(s, 1))
            plus_button.pack(side="left", padx=5)

            self.modifier_widgets[stat_name] = value_label

    def display_items(self, items, controller):
        """Clears and repopulates the list of items on the left."""
        for widget in self.item_list_frame.winfo_children():
            widget.destroy()
        
        for item in items:
            item_row = ctk.CTkButton(self.item_list_frame, text=item["name"], anchor="w", fg_color="transparent",
                                     command=lambda i=item: controller.select_item(i))
            item_row.pack(fill="x", pady=2)

    def populate_editor(self, item):
        """Fills the editor fields with the data of the selected item."""
        self.clear_modifiers()
        self.name_entry.delete(0, 'end')
        self.name_entry.insert(0, item["name"])
        self.type_combo.set(item["type"])
        self.desc_textbox.delete("1.0", "end")
        self.desc_textbox.insert("1.0", item["description"])
        
        for modifier in item.get("modifiers", []):
            stat = modifier["stat"]
            value = modifier["value"]
            if stat in self.modifier_widgets:
                self.modifier_widgets[stat].configure(text=str(value))

        self.save_new_button.pack_forget()
        self.save_changes_button.pack(side="left", padx=5)
        self.delete_button.pack(side="left", padx=5)

    def clear_editor(self):
        """Clears all editor fields and resets button visibility."""
        self.name_entry.delete(0, 'end')
        self.type_combo.set("Miscellaneous")
        self.desc_textbox.delete("1.0", "end")
        self.clear_modifiers()
        self.editor_label.configure(text="Create New Item")

        self.save_changes_button.pack_forget()
        self.delete_button.pack_forget()
        self.save_new_button.pack(side="left", padx=5)

    def clear_modifiers(self):
        """Resets all modifier value labels to '0'."""
        for label in self.modifier_widgets.values():
            label.configure(text="0")