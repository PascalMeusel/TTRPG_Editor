import customtkinter as ctk
from rules.rules_controller import RulesController
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
from combat.combat_controller import CombatController
from music.music_controller import MusicController
from map.map_controller import MapController

class AppController:
    """The main controller that orchestrates the entire application."""
    def __init__(self, root):
        self.root = root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        main_content_frame = ctk.CTkFrame(root)
        main_content_frame.grid(row=0, column=0, sticky="nsew")
        main_content_frame.grid_columnconfigure(1, weight=1)
        main_content_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(main_content_frame, width=250, corner_radius=0)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        right_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        self.notebook = ctk.CTkTabview(right_frame)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        
        self.character_creator_tab = self.notebook.add("Character Creator")
        self.npc_creator_tab = self.notebook.add("NPC Creator")
        self.character_sheet_tab = self.notebook.add("Character Sheet")
        self.npc_sheet_tab = self.notebook.add("NPC Sheet")
        self.combat_sim_tab = self.notebook.add("Combat Simulator")
        self.map_editor_tab = self.notebook.add("Map Editor")
        self.map_viewer_tab = self.notebook.add("Map Viewer")
        self.rules_creator_tab = self.notebook.add("Rule Set Creator")

        self.rules_controller = RulesController(self, self.left_frame, self.rules_creator_tab)
        self.character_controller = CharacterController(self, self.character_creator_tab, self.character_sheet_tab)
        self.npc_controller = NpcController(self, self.npc_creator_tab, self.npc_sheet_tab)
        self.combat_controller = CombatController(self, self.combat_sim_tab)
        self.music_controller = MusicController(self, self.left_frame)
        
        # --- FIX: Corrected variable names for the map tabs ---
        self.map_controller = MapController(self, self.map_editor_tab, self.map_viewer_tab)

        # Enable inter-controller communication
        self.map_controller.set_source_controllers(self.character_controller, self.npc_controller)

    def run(self):
        self.root.mainloop()

    def on_rule_set_loaded(self, rule_set):
        self.character_controller.handle_rule_set_load(rule_set)
        self.npc_controller.handle_rule_set_load(rule_set)
        self.combat_controller.handle_rule_set_load(rule_set)
        self.map_controller.handle_rule_set_load(rule_set)

    def on_character_or_npc_list_changed(self):
        self.combat_controller.update_combatant_lists()
        self.character_controller.update_character_sheet_list()
        self.npc_controller.update_npc_management_list()
        self.npc_controller.update_npc_sheet_list()
        self.map_controller.update_token_placer_list()