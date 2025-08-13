import customtkinter as ctk
import threading
import queue

class NewCampaignDialog(ctk.CTkToplevel):
    def __init__(self, parent, rulesets):
        super().__init__(parent)
        self.title("New Campaign")
        self.geometry("400x300")
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        self.result = None
        self.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="Create New Campaign", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 10))
        
        # Name Input
        ctk.CTkLabel(self, text="Campaign Name:", anchor="w").pack(pady=(5, 0), padx=20, fill="x")
        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=(0, 10), padx=20, fill="x")
        
        # Ruleset Selection
        ctk.CTkLabel(self, text="Choose Rule Set:", anchor="w").pack(pady=(5, 0), padx=20, fill="x")
        self.combobox = ctk.CTkComboBox(self, values=rulesets, state="readonly", width=300)
        self.combobox.pack(pady=(0, 10), padx=20, fill="x")
        if rulesets:
            self.combobox.set(rulesets[0])
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(pady=20)
        ctk.CTkButton(button_frame, text="Create Campaign", command=self._on_ok).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=self._on_close).pack(side="left", padx=10)

        self.transient(parent) # Set as modal
        self.grab_set()
        self.wait_window(self)

    def _on_close(self):
        self.grab_release()
        self.destroy()

    def _on_ok(self):
        campaign_name = self.name_entry.get().strip()
        ruleset_name = self.combobox.get()
        
        if not campaign_name or not ruleset_name or ruleset_name == "No rule sets found":
            self.result = None
            self._on_close()
            return
            
        self.result = (campaign_name, ruleset_name)
        self._on_close()

    def get_input(self):
        return self.result



class MainMenuView(ctk.CTkFrame):
    """The UI for the main menu screen, featuring a clean vertical layout."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.load_game_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="TTRPG Campaign Editor", font=ctk.CTkFont(size=32, weight="bold")).grid(
            row=0, column=0, pady=(50, 30))
        
        menu_frame = ctk.CTkFrame(self, fg_color="transparent")
        menu_frame.grid(row=1, column=0, sticky="n")

        button_width = 250
        button_height = 50
        button_pady = 10

        ctk.CTkButton(
            menu_frame, text="New Game", width=button_width, height=button_height,
            command=self.controller.new_game_flow
        ).pack(pady=button_pady)
        
        ctk.CTkButton(
            menu_frame, text="Load Game", width=button_width, height=button_height,
            command=self.show_load_game_window
        ).pack(pady=button_pady)
        
        ctk.CTkButton(
            menu_frame, text="Create New Ruleset", width=button_width, height=button_height,
            command=self.controller.show_ruleset_creator_standalone
        ).pack(pady=button_pady)
        
        ctk.CTkButton(
            menu_frame, text="Edit Rulesets", width=button_width, height=button_height,
            command=self.controller.show_placeholder_message, state="disabled"
        ).pack(pady=button_pady)
        
        ctk.CTkButton(
            menu_frame, text="Settings", width=button_width, height=button_height,
            command=self.controller.show_placeholder_message, state="disabled"
        ).pack(pady=button_pady)
        
        ctk.CTkButton(
            menu_frame, text="Exit", width=button_width, height=button_height,
            command=self.controller.exit_app, fg_color="#D2691E", hover_color="#B2590E"
        ).pack(pady=(30, 10))

    def show_load_game_window(self):
        """Creates and displays the 'Load Game' pop-up window."""
        if self.load_game_window is None or not self.load_game_window.winfo_exists():
            self.load_game_window = LoadGameWindow(self, self.controller)
            self.load_game_window.grab_set()
        else:
            self.load_game_window.focus()

class LoadGameWindow(ctk.CTkToplevel):
    """A pop-up window that asynchronously loads and displays saved campaigns."""
    def __init__(self, parent_view, controller):
        super().__init__(parent_view)
        self.controller = controller
        self.selected_campaign = None
        self.campaign_buttons = []

        self.title("Load Game")
        self.geometry("400x500")
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close) # Handle 'X' button
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Select a Campaign", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10)

        self.campaign_list_frame = ctk.CTkScrollableFrame(self, label_text="Existing Campaigns")
        self.campaign_list_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        
        self.loading_label = ctk.CTkLabel(self.campaign_list_frame, text="Loading...")
        self.loading_label.pack(pady=20)

        ctk.CTkButton(self, text="Load Selected", command=self._load_and_close).grid(row=2, column=0, pady=10)

        self.campaign_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._fetch_campaigns_worker, daemon=True)
        self.worker_thread.start()
        self.after(100, self._process_queue)

    def _fetch_campaigns_worker(self):
        """(Runs on a background thread) Fetches the list of campaigns."""
        campaigns = self.controller.campaign_model.list_campaigns()
        self.campaign_queue.put(campaigns)

    def _process_queue(self):
        """(Runs on the main GUI thread) Checks for results from the worker thread."""
        try:
            campaigns = self.campaign_queue.get_nowait()
            self._populate_list_ui(campaigns)
        except queue.Empty:
            if self.winfo_exists():
                self.after(100, self._process_queue)

    def _populate_list_ui(self, campaigns):
        """(Runs on the main GUI thread) Clears old widgets and builds the button list."""
        self.loading_label.destroy()
        for btn in self.campaign_buttons:
            btn.destroy()
        self.campaign_buttons.clear()
        self.selected_campaign = None

        if not campaigns:
            ctk.CTkLabel(self.campaign_list_frame, text="No saved games found.").pack()
        else:
            for name in campaigns:
                btn = ctk.CTkButton(self.campaign_list_frame, text=name, 
                                    command=lambda n=name: self._on_campaign_select(n),
                                    fg_color="transparent", border_width=1, border_color="gray50")
                btn.pack(pady=2, padx=5, fill="x")
                self.campaign_buttons.append(btn)
    
    def _on_campaign_select(self, campaign_name):
        self.selected_campaign = campaign_name
        for btn in self.campaign_buttons:
            if btn.cget("text") == campaign_name:
                btn.configure(fg_color="#3B8ED0", border_color="#3B8ED0")
            else:
                btn.configure(fg_color="transparent", border_color="gray50")
    
    def _on_close(self):
        """Ensures the grab is released before destroying the window."""
        self.grab_release()
        self.destroy()

    def _load_and_close(self):
        """Schedules the loading operation and safely closes the pop-up."""
        campaign_to_load = self.selected_campaign
        self._on_close() # Use the safe closing method
        if campaign_to_load:
            self.controller.root.after(50, lambda: self.controller.load_game_flow(campaign_to_load))

class RulesetSelectionDialog(ctk.CTkToplevel):
    """A modal dialog window to force the user to select a ruleset from a dropdown."""
    def __init__(self, parent, title, text, values):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close) # Handle 'X' button
        
        self.selection = None
        self.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self, text=text, wraplength=380).pack(pady=(20, 10), padx=20)
        
        self.combobox = ctk.CTkComboBox(self, values=values, state="readonly")
        self.combobox.pack(pady=10, padx=20, fill="x")
        if values:
            self.combobox.set(values[0])

        ctk.CTkButton(self, text="Confirm", command=self._on_ok).pack(pady=20)

        self.transient(parent)
        self.grab_set()
        self.wait_window(self)

    def _on_close(self):
        """Ensures the grab is released before destroying the window."""
        self.grab_release()
        self.destroy()

    def _on_ok(self, event=None):
        """Saves the selection and closes the dialog."""
        self.selection = self.combobox.get()
        self._on_close()

    def get_selection(self):
        return self.selection