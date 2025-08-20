import customtkinter as ctk
import tkinter as tk
import os
import time
import threading

from rules.rules_controller import RulesController
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
from combat.combat_controller import CombatController
from music.music_controller import MusicController
from map.map_controller import MapController
from item.item_controller import ItemController
from quest.quest_controller import QuestController
from item.item_model import ItemModel
from quest.quest_model import QuestModel
from character.character_model import CharacterModel
from npc.npc_model import NpcModel

from campaign_model import CampaignModel
from main_menu_view import MainMenuView, NewCampaignDialog
from custom_dialogs import MessageBox
from rules.rules_editor_window import RulesEditorWindow
from rules.rules_model import RulesModel
from database import Database

class AppController:
    def __init__(self, root):
        self.root = root
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.campaign_model = CampaignModel()
        self.current_campaign_path = None
        self.editor_frame = None
        self.unsaved_changes = False
        self.ruleset_data = None
        self.left_pane_pinned = False
        self.right_pane_pinned = False
        self.last_active_pane = "right"
        self.is_map_fullscreen = False
        self.data_cache = {}
        
        self.feature_cache = {}
        self.left_pane_feature_name = "Characters"
        self.right_pane_feature_name = "Items"
        self.pre_map_left_pane_feature = "Characters"
        self.pre_map_right_pane_feature = "Items"

        # --- NEW: Flag to control the background loader thread ---
        self.is_editor_active = False

        self.main_menu_view = MainMenuView(root, self)
        self.show_main_menu()

    def get_cached_data(self, key):
        return self.data_cache.get(key)

    def set_cached_data(self, key, data):
        self.data_cache[key] = data

    def clear_data_cache(self):
        self.data_cache.clear()

    def run(self):
        self.root.mainloop()

    def show_main_menu(self):
        # --- FIX: Make cleanup synchronous to prevent race conditions ---
        self._cleanup_editor_session()

    
        self.main_menu_view.pack(fill="both", expand=True)
        self.main_menu_view.tkraise()

    def _cleanup_editor_session(self):
        # This function is now fast because views lazy-load their most complex parts.
        self.is_editor_active = False # Stop the background thread if it's running

        if self.editor_frame:
            # We don't need to iterate the cache; destroying the parent frame does it all.
            self.editor_frame.destroy()
            self.editor_frame = None

        # Reset all state variables
        self.ruleset_data = None
        self.current_campaign_path = None
        self.left_pane_pinned = False
        self.right_pane_pinned = False
        self.feature_cache = {}
        self.clear_data_cache()
        self.is_map_fullscreen = False

    def _show_editor(self):
        self.main_menu_view.pack_forget()
        
        if self.editor_frame is None:
            self.unsaved_changes = False
            self.editor_frame = ctk.CTkFrame(self.root, fg_color="transparent")
            
            self.editor_frame.grid_columnconfigure(1, weight=1)
            self.editor_frame.grid_rowconfigure(1, weight=1)
            
            header_frame = ctk.CTkFrame(self.editor_frame, corner_radius=0, height=150, border_width=1, border_color="gray25")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
            header_left = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_left.pack(side="left", padx=20, pady=10)
            self.header_label = ctk.CTkLabel(header_left, text="Loading Campaign...", font=ctk.CTkFont(size=18))
            self.header_label.pack()
            
            ctk.CTkFrame(self.editor_frame, width=200, corner_radius=0, border_width=1, border_color="gray25").grid(row=1, column=0, sticky="nsw")
            ctk.CTkFrame(self.editor_frame, fg_color="transparent").grid(row=1, column=1, sticky="nsew")
            
            self.editor_frame.pack(fill="both", expand=True)
            self.editor_frame.tkraise()
            
            self.root.after(50, self._finish_editor_setup)

    def _finish_editor_setup(self):
        # --- FIX: Signal that a new, valid editor session has started ---
        self.is_editor_active = True
        
        print("Starting deferred editor setup")
        startTime = time.time()

        header_frame = self.editor_frame.winfo_children()[0]
        sidebar_frame = self.editor_frame.winfo_children()[1]
        self.main_content_area = self.editor_frame.winfo_children()[2]
        
        self.main_content_area.grid_columnconfigure(0, weight=1)
        self.main_content_area.grid_rowconfigure(0, weight=1)
        self.paned_window = tk.PanedWindow(self.main_content_area, orient=tk.HORIZONTAL, sashwidth=10, bg="#2B2B2B", bd=0, relief="raised", sashrelief=tk.RAISED)
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        self.left_pane_wrapper = ctk.CTkFrame(self.paned_window, fg_color="gray14", corner_radius=0, border_width=2, border_color="gray25")
        self.left_pane_wrapper.grid_columnconfigure(0, weight=1)
        self.left_pane_wrapper.grid_rowconfigure(1, weight=1)
        self.paned_window.add(self.left_pane_wrapper, minsize=400)
        left_header = ctk.CTkFrame(self.left_pane_wrapper, fg_color="gray20", corner_radius=0, height=35)
        left_header.grid(row=0, column=0, sticky="ew")
        self.left_pane_label = ctk.CTkLabel(left_header, text="Characters", anchor="w")
        self.left_pane_label.pack(side="left", padx=10, pady=5)
        self.left_pin_button = ctk.CTkButton(left_header, text="📌", width=30, fg_color="transparent", command=lambda: self.toggle_pin("left"))
        self.left_pin_button.pack(side="right", padx=5, pady=5)
        self.left_pane_frame = ctk.CTkFrame(self.left_pane_wrapper, fg_color="transparent")
        self.left_pane_frame.grid(row=1, column=0, sticky="nsew")
        self.left_pane_frame.grid_rowconfigure(0, weight=1)
        self.left_pane_frame.grid_columnconfigure(0, weight=1)
        self.right_pane_wrapper = ctk.CTkFrame(self.paned_window, fg_color="gray14", corner_radius=0, border_width=2, border_color="gray25")
        self.right_pane_wrapper.grid_columnconfigure(0, weight=1)
        self.right_pane_wrapper.grid_rowconfigure(1, weight=1)
        self.paned_window.add(self.right_pane_wrapper, minsize=400)
        right_header = ctk.CTkFrame(self.right_pane_wrapper, fg_color="gray20", corner_radius=0, height=35)
        right_header.grid(row=0, column=0, sticky="ew")
        self.right_pane_label = ctk.CTkLabel(right_header, text="Items", anchor="w")
        self.right_pane_label.pack(side="left", padx=10, pady=5)
        self.right_pin_button = ctk.CTkButton(right_header, text="📌", width=30, fg_color="transparent", command=lambda: self.toggle_pin("right"))
        self.right_pin_button.pack(side="right", padx=5, pady=5)
        self.right_pane_frame = ctk.CTkFrame(self.right_pane_wrapper, fg_color="transparent")
        self.right_pane_frame.grid(row=1, column=0, sticky="nsew")
        self.right_pane_frame.grid_rowconfigure(0, weight=1)
        self.right_pane_frame.grid_columnconfigure(0, weight=1)
        self.fullscreen_map_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
        self.fullscreen_map_frame.grid_rowconfigure(0, weight=1)
        self.fullscreen_map_frame.grid_columnconfigure(0, weight=1)

        header_right = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_right.pack(side="right", padx=10, pady=5)
        self.music_controller = MusicController(self, header_right)
        
        sidebar_frame.grid_rowconfigure(0, weight=1)
        sidebar_nav_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
        sidebar_nav_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
        
        self.all_feature_names = ["Characters", "NPCs", "Items", "Quests", "Combat", "Map Editor"]
        for name in self.all_feature_names:
            button = ctk.CTkButton(sidebar_nav_frame, text=name, corner_radius=0, fg_color="transparent", height=40, anchor="w")
            button.pack(fill="x")
            button.bind("<Button-1>", lambda event, n=name: self.load_feature(n))
            button.bind("<Button-3>", lambda event, n=name: self._show_context_menu(event, n))
        ctk.CTkButton(sidebar_frame, text="< Back to Main Menu", command=self.confirm_exit_to_main_menu, fg_color="transparent", border_width=1, border_color="gray50", height=40).grid(row=1, column=0, sticky="sew", padx=10, pady=10)
        
        ruleset_name = self.campaign_model.get_campaign_ruleset(os.path.basename(self.current_campaign_path))
        if ruleset_name:
            rules_model = RulesModel()
            self.ruleset_data = rules_model.load_rule_set(ruleset_name)
            if self.ruleset_data:
                campaign_name = os.path.basename(self.current_campaign_path)
                self.header_label.configure(text=f"{campaign_name}  |  Ruleset: {ruleset_name}")
            else:
                MessageBox.showerror("Error", f"Failed to load required ruleset '{ruleset_name}'.", self.root)
                self.show_main_menu()
                return
        
        self.root.after(100, lambda: self.paned_window.sash_place(0, self.paned_window.winfo_width() // 2, 0))
        
        self._redisplay_panes(None, None)
        
        loader_thread = threading.Thread(target=self._background_preload_controllers, daemon=True)
        loader_thread.start()

        print(f"Deferred rendering done in {time.time() - startTime:.4f} seconds")

    def _background_preload_controllers(self):
        print("\n--- Starting background controller pre-loading ---")
        time.sleep(0.5)

        features_to_preload = [
            name for name in self.all_feature_names 
            if name not in (self.left_pane_feature_name, self.right_pane_feature_name)
        ]

        for name in features_to_preload:
            # --- FIX: Check the flag before doing any work ---
            if not self.is_editor_active:
                print("  - Editor closed. Aborting background pre-load.")
                break

            if name in self.feature_cache: continue
            try:
                start_time = time.time()
                controller = self._create_feature_by_name(name, None)
                self.feature_cache[name] = {'controller': controller, 'frame': None}
                
                time.sleep(0.1)
                print(f"  - Background pre-loaded '{name}' controller in {time.time() - start_time:.4f}s")
            except Exception as e:
                print(f"  - [ERROR] Failed to background pre-load '{name}': {e}")
        
        if self.is_editor_active:
            print("--- Background pre-loading complete ---\n")

    def _create_feature_by_name(self, feature_name, parent_frame):
        content = None
        if feature_name == "Characters": content = CharacterController(self, parent_frame, self.current_campaign_path)
        elif feature_name == "NPCs": content = NpcController(self, parent_frame, self.current_campaign_path)
        elif feature_name == "Items": content = ItemController(self, parent_frame, self.current_campaign_path)
        elif feature_name == "Quests": content = QuestController(self, parent_frame, self.current_campaign_path)
        elif feature_name == "Combat": content = CombatController(self, parent_frame, self.current_campaign_path)
        elif feature_name == "Map Editor": content = MapController(self, parent_frame, self.current_campaign_path)
        return content

    def _get_or_create_feature(self, feature_name):
        if feature_name not in self.feature_cache:
            print(f"Loading feature '{feature_name}' on demand (UI thread)...")
            controller = self._create_feature_by_name(feature_name, None)
            self.feature_cache[feature_name] = {'controller': controller, 'frame': None}

        feature = self.feature_cache[feature_name]

        if feature['frame'] is None:
            print(f"Creating UI frame for '{feature_name}'...")
            frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
            
            controller = feature['controller']
            controller.view.parent_frame = frame
            controller.view.setup_ui(controller)

            if hasattr(controller, 'on_ui_ready'):
                controller.on_ui_ready()

            if self.ruleset_data and hasattr(controller, 'handle_rule_set_load'):
                controller.handle_rule_set_load(self.ruleset_data)

            feature['frame'] = frame
        
        return feature

    def _reload_character_cache(self):
        if not self.ruleset_data: return
        char_cache_key = f"characters_models_{self.ruleset_data['name']}"
        char_models = CharacterModel.get_all_for_ruleset(self.current_campaign_path, self.ruleset_data['name'])
        self.set_cached_data(char_cache_key, sorted(char_models, key=lambda m: m.name))

    def _reload_npc_cache(self):
        if not self.ruleset_data: return
        npc_cache_key = f"npcs_models_{self.ruleset_data['name']}"
        npc_models = NpcModel.get_all_for_ruleset(self.current_campaign_path, self.ruleset_data['name'])
        self.set_cached_data(npc_cache_key, sorted(npc_models, key=lambda m: m.name))

    def toggle_pin(self, pane):
        if pane == "left":
            self.left_pane_pinned = not self.left_pane_pinned
            self.left_pin_button.configure(fg_color="#3B8ED0" if self.left_pane_pinned else "transparent")
            if self.left_pane_pinned and self.right_pane_pinned:
                self.right_pane_pinned = False
                self.right_pin_button.configure(fg_color="transparent")
        else:
            self.right_pane_pinned = not self.right_pane_pinned
            self.right_pin_button.configure(fg_color="#3B8ED0" if self.right_pane_pinned else "transparent")
            if self.right_pane_pinned and self.left_pane_pinned:
                self.left_pane_pinned = False
                self.left_pin_button.configure(fg_color="transparent")

    def load_feature(self, feature_name):
        if self.is_map_fullscreen and feature_name != "Map Editor":
            self._exit_fullscreen_map_mode()

        if self.left_pane_pinned and self.right_pane_pinned:
            MessageBox.showinfo("Info", "Both panes are pinned. Unpin one to load a new feature.", self.root)
            return

        target_pane = None
        if self.left_pane_pinned: target_pane = "right"
        elif self.right_pane_pinned: target_pane = "left"
        else:
            if feature_name == self.left_pane_feature_name: target_pane = "left"
            elif feature_name == self.right_pane_feature_name: target_pane = "right"
            elif self.last_active_pane == "right": target_pane = "left"
            else: target_pane = "right"
        
        self.load_feature_into_pane(feature_name, target_pane)

    def _show_context_menu(self, event, feature_name):
        context_menu = tk.Menu(self.root, tearoff=0, bg="#2B2B2B", fg="white", activebackground="#3B8ED0")
        context_menu.add_command(label=f"Open '{feature_name}' in Left Pane", command=lambda: self.load_feature_into_pane(feature_name, "left"))
        context_menu.add_command(label=f"Open '{feature_name}' in Right Pane", command=lambda: self.load_feature_into_pane(feature_name, "right"))
        context_menu.tk_popup(event.x_root, event.y_root)

    def load_feature_into_pane(self, feature_name, pane_target):
        if feature_name == "Map Editor":
            if not self.is_map_fullscreen: self._enter_fullscreen_map_mode()
            return
        
        if self.is_map_fullscreen:
            self._exit_fullscreen_map_mode()

        prev_left, prev_right = self.left_pane_feature_name, self.right_pane_feature_name
        new_left, new_right = prev_left, prev_right

        if pane_target == "left":
            if feature_name == prev_right: new_left, new_right = prev_right, prev_left
            else: new_left = feature_name
        else:
            if feature_name == prev_left: new_left, new_right = prev_right, prev_left
            else: new_right = feature_name
        
        if (new_left, new_right) != (prev_left, prev_right):
            self.left_pane_feature_name, self.right_pane_feature_name = new_left, new_right
            self._redisplay_panes(prev_left, prev_right)

        self.last_active_pane = pane_target

    def _redisplay_panes(self, prev_left_feature=None, prev_right_feature=None):
        new_left, new_right = self.left_pane_feature_name, self.right_pane_feature_name

        if prev_left_feature != new_left:
            if prev_left_feature and prev_left_feature in self.feature_cache and self.feature_cache[prev_left_feature]['frame']:
                self.feature_cache[prev_left_feature]['frame'].grid_forget()
            
            feature = self._get_or_create_feature(new_left)
            feature['frame'].grid(in_=self.left_pane_frame, row=0, column=0, sticky="nsew")
            self.left_pane_label.configure(text=new_left)

        if prev_right_feature != new_right:
            if prev_right_feature and prev_right_feature in self.feature_cache and self.feature_cache[prev_right_feature]['frame']:
                self.feature_cache[prev_right_feature]['frame'].grid_forget()

            feature = self._get_or_create_feature(new_right)
            feature['frame'].grid(in_=self.right_pane_frame, row=0, column=0, sticky="nsew")
            self.right_pane_label.configure(text=new_right)

    def _enter_fullscreen_map_mode(self):
        self.pre_map_left_pane_feature, self.pre_map_right_pane_feature = self.left_pane_feature_name, self.right_pane_feature_name
        
        if self.left_pane_feature_name in self.feature_cache and self.feature_cache[self.left_pane_feature_name]['frame']:
            self.feature_cache[self.left_pane_feature_name]['frame'].grid_forget()
        if self.right_pane_feature_name in self.feature_cache and self.feature_cache[self.right_pane_feature_name]['frame']:
            self.feature_cache[self.right_pane_feature_name]['frame'].grid_forget()

        self.paned_window.grid_forget()
        self.fullscreen_map_frame.grid(row=0, column=0, sticky="nsew")
        self.is_map_fullscreen = True
        
        map_feature = self._get_or_create_feature("Map Editor")
        map_feature['frame'].grid(in_=self.fullscreen_map_frame, row=0, column=0, sticky="nsew")

    def _exit_fullscreen_map_mode(self):
        if "Map Editor" in self.feature_cache and self.feature_cache["Map Editor"]['frame']:
            self.feature_cache["Map Editor"]['frame'].grid_forget()

        self.fullscreen_map_frame.grid_forget()
        self.paned_window.grid(row=0, column=0, sticky="nsew")
        self.is_map_fullscreen = False
        
        prev_left, prev_right = self.left_pane_feature_name, self.right_pane_feature_name
        self.left_pane_feature_name, self.right_pane_feature_name = self.pre_map_left_pane_feature, self.pre_map_right_pane_feature
        self._redisplay_panes(prev_left, prev_right)

    def get_loaded_controller(self, controller_class):
        feature_map = {
            CharacterController: "Characters", NpcController: "NPCs",
            ItemController: "Items", QuestController: "Quests",
            CombatController: "Combat", MapController: "Map Editor"
        }
        feature_name = feature_map.get(controller_class)
        if not feature_name: return None

        if feature_name not in self.feature_cache:
            return None
        
        return self.feature_cache[feature_name]['controller']

    def set_dirty_flag(self, is_dirty=True):
        self.unsaved_changes = is_dirty

    def confirm_exit_to_main_menu(self):
        if not self.unsaved_changes:
            self.show_main_menu()
            return

        response = MessageBox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Save them before exiting?", parent=self.root)
        
        if response is True:
            MessageBox.showinfo("Save Manually", "Please use the 'Save Changes' buttons in the relevant panes to save your work.", parent=self.root)
        elif response is False:
            self.unsaved_changes = False
            self.show_main_menu()
            
    def new_game_flow(self):
        rules_model = RulesModel()
        rulesets = rules_model.get_all_rule_sets()
        if not rulesets:
            MessageBox.showerror("Error", "No rule sets found...", self.root)
            return
        dialog = NewCampaignDialog(parent=self.root, rulesets=rulesets)
        result = dialog.get_input()
        if not result: return
        campaign_name, ruleset_name = result
        self._cleanup_editor_session()
        path = self.campaign_model.create_campaign(campaign_name, ruleset_name)
        if path:
            self.current_campaign_path = path
            self._show_editor()
        else:
            MessageBox.showerror("Error", f"A campaign named '{campaign_name}' already exists.", self.root)

    def load_game_flow(self, campaign_name):
        if not campaign_name:
            MessageBox.showerror("Error", "Please select a campaign to load.", self.root)
            return
        
        self._cleanup_editor_session()
        
        self.current_campaign_path = os.path.join(self.campaign_model.base_dir, campaign_name)
        
        if os.path.exists(self.current_campaign_path):
            self._show_editor()
        else:
            MessageBox.showerror("Error", f"Could not find campaign data for '{campaign_name}'.", self.root)
            self.current_campaign_path = None

    def show_ruleset_creator_standalone(self):
        ruleset_window = RulesEditorWindow(self.root)
        standalone_rules_controller = RulesController(self)
        standalone_rules_controller.set_view(ruleset_window)
        ruleset_window.set_controller(standalone_rules_controller)

    def show_placeholder_message(self):
        MessageBox.showinfo("Not Implemented", "This feature is not yet available.", self.root)

    def exit_app(self):
        self._cleanup_editor_session()
        self.root.quit()
        self.root.destroy()
        
    def on_character_or_npc_list_changed(self):
        self._reload_character_cache()
        self._reload_npc_cache()

        for feature in self.feature_cache.values():
            if feature['controller']:
                content = feature['controller']
                if hasattr(content, 'update_combatant_lists'): content.update_combatant_lists()
                if hasattr(content, 'update_character_sheet_list'): content.update_character_sheet_list()
                if hasattr(content, 'update_npc_management_list'): content.update_npc_management_list()
                if hasattr(content, 'update_npc_sheet_list'): content.update_npc_sheet_list()
                if hasattr(content, 'update_token_placer_list'): content.update_token_placer_list()

    def refresh_char_npc_sheet_if_loaded(self):
        if "Characters" in self.feature_cache:
            char_controller = self.get_loaded_controller(CharacterController)
            if char_controller and char_controller.current_character:
                char_controller.load_character_to_sheet(refresh=True)
        
        if "NPCs" in self.feature_cache:
            npc_controller = self.get_loaded_controller(NpcController)
            if npc_controller and npc_controller.current_npc:
                npc_controller.load_npc_to_sheet(refresh=True)