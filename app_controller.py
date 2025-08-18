import customtkinter as ctk
from tkinter import messagebox
import os

# Import all controllers
from rules.rules_controller import RulesController
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
from combat.combat_controller import CombatController
from music.music_controller import MusicController
from map.map_controller import MapController
from item.item_controller import ItemController

# Import models and views
from campaign_model import CampaignModel
from main_menu_view import MainMenuView, NewCampaignDialog
from custom_dialogs import MessageBox
from rules.rules_editor_window import RulesEditorWindow
from rules.rules_model import RulesModel

class AppController:
    """The main controller that orchestrates the entire application."""
    def __init__(self, root):
        self.root = root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.campaign_model = CampaignModel()
        self.current_campaign_path = None
        self.editor_frame = None
        self.pages = {}
        self.sidebar_buttons = {}
        self.unsaved_changes = False

        self.main_menu_view = MainMenuView(root, self)
        self.show_main_menu()

    def run(self):
        """Starts the Tkinter main loop."""
        self.root.mainloop()

    def show_main_menu(self):
        """Hides the editor frame and shows the main menu."""
        if self.editor_frame:
            self.editor_frame.pack_forget()
        
        self.main_menu_view.pack(fill="both", expand=True)
        self.main_menu_view.tkraise()

    def _cleanup_editor_session(self):
        """Completely destroys and dereferences all editor components."""
        if self.editor_frame:
            self.editor_frame.destroy()
        
        self.editor_frame = None
        self.pages.clear()
        self.sidebar_buttons.clear()
        
        self.character_controller = None
        self.npc_controller = None
        self.combat_controller = None
        self.map_controller = None
        self.music_controller = None
        self.rules_controller = None
        self.item_controller = None # Clean up item controller reference

    def _show_editor(self):
        """Hides the main menu and builds the main editor UI."""
        self.main_menu_view.pack_forget()
        
        if self.editor_frame is None:
            self.unsaved_changes = False
            self.editor_frame = ctk.CTkFrame(self.root, fg_color="transparent")
            self.editor_frame.pack(fill="both", expand=True)
            self.editor_frame.grid_columnconfigure(1, weight=1)
            self.editor_frame.grid_rowconfigure(1, weight=1)

            # Header Frame
            header_frame = ctk.CTkFrame(self.editor_frame, corner_radius=0, height=60, border_width=1, border_color="gray25")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
            
            header_left = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_left.pack(side="left", padx=20, pady=10)
            self.header_label = ctk.CTkLabel(header_left, text="Loading...", font=ctk.CTkFont(size=18))
            self.header_label.pack()

            header_right = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_right.pack(side="right", padx=10, pady=5)

            # Sidebar Frame
            sidebar_frame = ctk.CTkFrame(self.editor_frame, width=200, corner_radius=0, border_width=1, border_color="gray25")
            sidebar_frame.grid(row=1, column=0, sticky="nsw")
            sidebar_frame.grid_rowconfigure(0, weight=1)

            # Content Frame
            content_frame = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
            content_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)
            content_frame.grid_columnconfigure(0, weight=1)
            content_frame.grid_rowconfigure(0, weight=1)
            
            # --- Initialize Pages (with "Items" added) ---
            page_names = ["Characters", "NPCs", "Character Sheet", "NPC Sheet", "Items", "Combat", "Map Editor", "Map Viewer"]
            for name in page_names:
                self.pages[name] = ctk.CTkFrame(content_frame, fg_color="transparent")
                self.pages[name].grid(row=0, column=0, sticky="nsew")

            # --- Initialize Controllers ---
            self.music_controller = MusicController(self, header_right)
            self.item_controller = ItemController(self, self.pages["Items"], self.current_campaign_path)
            self.character_controller = CharacterController(self, self.pages["Characters"], self.pages["Character Sheet"], self.current_campaign_path, self.item_controller)
            self.npc_controller = NpcController(self, self.pages["NPCs"], self.pages["NPC Sheet"], self.current_campaign_path, self.item_controller)
            self.combat_controller = CombatController(self, self.pages["Combat"], self.current_campaign_path)
            self.map_controller = MapController(self, self.pages["Map Editor"], self.pages["Map Viewer"], self.current_campaign_path)
            self.map_controller.set_source_controllers(self.character_controller, self.npc_controller)
            
            # Populate Sidebar
            sidebar_nav_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
            sidebar_nav_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
            for name in page_names:
                button = ctk.CTkButton(sidebar_nav_frame, text=name, corner_radius=0, fg_color="transparent",
                                       command=lambda n=name: self.show_page(n), height=40, anchor="w")
                button.pack(fill="x")
                self.sidebar_buttons[name] = button

            ctk.CTkButton(sidebar_frame, text="< Back to Main Menu", 
                          command=self.confirm_exit_to_main_menu,
                          fg_color="transparent", border_width=1, border_color="gray50", height=40).grid(
                row=1, column=0, sticky="sew", padx=10, pady=10)

            # Load Campaign Data
            ruleset_name = self.campaign_model.get_campaign_ruleset(os.path.basename(self.current_campaign_path))
            if ruleset_name:
                rules_model = RulesModel()
                ruleset_data = rules_model.load_rule_set(ruleset_name)
                if ruleset_data:
                    campaign_name = os.path.basename(self.current_campaign_path)
                    self.header_label.configure(text=f"{campaign_name}  |  Ruleset: {ruleset_name}")
                    self.on_rule_set_loaded(ruleset_data)
                    self.show_page("Characters")
                else:
                    MessageBox.showerror("Error", f"Failed to load required ruleset '{ruleset_name}'.", self.root)
                    self.show_main_menu()

        self.editor_frame.pack(fill="both", expand=True)
        self.editor_frame.tkraise()

    def show_page(self, page_name):
        if page_name in self.pages:
            self.pages[page_name].tkraise()
            for name, button in self.sidebar_buttons.items():
                if name == page_name:
                    button.configure(fg_color="#3B8ED0")
                else:
                    button.configure(fg_color="transparent")
        
    def set_dirty_flag(self, is_dirty=True):
        self.unsaved_changes = is_dirty

    def confirm_exit_to_main_menu(self):
        if not self.unsaved_changes:
            self.show_main_menu()
            return
        
        response = MessageBox.askyesnocancel("Unsaved Changes",
                                             "You have unsaved changes. Do you want to save them before returning to the main menu?",
                                             parent=self.root)
        
        if response is True:
            MessageBox.showinfo("Save Manually", "Please use the 'Save Changes' or 'Save Token Positions' buttons on the relevant pages to save your work.", parent=self.root)
            return
        elif response is False:
            self.unsaved_changes = False
            self.show_main_menu()
        elif response is None:
            return
            
    def new_game_flow(self):
        """Handles the flow for creating a new campaign."""
        rules_model = RulesModel()
        rulesets = rules_model.get_all_rule_sets()
        
        if not rulesets:
            MessageBox.showerror("Error", "No rule sets found. Please create a rule set first.", self.root)
            return
        
        dialog = NewCampaignDialog(parent=self.root, rulesets=rulesets)
        result = dialog.get_input()

        if not result:
            return

        campaign_name, ruleset_name = result
        self._cleanup_editor_session()

        path = self.campaign_model.create_campaign(campaign_name, ruleset_name)
        if path:
            self.current_campaign_path = path
            self._show_editor()
        else:
            MessageBox.showerror("Error", f"A campaign named '{campaign_name}' already exists.", self.root)

    def load_game_flow(self, campaign_name):
        """Loads a game, rebuilding the editor session."""
        if not campaign_name:
            MessageBox.showerror("Error", "Please select a campaign to load.", self.root)
            return

        new_path = os.path.join(self.campaign_model.base_dir, campaign_name)
        
        if self.editor_frame and self.current_campaign_path == new_path:
            self._show_editor()
        else:
            self._cleanup_editor_session()
            self.current_campaign_path = new_path
            if os.path.exists(self.current_campaign_path):
                self._show_editor()
            else:
                MessageBox.showerror("Error", f"Could not find campaign data for '{campaign_name}'.", self.root)

    def show_ruleset_creator_standalone(self):
        ruleset_window = RulesEditorWindow(self.root)
        standalone_rules_controller = RulesController(self)
        standalone_rules_controller.set_view(ruleset_window)
        ruleset_window.set_controller(standalone_rules_controller)

    def show_placeholder_message(self):
        MessageBox.showinfo("Not Implemented", "This feature has not been implemented yet.", self.root)

    def exit_app(self):
        self.root.quit()
        self.root.destroy()

    def on_rule_set_loaded(self, rule_set):
        """Notifies all relevant controllers that a new rule set is active."""
        self.character_controller.handle_rule_set_load(rule_set)
        self.npc_controller.handle_rule_set_load(rule_set)
        self.combat_controller.handle_rule_set_load(rule_set)
        self.map_controller.handle_rule_set_load(rule_set)
        self.item_controller.handle_rule_set_load(rule_set)

    def on_character_or_npc_list_changed(self):
        self.combat_controller.update_combatant_lists()
        self.character_controller.update_character_sheet_list()
        self.npc_controller.update_npc_management_list()
        self.npc_controller.update_npc_sheet_list()
        self.map_controller.update_token_placer_list()