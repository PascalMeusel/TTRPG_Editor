import customtkinter as ctk

class LinkSelectionDialog(ctk.CTkToplevel):
    """A reusable dialog to select an NPC or Item to link to a quest."""
    def __init__(self, parent, title, items_to_display):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x500")
        self.configure(fg_color="#2B2B2B")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.selected_id = None
        self.buttons = []
        ctk.CTkLabel(self, text=f"Select {title.split(' ')[-1]} to Link", font=ctk.CTkFont(size=16)).pack(pady=10)
        scroll_frame = ctk.CTkScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)
        if not items_to_display:
            ctk.CTkLabel(scroll_frame, text="Nothing available to link.").pack()
        else:
            for item in items_to_display:
                btn = ctk.CTkButton(scroll_frame, text=item["name"],
                                    command=lambda i=item: self._select(i), 
                                    fg_color="transparent", anchor="w", border_width=1, border_color="gray50")
                btn.pack(fill="x", pady=2)
                self.buttons.append((btn, item))
        self.confirm_button = ctk.CTkButton(self, text="Link Selected", command=self._on_confirm, state="disabled")
        self.confirm_button.pack(pady=10)
        self.transient(parent)
        self.update_idletasks()
        self.grab_set()
        self.wait_window()

    def _select(self, item):
        self.selected_id = item["id"]
        self.confirm_button.configure(state="normal")
        for btn, btn_item in self.buttons:
            if btn_item["id"] == item["id"]:
                btn.configure(fg_color="#3B8ED0", border_color="#3B8ED0")
            else:
                btn.configure(fg_color="transparent", border_color="gray50")

    def _on_confirm(self):
        self.destroy()

    def _on_cancel(self):
        self.selected_id = None
        self.destroy()

    def get_selection(self):
        return self.selected_id

class QuestView:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.quest_buttons = {}
        self.editor_is_built = False

    def setup_ui(self, controller):
        self.parent_frame.grid_columnconfigure(0, weight=1)
        self.parent_frame.grid_columnconfigure(1, weight=2)
        self.parent_frame.grid_rowconfigure(0, weight=1)
        
        list_frame = ctk.CTkFrame(self.parent_frame)
        list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(list_frame, text="Create New Quest", command=controller.create_new_quest).grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.quest_list_scroll_frame = ctk.CTkScrollableFrame(list_frame, label_text="Quests by Status")
        self.quest_list_scroll_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.editor_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        self.editor_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.editor_frame.grid_columnconfigure(0, weight=1)
        self.editor_frame.grid_rowconfigure(0, weight=1)

    def build_quest_editor(self, controller):
        """Builds the editor UI widgets ONCE."""
        if self.editor_is_built: return
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        self.editor_frame.grid_columnconfigure(1, weight=1)
        self.editor_frame.grid_rowconfigure(3, weight=1)
        self.editor_frame.grid_rowconfigure(5, weight=1)
        self.editor_label = ctk.CTkLabel(self.editor_frame, text="Create New Item", font=ctk.CTkFont(size=16, weight="bold"))
        self.editor_label.grid(row=0, column=0, columnspan=2, pady=10, padx=10)
        ctk.CTkLabel(self.editor_frame, text="Title:").grid(row=1, column=0, padx=10, sticky="w")
        self.title_entry = ctk.CTkEntry(self.editor_frame)
        self.title_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(self.editor_frame, text="Status:").grid(row=2, column=0, padx=10, sticky="w")
        self.status_combo = ctk.CTkComboBox(self.editor_frame, values=["Active", "Inactive", "Completed", "Failed"])
        self.status_combo.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        ctk.CTkLabel(self.editor_frame, text="Description:").grid(row=3, column=0, padx=10, sticky="nw")
        self.desc_text = ctk.CTkTextbox(self.editor_frame)
        self.desc_text.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        obj_frame = ctk.CTkFrame(self.editor_frame)
        obj_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")
        obj_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(obj_frame, text="Objectives").pack(side="left")
        ctk.CTkButton(obj_frame, text="+", width=30, command=controller.add_objective).pack(side="right")
        self.objectives_frame = ctk.CTkScrollableFrame(self.editor_frame, label_text="")
        self.objectives_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=(0,10), sticky="nsew")
        links_pane = ctk.CTkFrame(self.editor_frame)
        links_pane.grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        links_pane.grid_columnconfigure((0,1), weight=1)
        npc_link_frame = ctk.CTkFrame(links_pane)
        npc_link_frame.grid(row=0, column=0, padx=(0,5), sticky="nsew")
        npc_link_frame.grid_columnconfigure(0, weight=1)
        npc_link_header = ctk.CTkFrame(npc_link_frame, fg_color="transparent")
        npc_link_header.pack(fill="x")
        ctk.CTkLabel(npc_link_header, text="Linked NPCs").pack(side="left")
        ctk.CTkButton(npc_link_header, text="Add", width=50, command=controller.show_add_npc_dialog).pack(side="right")
        self.linked_npcs_frame = ctk.CTkScrollableFrame(npc_link_frame, label_text="")
        self.linked_npcs_frame.pack(fill="both", expand=True)
        item_link_frame = ctk.CTkFrame(links_pane)
        item_link_frame.grid(row=0, column=1, padx=(5,0), sticky="nsew")
        item_link_frame.grid_columnconfigure(0, weight=1)
        item_link_header = ctk.CTkFrame(item_link_frame, fg_color="transparent")
        item_link_header.pack(fill="x")
        ctk.CTkLabel(item_link_header, text="Linked Items").pack(side="left")
        ctk.CTkButton(item_link_header, text="Add", width=50, command=controller.show_add_item_dialog).pack(side="right")
        self.linked_items_frame = ctk.CTkScrollableFrame(item_link_frame, label_text="")
        self.linked_items_frame.pack(fill="both", expand=True)
        button_frame = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
        button_frame.grid(row=7, column=0, columnspan=2, pady=10)
        ctk.CTkButton(button_frame, text="Save Changes", command=controller.save_changes).grid(row=0, column=0, padx=5)
        ctk.CTkButton(button_frame, text="Delete Quest", command=controller.delete_quest, fg_color="#D2691E").grid(row=0, column=1, padx=5)
        self.editor_is_built = True

    def populate_editor(self, quest):
        """Populates the pre-existing editor widgets with new data."""
        self.editor_label.configure(text=f"Editing: {quest['title']}")
        self.title_entry.delete(0, 'end')
        self.title_entry.insert(0, quest['title'])
        self.status_combo.set(quest['status'])
        self.desc_text.delete("1.0", "end")
        self.desc_text.insert("1.0", quest['description'])
        
    def clear_editor(self):
        """Hides the editor content and shows a placeholder."""
        for widget in self.editor_frame.winfo_children():
            widget.destroy()
        self.editor_is_built = False
        self.placeholder_label = ctk.CTkLabel(self.editor_frame, text="Select a quest to view or create a new one.", font=ctk.CTkFont(size=16))
        self.placeholder_label.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
    def show_editor_widgets(self):
        if hasattr(self, 'placeholder_label'):
            self.placeholder_label.destroy()

    def display_quest_list(self, quests_by_status, controller):
        """Rebuilds the categorized and color-coded list of quest buttons."""
        for widget in self.quest_list_scroll_frame.winfo_children():
            widget.destroy()
        self.quest_buttons.clear()
        status_map = {
            "Active": {"order": 1, "color": "#3B8ED0"},
            "Inactive": {"order": 2, "color": "gray50"},
            "Completed": {"order": 3, "color": "#228B22"},
            "Failed": {"order": 4, "color": "#D2691E"}
        }
        sorted_statuses = sorted(quests_by_status.keys(), key=lambda s: status_map.get(s, {}).get("order", 99))
        for status in sorted_statuses:
            if not quests_by_status[status]: continue
            header_color = status_map.get(status, {"color": "gray25"})["color"]
            header_frame = ctk.CTkFrame(self.quest_list_scroll_frame, fg_color=header_color, corner_radius=5)
            header_frame.pack(fill="x", pady=(8, 2))
            ctk.CTkLabel(header_frame, text=status, font=ctk.CTkFont(size=14, weight="bold")).pack(padx=10, pady=5)
            for quest in sorted(quests_by_status[status], key=lambda q: q['title'].lower()):
                quest_row = ctk.CTkButton(self.quest_list_scroll_frame, text=quest["title"], anchor="w", fg_color="gray25",
                                         command=lambda q=quest: controller.select_quest(q))
                quest_row.pack(fill="x", pady=0, padx=10)
                self.quest_buttons[quest['id']] = quest_row

    def highlight_selected_quest(self, selected_quest_id=None):
        """Updates the border of the selected quest button."""
        for quest_id, button in self.quest_buttons.items():
            if quest_id == selected_quest_id:
                button.configure(border_width=2, border_color="#FFFFFF")
            else:
                button.configure(border_width=0)

    def redraw_objectives(self, objectives, controller):
        for widget in self.objectives_frame.winfo_children():
            widget.destroy()
        for i, obj in enumerate(objectives):
            obj_row = ctk.CTkFrame(self.objectives_frame, fg_color="transparent")
            obj_row.pack(fill="x", pady=2)
            check = ctk.CTkCheckBox(obj_row, text="", width=20, command=lambda idx=i: controller.toggle_objective(idx))
            if obj['completed']: check.select()
            check.pack(side="left")
            entry = ctk.CTkEntry(obj_row)
            entry.insert(0, obj['text'])
            entry.bind("<KeyRelease>", lambda event, idx=i, w=entry: controller.update_objective_text(idx, w.get()))
            entry.pack(side="left", fill="x", expand=True, padx=5)
            ctk.CTkButton(obj_row, text="-", width=30, fg_color="gray50", command=lambda idx=i: controller.remove_objective(idx)).pack(side="right")

    def redraw_links(self, linked_npcs, linked_items, all_npcs, all_items, controller):
        for widget in self.linked_npcs_frame.winfo_children():
            widget.destroy()
        for npc_id in linked_npcs:
            npc = next((n for n in all_npcs if n['id'] == npc_id), None)
            if npc:
                link_row = ctk.CTkFrame(self.linked_npcs_frame, fg_color="transparent")
                link_row.pack(fill="x", pady=2)
                ctk.CTkLabel(link_row, text=npc['name'], anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkButton(link_row, text="X", width=25, fg_color="#D2691E", command=lambda i=npc_id: controller.remove_link("npc", i)).pack(side="right")
        for widget in self.linked_items_frame.winfo_children():
            widget.destroy()
        for item_id in linked_items:
            item = next((i for i in all_items if i['id'] == item_id), None)
            if item:
                link_row = ctk.CTkFrame(self.linked_items_frame, fg_color="transparent")
                link_row.pack(fill="x", pady=2)
                ctk.CTkLabel(link_row, text=item['name'], anchor="w").pack(side="left", fill="x", expand=True)
                ctk.CTkButton(link_row, text="X", width=25, fg_color="#D2691E", command=lambda i=item_id: controller.remove_link("item", i)).pack(side="right")