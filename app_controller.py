import customtkinter as ctk
import tkinter as tk
import os

from rules.rules_controller import RulesController
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
from combat.combat_controller import CombatController
from music.music_controller import MusicController
from map.map_controller import MapController
from item.item_controller import ItemController

from campaign_model import CampaignModel
from main_menu_view import MainMenuView, NewCampaignDialog
from custom_dialogs import MessageBox
from rules.rules_editor_window import RulesEditorWindow
from rules.rules_model import RulesModel

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
        self.left_pane_content = None
        self.right_pane_content = None
        self.left_pane_pinned = False
        self.right_pane_pinned = False
        self.last_active_pane = "right"
        self.feature_cache = {}
        self.is_map_fullscreen = False
        self.left_pane_feature_name = None
        self.right_pane_feature_name = None
        self.pre_map_left_pane_feature = "Characters"
        self.pre_map_right_pane_feature = "Items"
        self.main_menu_view = MainMenuView(root, self)
        self.show_main_menu()

    def run(self):
        self.root.mainloop()

    def show_main_menu(self):
        if self.editor_frame:
            self.editor_frame.pack_forget()
        self.main_menu_view.pack(fill="both", expand=True)
        self.main_menu_view.tkraise()

    def _cleanup_editor_session(self):
        if self.editor_frame:
            self.editor_frame.destroy()
        self.editor_frame = None
        self.left_pane_content = None
        self.right_pane_content = None
        self.ruleset_data = None
        self.left_pane_pinned = False
        self.right_pane_pinned = False
        self.feature_cache.clear()
        self.is_map_fullscreen = False

    def _show_editor(self):
        self.main_menu_view.pack_forget()
        if self.editor_frame is None:
            self.unsaved_changes = False
            self.feature_cache = {}
            self.editor_frame = ctk.CTkFrame(self.root, fg_color="transparent")
            self.editor_frame.pack(fill="both", expand=True)
            self.editor_frame.grid_columnconfigure(1, weight=1)
            self.editor_frame.grid_rowconfigure(1, weight=1)
            header_frame = ctk.CTkFrame(self.editor_frame, corner_radius=0, height=60, border_width=1, border_color="gray25")
            header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
            header_left = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_left.pack(side="left", padx=20, pady=10)
            self.header_label = ctk.CTkLabel(header_left, text="Loading...", font=ctk.CTkFont(size=18))
            self.header_label.pack()
            header_right = ctk.CTkFrame(header_frame, fg_color="transparent")
            header_right.pack(side="right", padx=10, pady=5)
            sidebar_frame = ctk.CTkFrame(self.editor_frame, width=200, corner_radius=0, border_width=1, border_color="gray25")
            sidebar_frame.grid(row=1, column=0, sticky="nsw")
            sidebar_frame.grid_rowconfigure(0, weight=1)
            self.main_content_area = ctk.CTkFrame(self.editor_frame, fg_color="transparent")
            self.main_content_area.grid(row=1, column=1, sticky="nsew")
            self.paned_window = tk.PanedWindow(self.main_content_area, orient=tk.HORIZONTAL, sashwidth=10, bg="#2B2B2B", bd=0, relief="raised", sashrelief=tk.RAISED)
            self.left_pane_wrapper = ctk.CTkFrame(self.paned_window, fg_color="gray14", corner_radius=0, border_width=2, border_color="gray25")
            self.left_pane_wrapper.grid_columnconfigure(0, weight=1)
            self.left_pane_wrapper.grid_rowconfigure(1, weight=1)
            self.paned_window.add(self.left_pane_wrapper, minsize=400)
            left_header = ctk.CTkFrame(self.left_pane_wrapper, fg_color="gray20", corner_radius=0, height=35)
            left_header.grid(row=0, column=0, sticky="ew")
            self.left_pane_label = ctk.CTkLabel(left_header, text="Left Pane", anchor="w")
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
            self.right_pane_label = ctk.CTkLabel(right_header, text="Right Pane", anchor="w")
            self.right_pane_label.pack(side="left", padx=10, pady=5)
            self.right_pin_button = ctk.CTkButton(right_header, text="📌", width=30, fg_color="transparent", command=lambda: self.toggle_pin("right"))
            self.right_pin_button.pack(side="right", padx=5, pady=5)
            self.right_pane_frame = ctk.CTkFrame(self.right_pane_wrapper, fg_color="transparent")
            self.right_pane_frame.grid(row=1, column=0, sticky="nsew")
            self.right_pane_frame.grid_rowconfigure(0, weight=1)
            self.right_pane_frame.grid_columnconfigure(0, weight=1)
            self.fullscreen_map_frame = ctk.CTkFrame(self.main_content_area, fg_color="transparent")
            self.paned_window.pack(fill="both", expand=True)
            self.music_controller = MusicController(self, header_right)
            sidebar_nav_frame = ctk.CTkFrame(sidebar_frame, fg_color="transparent")
            sidebar_nav_frame.grid(row=0, column=0, sticky="new", padx=5, pady=5)
            page_names = ["Characters", "NPCs", "Items", "Combat", "Map Editor"]
            for name in page_names:
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
            self.load_feature_into_pane("Characters", "left")
            self.load_feature_into_pane("Items", "right")
        self.editor_frame.pack(fill="both", expand=True)
        self.editor_frame.tkraise()

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
        if feature_name == self.left_pane_feature_name or feature_name == self.right_pane_feature_name:
            return
        if self.left_pane_pinned and self.right_pane_pinned:
            MessageBox.showinfo("Info", "Both panes are pinned. Unpin one to load a new feature.", self.root)
            return
        elif self.left_pane_pinned: self.load_feature_into_pane(feature_name, "right")
        elif self.right_pane_pinned: self.load_feature_into_pane(feature_name, "left")
        elif self.last_active_pane == "right": self.load_feature_into_pane(feature_name, "left")
        else: self.load_feature_into_pane(feature_name, "right")

    def _show_context_menu(self, event, feature_name):
        context_menu = tk.Menu(self.root, tearoff=0, bg="#2B2B2B", fg="white", activebackground="#3B8ED0")
        context_menu.add_command(label=f"Open '{feature_name}' in Left Pane", command=lambda: self.load_feature_into_pane(feature_name, "left"))
        context_menu.add_command(label=f"Open '{feature_name}' in Right Pane", command=lambda: self.load_feature_into_pane(feature_name, "right"))
        context_menu.tk_popup(event.x_root, event.y_root)

    def load_feature_into_pane(self, feature_name, pane_target):
        if (pane_target == "left" and feature_name == self.left_pane_feature_name) or \
           (pane_target == "right" and feature_name == self.right_pane_feature_name):
            return
        if feature_name == "Map Editor":
            if not self.is_map_fullscreen: self._enter_fullscreen_map_mode()
            return
        elif self.is_map_fullscreen: self._exit_fullscreen_map_mode()
        
        target_frame = self.left_pane_frame if pane_target == "left" else self.right_pane_frame
        target_label = self.left_pane_label if pane_target == "left" else self.right_pane_label
        
        for widget in target_frame.winfo_children():
            widget.grid_forget()

        if pane_target == "left": self.left_pane_content = None
        else: self.right_pane_content = None

        if feature_name in self.feature_cache:
            cached_feature = self.feature_cache[feature_name]
            content = cached_feature['controller']
            feature_container = cached_feature['container']
            feature_container.grid(in_=target_frame, row=0, column=0, sticky="nsew")
        else:
            feature_container = ctk.CTkFrame(target_frame, fg_color="transparent")
            feature_container.grid(row=0, column=0, sticky="nsew")
            content = None
            if feature_name == "Characters": content = CharacterController(self, feature_container, self.current_campaign_path)
            elif feature_name == "NPCs": content = NpcController(self, feature_container, self.current_campaign_path)
            elif feature_name == "Items": content = ItemController(self, feature_container, self.current_campaign_path)
            elif feature_name == "Combat": content = CombatController(self, feature_container, self.current_campaign_path)
            if content:
                self.feature_cache[feature_name] = {'controller': content, 'container': feature_container}
                if hasattr(content, 'handle_rule_set_load') and self.ruleset_data:
                    content.handle_rule_set_load(self.ruleset_data)
        
        if content:
            target_label.configure(text=feature_name)
            if pane_target == "left":
                self.left_pane_content = content
                self.left_pane_feature_name = feature_name
            else:
                self.right_pane_content = content
                self.right_pane_feature_name = feature_name
            self.last_active_pane = pane_target

    def _enter_fullscreen_map_mode(self):
        self.pre_map_left_pane_feature = self.left_pane_feature_name
        self.pre_map_right_pane_feature = self.right_pane_feature_name
        self.paned_window.pack_forget()
        self.fullscreen_map_frame.pack(in_=self.main_content_area, fill="both", expand=True)
        self.is_map_fullscreen = True
        map_content = self.feature_cache.get("Map Editor")
        if map_content:
            map_container = map_content['container']
            map_container.pack_forget()
            map_container.pack(in_=self.fullscreen_map_frame, fill="both", expand=True)
        else:
            map_container = ctk.CTkFrame(self.fullscreen_map_frame, fg_color="transparent")
            map_container.pack(fill="both", expand=True)
            map_controller = MapController(self, map_container, self.current_campaign_path)
            self.feature_cache["Map Editor"] = {'controller': map_controller, 'container': map_container}
            if hasattr(map_controller, 'handle_rule_set_load') and self.ruleset_data:
                map_controller.handle_rule_set_load(self.ruleset_data)

    def _exit_fullscreen_map_mode(self):
        if "Map Editor" in self.feature_cache:
            self.feature_cache["Map Editor"]['container'].pack_forget()
        self.fullscreen_map_frame.pack_forget()
        self.paned_window.pack(fill="both", expand=True)
        self.is_map_fullscreen = False
        self.load_feature_into_pane(self.pre_map_left_pane_feature, "left")
        self.load_feature_into_pane(self.pre_map_right_pane_feature, "right")

    def get_loaded_controller(self, controller_class):
        for feature in self.feature_cache.values():
            if isinstance(feature['controller'], controller_class):
                return feature['controller']
        return None

    def set_dirty_flag(self, is_dirty=True):
        self.unsaved_changes = is_dirty

    def confirm_exit_to_main_menu(self):
        if not self.unsaved_changes: self.show_main_menu()
        else:
            response = MessageBox.askyesnocancel("Unsaved Changes", "You have unsaved changes...", parent=self.root)
            if response is True: MessageBox.showinfo("Save Manually", "Please use the 'Save Changes' buttons...", parent=self.root)
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
        MessageBox.showinfo("Not Implemented", "This feature is not yet available.", self.root)

    def exit_app(self):
        self.root.quit()
        self.root.destroy()
        
    def on_character_or_npc_list_changed(self):
        for feature in self.feature_cache.values():
            content = feature['controller']
            if hasattr(content, 'update_combatant_lists'): content.update_combatant_lists()
            if hasattr(content, 'update_character_sheet_list'): content.update_character_sheet_list()
            if hasattr(content, 'update_npc_management_list'): content.update_npc_management_list()
            if hasattr(content, 'update_npc_sheet_list'): content.update_npc_sheet_list()
            if hasattr(content, 'update_token_placer_list'): content.update_token_placer_list()

    def refresh_char_npc_sheet_if_loaded(self):
        char_controller = self.get_loaded_controller(CharacterController)
        if char_controller and char_controller.current_character:
            char_controller.load_character_to_sheet(refresh=True)
        npc_controller = self.get_loaded_controller(NpcController)
        if npc_controller and npc_controller.current_npc:
            npc_controller.load_npc_to_sheet(refresh=True)