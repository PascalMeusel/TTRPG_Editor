import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw
import os

class MapView:
    """Manages the UI for the self-contained Map feature."""
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        
        self.tab_view = ctk.CTkTabview(parent_frame, fg_color="transparent")
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        self.editor_tab = self.tab_view.add("Editor")
        self.viewer_tab = self.tab_view.add("Viewer")

        self.map_photo_image = None
        self.PC_COLOR = "#00BFFF"
        self.NPC_COLOR = "#DC143C"

    def setup_ui(self, controller):
        """Calls the setup methods for both internal tabs."""
        self.setup_editor_ui(controller)
        self.setup_viewer_ui(controller)

    def setup_editor_ui(self, controller):
        """Builds the UI for the Map Editor tab."""
        self.editor_tab.grid_columnconfigure(1, weight=1)
        self.editor_tab.grid_rowconfigure(0, weight=1)
        
        toolbar = ctk.CTkFrame(self.editor_tab, width=200)
        toolbar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        
        ctk.CTkButton(toolbar, text="New Map...", command=controller.show_new_map_dialog).pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(toolbar, text="Level Controls", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        self.editor_level_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.editor_level_frame.pack(fill="x", padx=10, pady=5)
        self.editor_level_down_btn = ctk.CTkButton(self.editor_level_frame, text="Down", command=lambda: controller.change_level(-1))
        self.editor_level_down_btn.pack(side="left", expand=True, padx=2)
        self.editor_level_label = ctk.CTkLabel(self.editor_level_frame, text="Lvl: 0", width=50)
        self.editor_level_label.pack(side="left", expand=True)
        self.editor_level_up_btn = ctk.CTkButton(self.editor_level_frame, text="Up", command=lambda: controller.change_level(1))
        self.editor_level_up_btn.pack(side="left", expand=True, padx=2)
        
        ctk.CTkLabel(toolbar, text="Editor Tools", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        ctk.CTkButton(toolbar, text="Brush", command=lambda: controller.set_tool("brush")).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Rectangle", command=lambda: controller.set_tool("rect")).pack(pady=5, padx=10, fill="x")
        self.color_var = ctk.StringVar(value="#999999")
        colors = {"Stone": "#999999", "Grass": "#6B8E23", "Water": "#4682B4", "Wood": "#8B4513"}
        for name, code in colors.items(): ctk.CTkRadioButton(toolbar, text=name, variable=self.color_var, value=code).pack(anchor="w", padx=20, pady=2)
        
        ctk.CTkLabel(toolbar, text="Landmark Tool", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.landmark_text_entry = ctk.CTkEntry(toolbar, placeholder_text="Landmark Text...")
        self.landmark_text_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Place Landmark", command=lambda: controller.set_tool("landmark")).pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(toolbar, text="Map Properties", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        scale_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        scale_frame.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(scale_frame, text="Grid Scale (m):").pack(side="left")
        self.scale_entry = ctk.CTkEntry(scale_frame, width=60)
        self.scale_entry.pack(side="left", padx=5)

        ctk.CTkLabel(toolbar, text="Map Name:").pack(anchor="w", padx=10)
        self.map_name_entry = ctk.CTkEntry(toolbar)
        self.map_name_entry.pack(pady=(0,10), padx=10, fill="x")
        
        ctk.CTkButton(toolbar, text="Save Map", command=controller.save_map).pack(side="bottom", pady=10, padx=10, fill="x")
        
        canvas_container = ctk.CTkScrollableFrame(self.editor_tab, label_text="Map Canvas")
        canvas_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.editor_canvas = ctk.CTkCanvas(canvas_container, bg="#2B2B2B", highlightthickness=0)
        self.editor_canvas.bind("<B1-Motion>", controller.on_editor_canvas_drag)
        self.editor_canvas.bind("<ButtonPress-1>", controller.on_editor_canvas_press)
        self.editor_canvas.bind("<ButtonRelease-1>", controller.on_editor_canvas_release)
        self.editor_canvas.pack()

    def setup_viewer_ui(self, controller):
        """Builds the UI for the Map Viewer tab."""
        self.viewer_tab.grid_columnconfigure(1, weight=1)
        self.viewer_tab.grid_rowconfigure(0, weight=1)
        toolbar = ctk.CTkFrame(self.viewer_tab, width=200)
        toolbar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(toolbar, text="Select Map:").pack(pady=(10, 5))
        self.map_selection_list = ctk.CTkComboBox(toolbar, command=controller.load_map_for_viewing)
        self.map_selection_list.pack(pady=5, padx=10, fill="x")
        self.map_selection_list.bind("<Button-1>", lambda event: self.map_selection_list._open_dropdown_menu())
        
        ctk.CTkLabel(toolbar, text="Level Controls", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        self.viewer_level_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        self.viewer_level_frame.pack(fill="x", padx=10, pady=5)
        self.viewer_level_down_btn = ctk.CTkButton(self.viewer_level_frame, text="Down", command=lambda: controller.change_level(-1))
        self.viewer_level_down_btn.pack(side="left", expand=True, padx=2)
        self.viewer_level_label = ctk.CTkLabel(self.viewer_level_frame, text="Lvl: 0", width=50)
        self.viewer_level_label.pack(side="left", expand=True)
        self.viewer_level_up_btn = ctk.CTkButton(self.viewer_level_frame, text="Up", command=lambda: controller.change_level(1))
        self.viewer_level_up_btn.pack(side="left", expand=True, padx=2)

        ctk.CTkLabel(toolbar, text="Token Tools", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.token_placer_list = ctk.CTkComboBox(toolbar, values=["Load characters/npcs"])
        self.token_placer_list.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Place Token", command=lambda: controller.set_tool("place_token")).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Delete Selected", command=controller.delete_selected_tokens, fg_color="#D2691E", hover_color="#B2590E").pack(pady=5, padx=10, fill="x")
        
        ctk.CTkLabel(toolbar, text="Token Actions", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        ctk.CTkLabel(toolbar, text="Movement (m):").pack()
        self.movement_entry = ctk.CTkEntry(toolbar, width=80)
        self.movement_entry.pack()
        self.movement_entry.insert(0, "6")
        ctk.CTkLabel(toolbar, text="Distance:").pack(pady=(10, 0))
        self.distance_label = ctk.CTkLabel(toolbar, text="-", font=ctk.CTkFont(size=16, weight="bold"))
        self.distance_label.pack()
        
        canvas_container = ctk.CTkScrollableFrame(self.viewer_tab, label_text="Live Map")
        canvas_container.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        self.viewer_canvas = ctk.CTkCanvas(canvas_container, bg="#101010", highlightthickness=0)
        self.viewer_canvas.bind("<Button-1>", controller.on_viewer_canvas_press)
        self.viewer_canvas.bind("<B1-Motion>", controller.on_viewer_canvas_drag)
        self.viewer_canvas.bind("<ButtonRelease-1>", controller.on_viewer_canvas_release)
        self.viewer_canvas.bind("<Control-Button-1>", controller.on_viewer_canvas_ctrl_press)
        self.viewer_canvas.pack()

    def clear_all_canvases(self):
        self.editor_canvas.delete("all")
        self.editor_canvas.configure(width=1, height=1)
        self.viewer_canvas.delete("all")
        self.viewer_canvas.configure(width=1, height=1)

    def update_level_controls(self, map_model, current_level):
        if map_model and map_model.map_type == 'inside':
            self.editor_level_label.configure(text=f"Lvl: {current_level}")
            self.editor_level_down_btn.configure(state="normal")
            self.editor_level_up_btn.configure(state="normal")
            self.viewer_level_label.configure(text=f"Lvl: {current_level}")
            self.viewer_level_down_btn.configure(state="normal")
            self.viewer_level_up_btn.configure(state="normal")
        else:
            level_text = "Outside" if map_model else "No Map"
            self.editor_level_label.configure(text=level_text)
            self.editor_level_down_btn.configure(state="disabled")
            self.editor_level_up_btn.configure(state="disabled")
            self.viewer_level_label.configure(text=level_text)
            self.viewer_level_down_btn.configure(state="disabled")
            self.viewer_level_up_btn.configure(state="disabled")

    def save_canvas_to_png(self, filepath, map_model, current_level):
        try:
            grid_size = map_model.grid_size
            width = map_model.width * grid_size
            height = map_model.height * grid_size
            image = Image.new("RGB", (width, height), "#2B2B2B")
            draw = ImageDraw.Draw(image)
            for elem in map_model.levels[current_level]['elements']:
                coords = tuple(c * grid_size for c in elem['coords'])
                draw.rectangle(coords, fill=elem['color'], outline=None)
            grid_line_color = "#444444"
            for i in range(0, width, grid_size):
                draw.line([(i, 0), (i, height)], fill=grid_line_color, width=1)
            for i in range(0, height, grid_size):
                draw.line([(0, i), (width, i)], fill=grid_line_color, width=1)
            image.save(filepath)
            return True
        except Exception as e:
            print(f"Error saving canvas to PNG with ImageDraw: {e}")
            return False

    def _draw_grid(self, canvas, width, height, grid_size):
        for i in range(0, width + 1, grid_size):
            canvas.create_line(i, 0, i, height, tag="grid_line", fill="#444444")
        for i in range(0, height + 1, grid_size):
            canvas.create_line(0, i, width, i, tag="grid_line", fill="#444444")

    # --- NEW: Helper method to draw landmark text ---
    def _draw_landmarks(self, canvas, map_model, current_level):
        if 'landmarks' not in map_model.levels[current_level]: return
        
        grid_size = map_model.grid_size
        for landmark in map_model.levels[current_level]['landmarks']:
            x = (landmark['x'] + 0.5) * grid_size
            y = (landmark['y'] + 0.5) * grid_size
            canvas.create_text(x, y, text=landmark['text'], fill="yellow", 
                               font=("Arial", 10, "bold"), anchor="center")

    def draw_editor_canvas(self, map_model, current_level):
        canvas_width = map_model.width * map_model.grid_size
        canvas_height = map_model.height * map_model.grid_size
        self.editor_canvas.configure(width=canvas_width, height=canvas_height)
        self.editor_canvas.delete("all")
        
        for elem in map_model.levels[current_level]['elements']:
            coords = tuple(c * map_model.grid_size for c in elem['coords'])
            self.editor_canvas.create_rectangle(coords, fill=elem['color'], outline="")
        
        self._draw_grid(self.editor_canvas, canvas_width, canvas_height, map_model.grid_size)
        # --- NEW: Call the landmark drawing method ---
        self._draw_landmarks(self.editor_canvas, map_model, current_level)

    def draw_static_background(self, map_model, current_level):
        """Draws the map background and landmarks on the viewer canvas."""
        canvas_width = map_model.width * map_model.grid_size
        canvas_height = map_model.height * map_model.grid_size
        self.viewer_canvas.configure(width=canvas_width, height=canvas_height)
        self.viewer_canvas.delete("all")
        if not map_model: return
        
        for elem in map_model.levels[current_level]['elements']:
            coords = tuple(c * map_model.grid_size for c in elem['coords'])
            self.viewer_canvas.create_rectangle(coords, fill=elem['color'], outline="")
        
        self._draw_grid(self.viewer_canvas, canvas_width, canvas_height, map_model.grid_size)
        # --- NEW: Call the landmark drawing method ---
        self._draw_landmarks(self.viewer_canvas, map_model, current_level)

    def draw_viewer_canvas(self, map_model, controller):
        self.viewer_canvas.delete("token", "overlay")
        current_level = controller.current_level
        grid_size = map_model.grid_size
        for token in map_model.levels[current_level]['tokens']:
            if token is not controller.token_being_dragged:
                self._draw_token(self.viewer_canvas, token, grid_size)
        if controller.token_being_dragged and controller.drag_preview_pos:
            self._draw_token(self.viewer_canvas, controller.token_being_dragged, grid_size, preview_pos=controller.drag_preview_pos)
        self._draw_selection_overlay(map_model, controller)

    def _draw_token(self, canvas, token_data, grid_size, preview_pos=None):
        color = self.PC_COLOR if token_data['type'] == 'PC' else self.NPC_COLOR
        center_x, center_y = preview_pos or ((token_data['x'] + 0.5) * grid_size, (token_data['y'] + 0.5) * grid_size)
        radius = grid_size * 0.4
        canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=color, outline="white", width=1, tags="token")
        canvas.create_text(center_x, center_y, text=token_data['name'][0], fill="white", font=("Arial", 10, "bold"), tags="token")

    def _draw_selection_overlay(self, map_model, controller):
        if not controller.selected_tokens: return
        grid_size = map_model.grid_size
        if len(controller.selected_tokens) == 1:
            token = controller.selected_tokens[0]
            try: move_dist = float(self.movement_entry.get() or 0)
            except ValueError: move_dist = 0
            if move_dist > 0:
                start_pos = controller.drag_start_pos.get(token['name'], (token['x'], token['y']))
                radius = (move_dist / map_model.grid_scale) * grid_size
                center_x, center_y = (start_pos[0] + 0.5) * grid_size, (start_pos[1] + 0.5) * grid_size
                self.viewer_canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, outline="yellow", dash=(4, 4), width=2, tags="overlay")
        elif len(controller.selected_tokens) == 2:
            t1, t2 = controller.selected_tokens[0], controller.selected_tokens[1]
            x1, y1 = (t1['x'] + 0.5) * grid_size, (t1['y'] + 0.5) * grid_size
            x2, y2 = (t2['x'] + 0.5) * grid_size, (t2['y'] + 0.5) * grid_size
            self.viewer_canvas.create_line(x1, y1, x2, y2, fill="yellow", width=2, dash=(4, 4), tags="overlay")

    def update_token_placer_list(self, tokens):
        self.token_placer_list.configure(values=tokens or ["Load characters/npcs"])
        if tokens: self.token_placer_list.set(tokens[0])
        else: self.token_placer_list.set("Load characters/npcs")

    def update_map_list(self, maps):
        prompt = "Select a saved map..."
        display_values = [prompt] + (maps or [])
        self.map_selection_list.configure(values=display_values)
        self.map_selection_list.set(prompt)

    def draw_static_background(self, map_model, current_level):
        canvas_width = map_model.width * map_model.grid_size
        canvas_height = map_model.height * map_model.grid_size
        self.viewer_canvas.configure(width=canvas_width, height=canvas_height)
        self.viewer_canvas.delete("all")
        if not map_model: return
        for elem in map_model.levels[current_level]['elements']:
            coords = tuple(c * map_model.grid_size for c in elem['coords'])
            self.viewer_canvas.create_rectangle(coords, fill=elem['color'], outline="")
        self._draw_grid(self.viewer_canvas, canvas_width, canvas_height, map_model.grid_size)

    def update_dimension_fields(self, map_model):
        self.scale_entry.delete(0, 'end')
        self.scale_entry.insert(0, str(map_model.grid_scale))