from custom_dialogs import MessageBox
from .map_model import MapModel
from .map_view import MapView
import math
import os

class MapController:
    """Controller for all map interactions with a fixed grid size."""
    def __init__(self, app_controller, editor_tab, viewer_tab, campaign_path):
        self.app_controller = app_controller
        self.view = MapView(editor_tab, viewer_tab) # Correctly passes arguments
        self.campaign_path = campaign_path
        self.model = MapModel(self.campaign_path)
        self.current_tool = "select"
        self.editor_start_pos = None
        self.selected_tokens = []
        self.token_being_dragged = None
        self.drag_start_pos = {}
        self.drag_preview_pos = None
        self.char_controller = None
        self.npc_controller = None

        self.view.setup_editor_ui(self)
        self.view.setup_viewer_ui(self)
        self._initialize_blank_map()
        self.refresh_map_list()

    def _initialize_blank_map(self):
        """Silently creates a new blank map model with default 50x50 dimensions."""
        self.model = MapModel(self.campaign_path)
        self.model.clear_map()
        self.view.map_name_entry.delete(0, 'end')
        self.view.map_name_entry.insert(0, "New Blank Map")
        self.view.update_dimension_fields(self.model)
        self._redraw_all()

    def new_map(self):
        """Creates a new 50x50 map, asking for confirmation only if the map has been modified."""
        # --- FIX: Only ask for confirmation if the map is not blank. ---
        # A blank map only has 1 element (the background rectangle).
        if len(self.model.map_elements) > 1:
            if not MessageBox.askyesno("Confirm", "This will erase the current map design. Are you sure?", parent=self.view.editor_tab):
                return
                
        try:
            scale = float(self.view.scale_entry.get())
            if scale <= 0: raise ValueError("Scale must be positive")
        except ValueError:
            MessageBox.showerror("Error", "Invalid grid scale. Please enter a positive number.", parent=self.view.editor_tab); return
            
        self.model = MapModel(self.campaign_path, grid_scale=scale)
        self.model.clear_map()
        self.view.map_name_entry.delete(0, 'end')
        self.view.map_name_entry.insert(0, "New Custom Map")
        self.set_tool("select")
        self._redraw_all()
        # A new map has no unsaved changes yet.
        self.app_controller.set_dirty_flag(False)

    def set_source_controllers(self, char_controller, npc_controller):
        self.char_controller = char_controller
        self.npc_controller = npc_controller

    def handle_rule_set_load(self, rule_set):
        self.update_token_placer_list()

    def update_token_placer_list(self):
        if not self.char_controller or not self.npc_controller: return
        pc_list = [f"PC: {name}" for name in self.char_controller.get_character_list()]
        npc_list = [f"NPC: {name}" for name in self.npc_controller.get_npc_list()]
        self.view.update_token_placer_list(pc_list + npc_list)

    def set_tool(self, tool_name):
        self.current_tool = tool_name
        if tool_name in ["brush", "rect"]:
            self.selected_tokens = []
            self._redraw_viewer_canvas()

    def on_editor_canvas_press(self, event):
        self.editor_start_pos = (event.x, event.y)

    def on_editor_canvas_drag(self, event):
        if self.current_tool == "brush":
            x, y = event.x // self.model.grid_size, event.y // self.model.grid_size
            self.model.add_element({'type': 'rect', 'coords': (x, y, x + 1, y + 1), 'color': self.view.color_var.get()})
            self.view.draw_editor_canvas(self.model)
            self.app_controller.set_dirty_flag()

    def on_editor_canvas_release(self, event):
        if self.current_tool == "rect" and self.editor_start_pos:
            x0 = min(self.editor_start_pos[0], event.x) // self.model.grid_size
            y0 = min(self.editor_start_pos[1], event.y) // self.model.grid_size
            x1 = max(self.editor_start_pos[0], event.x) // self.model.grid_size
            y1 = max(self.editor_start_pos[1], event.y) // self.model.grid_size
            self.model.add_element({'type': 'rect', 'coords': (x0, y0, x1 + 1, y1 + 1), 'color': self.view.color_var.get()})
            self.view.draw_editor_canvas(self.model)
            self.app_controller.set_dirty_flag()
        self.editor_start_pos = None

    def on_viewer_canvas_press(self, event):
        x_grid, y_grid = event.x // self.model.grid_size, event.y // self.model.grid_size
        if self.current_tool == "place_token":
            token_str = self.view.token_placer_list.get()
            if not token_str or "No tokens" in token_str: return
            token_type, token_name = token_str.split(': ', 1)
            if self.model.add_token(token_name, token_type, x_grid, y_grid):
                self._redraw_viewer_canvas()
                self.app_controller.set_dirty_flag()
            else: MessageBox.showwarning("Warning", f"Token '{token_name}' is already on the map.", parent=self.view.editor_tab)
            self.set_tool("select")
            return
        
        clicked_token = self.model.get_token_at(x_grid, y_grid)
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
        x_grid, y_grid = event.x // self.model.grid_size, event.y // self.model.grid_size
        clicked_token = self.model.get_token_at(x_grid, y_grid)
        if clicked_token:
            if clicked_token in self.selected_tokens: self.selected_tokens.remove(clicked_token)
            else: self.selected_tokens.append(clicked_token)
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
                self.model.move_token(self.token_being_dragged['name'], final_x, final_y)
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
        else: self.view.distance_label.configure(text="-")

    def _redraw_all(self):
        self.view.draw_editor_canvas(self.model)
        self.view.draw_static_background(self.model.name, self.model)
        self.view.draw_viewer_canvas(self.model, self)

    def _redraw_viewer_canvas(self):
        self.view.draw_viewer_canvas(self.model, self)

    def generate_dungeon(self):
        """Generates a dungeon, asking for confirmation only if the map has been modified."""
        # --- FIX: Only ask for confirmation if the map is not blank. ---
        if len(self.model.map_elements) > 1:
            if not MessageBox.askyesno("Confirm", "This will erase the current map design. Are you sure?", parent=self.view.editor_tab):
                return

        try:
            scale = float(self.view.scale_entry.get())
            if scale <= 0: raise ValueError("Scale must be positive")
        except ValueError:
            MessageBox.showerror("Error", "Invalid grid scale.", parent=self.view.editor_tab); return
            
        self.model = MapModel(self.campaign_path, grid_scale=scale) # Generates a 50x50 map
        self.model.generate_dungeon(room_max_size=12, room_min_size=5, max_rooms=30)
        self.view.map_name_entry.delete(0, 'end')
        self.view.map_name_entry.insert(0, "Generated Dungeon")
        self._redraw_all()
        self.app_controller.set_dirty_flag()

    def save_map(self):
        map_name = self.view.map_name_entry.get()
        if not map_name: MessageBox.showerror("Error", "Please enter a name for the map.", parent=self.view.editor_tab); return
        
        self.model.name = map_name
        try:
            self.model.grid_scale = float(self.view.scale_entry.get())
        except ValueError:
            MessageBox.showerror("Error", "Invalid grid scale.", parent=self.view.editor_tab); return

        png_path = os.path.join(self.model.maps_dir, f"{map_name.lower().replace(' ', '_')}.png")
        if not self.view.save_canvas_to_png(png_path, self.model):
            MessageBox.showerror("Error", "Failed to save map image.", parent=self.view.editor_tab); return
            
        # Saving the map automatically saves the tokens as well, so unsaved changes are now committed.
        self.save_token_positions()
        # Reset the flag after a successful save
        self.app_controller.set_dirty_flag(False)
        self.refresh_map_list()
        MessageBox.showinfo("Success", f"Map '{self.model.name}' and its token positions have been saved.", parent=self.view.editor_tab)


    def save_token_positions(self):
        if not self.model.name or self.model.name in ["New Blank Map", "New Custom Map", "Generated Dungeon"]:
             MessageBox.showwarning("Save Required", "Please save the main map background first before saving token positions.", parent=self.view.editor_tab)
             return
        try:
            self.model.save_map_data()
            self.app_controller.set_dirty_flag(False)
            MessageBox.showinfo("Success", f"Token positions for '{self.model.name}' saved.", parent=self.view.editor_tab)
        except Exception as e:
            MessageBox.showerror("Error", f"Failed to save token data: {e}", parent=self.view.editor_tab)

    def refresh_map_list(self):
        maps = MapModel.get_all_maps(self.campaign_path)
        self.view.update_map_list(maps)
        
    def load_map_for_viewing(self, map_name):
        loaded_model = MapModel.load(self.campaign_path, map_name)
        if loaded_model:
            self.model = loaded_model
            self.view.map_name_entry.delete(0, 'end')
            self.view.map_name_entry.insert(0, self.model.name)
            self.view.update_dimension_fields(self.model)
            self.set_tool("select")
            
            png_path = os.path.join(self.model.maps_dir, f"{map_name.lower().replace(' ', '_')}.png")
            self.view.draw_editor_canvas(self.model, background_png_path=png_path)
            self.view.draw_static_background(map_name, self.model)
            self._redraw_viewer_canvas()
            self.app_controller.set_dirty_flag(False)
        else:
            MessageBox.showerror("Error", f"Could not load map data for '{map_name}'.", parent=self.view.editor_tab)

    def delete_selected_tokens(self):
        if not self.selected_tokens: MessageBox.showinfo("Info", "No tokens selected to delete.", parent=self.view.editor_tab); return
        if MessageBox.askyesno("Confirm", f"Are you sure you want to delete {len(self.selected_tokens)} token(s)?", parent=self.view.editor_tab):
            for token in self.selected_tokens:
                self.model.delete_token(token['name'])
            self.selected_tokens = []
            self._update_distance_display()
            self._redraw_viewer_canvas()
            self.app_controller.set_dirty_flag()