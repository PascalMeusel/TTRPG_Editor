from tkinter import messagebox
from .map_model import MapModel
from .map_view import MapView

class MapController:
    """Controller for the Map Editor and Viewer."""
    def __init__(self, app_controller, editor_tab, viewer_tab):
        self.app_controller = app_controller
        self.view = MapView(editor_tab, viewer_tab)
        self.model = MapModel() # Start with a blank map
        self.current_tool = "brush"
        self.start_pos = None # For drawing shapes

        self.view.setup_editor_ui(self)
        self.view.setup_viewer_ui(self)
        self.refresh_map_list()

    def set_tool(self, tool_name):
        self.current_tool = tool_name

    def on_canvas_press(self, event):
        self.start_pos = (event.x, event.y)

    def on_canvas_release(self, event):
        if self.current_tool == "rect" and self.start_pos:
            grid_size = self.model.grid_size
            x1 = self.start_pos[0] // grid_size
            y1 = self.start_pos[1] // grid_size
            x2 = event.x // grid_size
            y2 = event.y // grid_size
            color = self.view.color_var.get()
            self.model.add_element({'type': 'rect', 'coords': (x1, y1, x2, y2), 'color': color})
            self.view.draw_map_on_canvas(self.model)
        self.start_pos = None

    def on_canvas_drag(self, event):
        if self.current_tool == "brush" or self.current_tool == "eraser":
            grid_size = self.model.grid_size
            x = event.x // grid_size
            y = event.y // grid_size
            color = self.view.color_var.get() if self.current_tool == "brush" else "#3C3C3C" # Eraser draws floor
            
            # Draw a 1x1 rect as a brush stroke
            self.model.add_element({'type': 'rect', 'coords': (x, y, x + 1, y + 1), 'color': color})
            self.view.draw_map_on_canvas(self.model)

    def generate_dungeon(self):
        if messagebox.askyesno("Confirm", "This will erase the current map. Are you sure?"):
            self.model.generate_dungeon(room_max_size=8, room_min_size=4, max_rooms=20)
            self.view.draw_map_on_canvas(self.model)

    def save_map(self):
        map_name = self.view.map_name_entry.get()
        if not map_name:
            messagebox.showerror("Error", "Please enter a name for the map.")
            return
        
        try:
            self.model.save_map(map_name)
            messagebox.showinfo("Success", f"Map '{map_name}' saved successfully.")
            self.refresh_map_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save map: {e}")
            
    def refresh_map_list(self):
        maps = MapModel.get_all_maps()
        self.view.update_map_list(maps)
        
    def load_map_for_viewing(self, map_name):
        self.view.display_map_image(map_name)