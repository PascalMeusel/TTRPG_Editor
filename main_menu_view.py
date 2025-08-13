import customtkinter as ctk
import threading
import queue

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
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Select a Campaign", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, pady=10)

        self.campaign_list_frame = ctk.CTkScrollableFrame(self, label_text="Existing Campaigns")
        self.campaign_list_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        
        self.loading_label = ctk.CTkLabel(self.campaign_list_frame, text="Loading...")
        self.loading_label.pack(pady=20)

        ctk.CTkButton(self, text="Load Selected", command=self._load_and_close).grid(row=2, column=0, pady=10)

        # --- THE FIX: Asynchronous Loading ---
        self.campaign_queue = queue.Queue()
        # 1. Start a background thread to do the slow disk I/O
        self.worker_thread = threading.Thread(target=self._fetch_campaigns_worker, daemon=True)
        self.worker_thread.start()
        # 2. Start a polling loop on the main GUI thread to check for results
        self.after(100, self._process_queue)

    def _fetch_campaigns_worker(self):
        """(Runs on a background thread) Fetches the list of campaigns and puts it in the queue."""
        campaigns = self.controller.campaign_model.list_campaigns()
        self.campaign_queue.put(campaigns)

    def _process_queue(self):
        """(Runs on the main GUI thread) Checks the queue for data from the worker thread."""
        try:
            campaigns = self.campaign_queue.get_nowait()
            # If we got data, update the UI with it
            self._populate_list_ui(campaigns)
        except queue.Empty:
            # If no data yet, check again in 100ms
            if self.winfo_exists(): # Only continue polling if the window is still open
                self.after(100, self._process_queue)

    def _populate_list_ui(self, campaigns):
        """(Runs on the main GUI thread) Clears old widgets and builds the button list."""
        self.loading_label.destroy() # Remove "Loading..." message
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
    
    def _load_and_close(self):
        campaign_to_load = self.selected_campaign
        self.destroy()
        if campaign_to_load:
            self.controller.root.after(50, lambda: self.controller.load_game_flow(campaign_to_load))

class RulesetSelectionDialog(ctk.CTkToplevel):
    """A modal dialog window to force the user to select a ruleset from a dropdown."""
    def __init__(self, parent, title, text, values):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        
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

    def _on_ok(self, event=None):
        self.selection = self.combobox.get()
        self.destroy()

    def get_selection(self):
        return self.selection