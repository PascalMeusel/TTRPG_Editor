from tkinter import messagebox
from .map_model import MapModel
from .map_view import MapView
from .map_generation.map_generation_controller import MapGenerationController
from custom_dialogs import MessageBox
from character.character_controller import CharacterController
from npc.npc_controller import NpcController
import customtkinter as ctk
import math
import os

    
class MapController:
    """Controller for the self-contained Map feature."""
    def __init__(self, app_controller, parent_frame, campaign_path):
        self.app_controller = app_controller
        self.view = MapView(parent_frame)
        self.campaign_path = campaign_path
        self.model = None
        self.current_level = 0
        self.current_tool = "select"
        self.editor_start_pos = None
        self.selected_tokens = []
        self.token_being_dragged = None
        self.drag_start_pos = {}
        self.drag_preview_pos = None

  

    def _initialize_blank_state(self):
        self.model = None
        self.current_level = 0
        self.selected_tokens = []
        self.view.clear_all_canvases()
        if hasattr(self.view, 'map_name_entry'):
            self.view.map_name_entry.delete(0, 'end')
        self.view.update_level_controls(None, 0)
        self.refresh_map_list()

    def handle_rule_set_load(self, rule_set):
        self.update_token_placer_list()

    def show_new_map_dialog(self):
        if self.model and self.app_controller.unsaved_changes:
            if not MessageBox.askyesno("Unsaved Changes", "This will erase the current unsaved map design. Are you sure?", self.view.parent_frame):
                return
        gen_controller = MapGenerationController(parent_view=self.view.parent_frame)
        map_data = gen_controller.show_generation_dialog()
        if map_data:
            self.load_new_map_data(map_data)

    def load_new_map_data(self, map_data):
        self.model = MapModel(self.campaign_path, name="New Generated Map", width=map_data['width'], height=map_data['height'], grid_scale=map_data['grid_scale'])
        self.model.map_type = map_data['map_type']
        self.model.levels = map_data['levels']
        self.current_level = 0
        self.selected_tokens = []
        self.view.map_name_entry.delete(0, 'end')
        self.view.map_name_entry.insert(0, self.model.name)
        self.view.update_dimension_fields(self.model)
        self.set_tool("select")
        self._sync_and_redraw_all_views()
        self.app_controller.set_dirty_flag(True)

    def change_level(self, delta):
        if not self.model or self.model.map_type != 'inside': return
        new_level = self.current_level + delta
        if new_level in self.model.levels:
            self.current_level = new_level
            self.selected_tokens = []
            self._sync_and_redraw_all_views()
        else:
            if MessageBox.askyesno("Create New Level?", f"Level {new_level} does not exist. Would you like to create a new blank level?", self.view.parent_frame):
                self.model.levels[new_level] = {'elements': [], 'tokens': [], 'landmarks': []}
                self.model.clear_map_level(new_level)
                self.current_level = new_level
                self.selected_tokens = []
                self._sync_and_redraw_all_views()
                self.app_controller.set_dirty_flag(True)

    def update_token_placer_list(self):
        char_controller = self.app_controller.get_loaded_controller(CharacterController)
        npc_controller = self.app_controller.get_loaded_controller(NpcController)
        pc_list, npc_list = [], []
        if char_controller:
            pc_models = char_controller.get_character_list()
            pc_list = [f"PC: {model.name}" for model in pc_models]
        if npc_controller:
            npc_models = npc_controller.get_npc_list()
            npc_list = [f"NPC: {model.name}" for model in npc_models]
        self.view.update_token_placer_list(pc_list + npc_list)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        if tool_name in ["brush", "rect"]:
            self.selected_tokens = []
            if self.model: self._redraw_viewer_canvas()

    # --- FIX: Restored missing canvas event handlers ---
    def on_editor_canvas_press(self, event):
        if not self.model: return
        self.editor_start_pos = (event.x, event.y)
        if self.current_tool == "landmark":
            landmark_text = self.view.landmark_text_entry.get()
            if not landmark_text:
                MessageBox.showwarning("Warning", "Please enter text for the landmark first.", self.view.parent_frame)
                return
            x_grid, y_grid = event.x // self.model.grid_size, event.y // self.model.grid_size
            self.model.add_landmark(x_grid, y_grid, landmark_text, self.current_level)
            self._sync_and_redraw_all_views()
            self.app_controller.set_dirty_flag()
            self.set_tool("select")

    def on_editor_canvas_drag(self, event):
        if not self.model: return
        if self.current_tool == "brush":
            x, y = event.x // self.model.grid_size, event.y // self.model.grid_size
            self.model.add_element({'type': 'rect', 'coords': (x, y, x + 1, y + 1), 'color': self.view.color_var.get()}, self.current_level)
            self.view.draw_editor_canvas(self.model, self.current_level)
            self.app_controller.set_dirty_flag()

    def on_editor_canvas_release(self, event):
        if not self.model: return
        if self.current_tool == "rect" and self.editor_start_pos:
            x0 = min(self.editor_start_pos[0], event.x) // self.model.grid_size
            y0 = min(self.editor_start_pos[1], event.y) // self.model.grid_size
            x1 = max(self.editor_start_pos[0], event.x) // self.model.grid_size
            y1 = max(self.editor_start_pos[1], event.y) // self.model.grid_size
            self.model.add_element({'type': 'rect', 'coords': (x0, y0, x1 + 1, y1 + 1), 'color': self.view.color_var.get()}, self.current_level)
            self._sync_and_redraw_all_views()
            self.app_controller.set_dirty_flag()
        self.editor_start_pos = None

    def on_viewer_canvas_press(self, event):
        if not self.model: return
        x_grid, y_grid = event.x // self.model.grid_size, event.y // self.model.grid_size
        if self.current_tool == "place_token":
            token_str = self.view.token_placer_list.get()
            if not token_str or "No tokens" in token_str or "Load" in token_str: return
            token_type, token_name = token_str.split(': ', 1)
            if self.model.add_token(token_name.strip(), token_type, x_grid, y_grid, self.current_level):
                self._redraw_viewer_canvas()
                self.app_controller.set_dirty_flag()
            else:
                MessageBox.showwarning("Warning", f"Token '{token_name.strip()}' is already on the map.", self.view.parent_frame)
            self.set_tool("select")
            return
        clicked_token = self.model.get_token_at(x_grid, y_grid, self.current_level)
        if clicked_token:
            self.token_being_dragged = clicked_token
            self.drag_start_pos[clicked_token['name']] = (clicked_token['x'], clicked_token['y'])
            if clicked_token not in self.selected_tokens:
                self.selected_tokens = [clicked_token]
        else:
            self.selected_tokens = []
        self._update_distance_display()
        self._redraw_viewer_canvas()

    def on_viewer_canvas_ctrl_press(self, event):
        if not self.model: return
        x_grid, y_grid = event.x // self.model.grid_size, event.y // self.model.grid_size
        clicked_token = self.model.get_token_at(x_grid, y_grid, self.current_level)
        if clicked_token:
            if clicked_token in self.selected_tokens:
                self.selected_tokens.remove(clicked_token)
            else:
                self.selected_tokens.append(clicked_token)
            self._update_distance_display()
            self._redraw_viewer_canvas()

    def on_viewer_canvas_drag(self, event):
        if not self.token_being_dragged: return
        mouse_x, mouse_y = event.x, event.y
        try: move_dist_m = float(self.view.movement_entry.get() or 0)
        except ValueError: move_dist_m = 0
        start_grid_x, start_grid_y = self.drag_start_pos[self.token_being_dragged['name']]
        start_pixel_x = (start_grid_x + 0.5) * self.model.grid_size
        start_pixel_y = (start_grid_y + 0.5) * self.model.grid_size
        if move_dist_m > 0:
            dist_moved_pixels = math.sqrt((mouse_x - start_pixel_x)**2 + (mouse_y - start_pixel_y)**2)
            max_dist_pixels = (move_dist_m / self.model.grid_scale) * self.model.grid_size
            if dist_moved_pixels > max_dist_pixels and dist_moved_pixels > 0:
                angle = math.atan2(mouse_y - start_pixel_y, mouse_x - start_pixel_x)
                clamped_x = start_pixel_x + max_dist_pixels * math.cos(angle)
                clamped_y = start_pixel_y + max_dist_pixels * math.sin(angle)
                self.drag_preview_pos = (clamped_x, clamped_y)
            else:
                self.drag_preview_pos = (mouse_x, mouse_y)
        else:
            self.drag_preview_pos = (mouse_x, mouse_y)
        self._redraw_viewer_canvas()

    def on_viewer_canvas_release(self, event):
        if self.token_being_dragged and self.drag_preview_pos:
            final_x = int(self.drag_preview_pos[0] // self.model.grid_size)
            final_y = int(self.drag_preview_pos[1] // self.model.grid_size)
            if (self.token_being_dragged['x'], self.token_being_dragged['y']) != (final_x, final_y):
                self.model.move_token(self.token_being_dragged['name'], final_x, final_y, self.current_level)
                self.app_controller.set_dirty_flag()
        self.token_being_dragged = None
        self.drag_start_pos = {}
        self.drag_preview_pos = None
        self._redraw_viewer_canvas()

    def _update_distance_display(self):
        if len(self.selected_tokens) == 2:
            dist_grid = self.model.calculate_distance(self.selected_tokens[0], self.selected_tokens[1])
            dist_m = dist_grid * self.model.grid_scale
            self.view.distance_label.configure(text=f"{dist_m:.1f} m")
        else:
            self.view.distance_label.configure(text="-")

    def _sync_and_redraw_all_views(self):
        if not self.model: return
        self.view.update_level_controls(self.model, self.current_level)
        self.view.draw_editor_canvas(self.model, self.current_level)
        self.view.draw_static_background(self.model, self.current_level)
        self.view.draw_viewer_canvas(self.model, self)

    def _redraw_editor_view_only(self):
        if not self.model: return
        self.view.update_level_controls(self.model, self.current_level)
        self.view.draw_editor_canvas(self.model, self.current_level)
        
    def _redraw_viewer_canvas(self):
        if not self.model: return
        self.view.draw_viewer_canvas(self.model, self)

    def save_map(self):
        if not self.model:
            MessageBox.showerror("Error", "There is no map to save.", self.view.parent_frame)
            return
        map_name = self.view.map_name_entry.get()
        if not map_name or map_name == "New Generated Map":
            MessageBox.showerror("Error", "Please enter a unique name for the map.", self.view.parent_frame)
            return
        self.model.name = map_name
        try:
            self.model.grid_scale = float(self.view.scale_entry.get())
        except ValueError:
            MessageBox.showerror("Error", "Invalid grid scale.", self.view.parent_frame)
            return
        self.model.save_map_data()
        png_path = os.path.join(self.model.maps_dir, f"{self.model.name.lower().replace(' ', '_')}.png")
        if not self.view.save_canvas_to_png(png_path, self.model, self.current_level):
            MessageBox.showerror("Error", "Failed to save map image.", self.view.parent_frame)
            return
        self.app_controller.set_dirty_flag(False)
        self.refresh_map_list()
        MessageBox.showinfo("Success", f"Map '{self.model.name}' has been saved.", self.view.parent_frame)

    def refresh_map_list(self):
        maps = MapModel.get_all_maps(self.campaign_path)
        self.view.update_map_list(maps)
        
    def load_map_for_viewing(self, map_name):
        if "Select a saved map..." in map_name:
            self._initialize_blank_state()
            return
        loaded_model = MapModel.load(self.campaign_path, map_name)
        if loaded_model:
            self.model = loaded_model
            self.current_level = 0
            self.selected_tokens = []
            self.view.map_name_entry.delete(0, 'end')
            self.view.map_name_entry.insert(0, self.model.name)
            self.view.update_dimension_fields(self.model)
            self.set_tool("select")
            self._sync_and_redraw_all_views()
            self.app_controller.set_dirty_flag(False)
        else:
            MessageBox.showerror("Error", f"Could not load map data for '{map_name}'.", self.view.parent_frame)

    def delete_selected_tokens(self):
        if not self.selected_tokens:
            MessageBox.showinfo("Info", "No tokens selected to delete.", self.view.parent_frame)
            return
        if MessageBox.askyesno("Confirm", f"Are you sure you want to delete {len(self.selected_tokens)} token(s)?", self.view.parent_frame):
            for token in self.selected_tokens:
                self.model.delete_token(token['name'], self.current_level)
            self.selected_tokens = []
            self._update_distance_display()
            self._redraw_viewer_canvas()
            self.app_controller.set_dirty_flag(True)