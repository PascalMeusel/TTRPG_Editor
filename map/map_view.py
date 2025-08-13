import customtkinter as ctk
from PIL import Image, ImageTk, ImageGrab
import os

class MapView:
    """Manages the UI for the Map Editor and Map Viewer tabs."""
    def __init__(self, editor_tab, viewer_tab):
        self.editor_tab = editor_tab
        self.viewer_tab = viewer_tab
        self.map_photo_image = None
        self.editor_bg_image = None # Separate reference for editor background
        self.PC_COLOR = "#00BFFF"
        self.NPC_COLOR = "#DC143C"

    def setup_editor_ui(self, controller):
        """Builds the UI for the Map Editor tab."""
        self.editor_tab.grid_columnconfigure(1, weight=1)
        self.editor_tab.grid_rowconfigure(0, weight=1)
        toolbar = ctk.CTkFrame(self.editor_tab, width=200)
        toolbar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        
        # --- Map Creation ---
        ctk.CTkLabel(toolbar, text="Map Setup", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        dims_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        dims_frame.pack(fill="x", padx=10)
        dims_frame.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(dims_frame, text="Width").grid(row=0, column=0)
        self.width_entry = ctk.CTkEntry(dims_frame)
        self.width_entry.grid(row=1, column=0, padx=(0,2))
        self.width_entry.insert(0, "80")
        ctk.CTkLabel(dims_frame, text="Height").grid(row=0, column=1)
        self.height_entry = ctk.CTkEntry(dims_frame)
        self.height_entry.grid(row=1, column=1, padx=(2,0))
        self.height_entry.insert(0, "60")
        ctk.CTkLabel(dims_frame, text="Grid Scale (m)").grid(row=2, column=0, pady=(5,0))
        self.scale_entry = ctk.CTkEntry(dims_frame)
        self.scale_entry.grid(row=3, column=0, padx=(0,2))
        self.scale_entry.insert(0, "1.5")
        ctk.CTkButton(toolbar, text="New Blank Map", command=controller.new_map).pack(pady=(10,5), padx=10, fill="x")
        
        # --- Drawing Tools ---
        ctk.CTkLabel(toolbar, text="Drawing Tools", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        ctk.CTkButton(toolbar, text="Brush", command=lambda: controller.set_tool("brush")).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Rectangle", command=lambda: controller.set_tool("rect")).pack(pady=5, padx=10, fill="x")
        self.color_var = ctk.StringVar(value="#999999")
        colors = {"Stone": "#999999", "Grass": "#6B8E23", "Water": "#4682B4", "Wood": "#8B4513"}
        for name, code in colors.items(): ctk.CTkRadioButton(toolbar, text=name, variable=self.color_var, value=code).pack(anchor="w", padx=20, pady=2)
        
        # --- Generator ---
        ctk.CTkLabel(toolbar, text="Generator", font=ctk.CTkFont(weight="bold")).pack(pady=(10,0))
        ctk.CTkButton(toolbar, text="Generate Dungeon", command=controller.generate_dungeon).pack(pady=5, padx=10, fill="x")
        
        # --- Saving ---
        ctk.CTkLabel(toolbar, text="Map Name").pack(pady=(20, 5))
        self.map_name_entry = ctk.CTkEntry(toolbar)
        self.map_name_entry.pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Save Map Background", command=controller.save_map).pack(pady=10, padx=10, fill="x")
        
        canvas_frame = ctk.CTkFrame(self.editor_tab)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.editor_canvas = ctk.CTkCanvas(canvas_frame, bg="#2B2B2B", highlightthickness=0)
        self.editor_canvas.pack(fill="both", expand=True)
        self.editor_canvas.bind("<B1-Motion>", controller.on_editor_canvas_drag)
        self.editor_canvas.bind("<ButtonPress-1>", controller.on_editor_canvas_press)
        self.editor_canvas.bind("<ButtonRelease-1>", controller.on_editor_canvas_release)

    def setup_viewer_ui(self, controller):
        """Builds the UI for the Map Viewer (live play) tab."""
        self.viewer_tab.grid_columnconfigure(1, weight=1)
        self.viewer_tab.grid_rowconfigure(0, weight=1)
        toolbar = ctk.CTkFrame(self.viewer_tab, width=180)
        toolbar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        ctk.CTkLabel(toolbar, text="Select Map:").pack(pady=(10, 5))
        self.map_selection_list = ctk.CTkComboBox(toolbar, command=controller.load_map_for_viewing)
        self.map_selection_list.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(toolbar, text="Token Tools", font=ctk.CTkFont(weight="bold")).pack(pady=(20, 5))
        self.token_placer_list = ctk.CTkComboBox(toolbar, values=["Load a rule set"])
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
        ctk.CTkButton(toolbar, text="Save Token Positions", command=controller.save_map).pack(side="bottom", pady=20, padx=10, fill="x")
        canvas_frame = ctk.CTkFrame(self.viewer_tab)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.viewer_canvas = ctk.CTkCanvas(canvas_frame, bg="#101010", highlightthickness=0)
        self.viewer_canvas.pack(fill="both", expand=True)
        self.viewer_canvas.bind("<Button-1>", controller.on_viewer_canvas_press)
        self.viewer_canvas.bind("<B1-Motion>", controller.on_viewer_canvas_drag)
        self.viewer_canvas.bind("<ButtonRelease-1>", controller.on_viewer_canvas_release)
        self.viewer_canvas.bind("<Control-Button-1>", controller.on_viewer_canvas_ctrl_press)

    def save_canvas_to_png(self, filepath):
        """Saves the current state of the editor canvas to a PNG file."""
        try:
            x = self.editor_canvas.winfo_rootx()
            y = self.editor_canvas.winfo_rooty()
            width = self.editor_canvas.winfo_width()
            height = self.editor_canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            img.save(filepath)
            return True
        except Exception as e:
            print(f"Error saving canvas to PNG: {e}")
            return False

    def draw_editor_canvas(self, map_model, background_png_path=None):
        """Draws the editor canvas. If a path is provided, it uses it as a background."""
        self.editor_canvas.delete("all")
        if background_png_path and os.path.exists(background_png_path):
            img = Image.open(background_png_path)
            self.editor_bg_image = ImageTk.PhotoImage(img)
            self.editor_canvas.create_image(0, 0, anchor="nw", image=self.editor_bg_image, tags="background")
        else:
            grid_size = map_model.grid_size
            for elem in map_model.map_elements:
                coords = tuple(c * grid_size for c in elem['coords'])
                self.editor_canvas.create_rectangle(coords, fill=elem['color'], outline="")

    def draw_viewer_canvas(self, map_model, controller):
        """Draws dynamic elements (tokens, overlays) on the viewer canvas."""
        self.viewer_canvas.delete("token", "overlay")
        grid_size = map_model.grid_size
        for token in map_model.tokens:
            if token is not controller.token_being_dragged:
                self._draw_token(self.viewer_canvas, token, grid_size)
        if controller.token_being_dragged and controller.drag_preview_pos:
            self._draw_token(self.viewer_canvas, controller.token_being_dragged, grid_size, preview_pos=controller.drag_preview_pos)
        self._draw_selection_overlay(map_model, controller)

    def _draw_token(self, canvas, token_data, grid_size, preview_pos=None):
        """Helper to draw a single token."""
        color = self.PC_COLOR if token_data['type'] == 'PC' else self.NPC_COLOR
        center_x, center_y = preview_pos or ((token_data['x'] + 0.5) * grid_size, (token_data['y'] + 0.5) * grid_size)
        radius = grid_size * 0.4
        canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=color, outline="white", width=1, tags="token")
        canvas.create_text(center_x, center_y, text=token_data['name'][0], fill="white", font=("Arial", 10, "bold"), tags="token")

    def _draw_selection_overlay(self, map_model, controller):
        """Draws overlays like movement circles and distance lines."""
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
        self.token_placer_list.configure(values=tokens or ["No tokens available"])
        if tokens: self.token_placer_list.set(tokens[0])
        else: self.token_placer_list.set("")

    def update_map_list(self, maps):
        self.map_selection_list.configure(values=maps or ["No maps found"])
        if not maps: self.map_selection_list.set("")

    def draw_static_background(self, map_name):
        """Draws the static background image on the viewer canvas."""
        self.viewer_canvas.delete("all")
        if not map_name: return
        png_path = os.path.join("data/maps", f"{map_name.lower().replace(' ', '_')}.png")
        if os.path.exists(png_path):
            try:
                img = Image.open(png_path)
                self.map_photo_image = ImageTk.PhotoImage(img)
                self.viewer_canvas.create_image(0, 0, anchor="nw", image=self.map_photo_image, tags="background")
            except Exception as e:
                print(f"Error loading map image: {e}")

    def update_dimension_fields(self, map_model):
        """Updates the dimension entry fields with the loaded map's data."""
        self.width_entry.delete(0, 'end')
        self.width_entry.insert(0, str(map_model.width))
        self.height_entry.delete(0, 'end')
        self.height_entry.insert(0, str(map_model.height))
        self.scale_entry.delete(0, 'end')
        self.scale_entry.insert(0, str(map_model.grid_scale))