import customtkinter as ctk
from PIL import Image, ImageTk
import os # Import os here to use it

class MapView:
    """Manages the UI for the Map Editor and Map Viewer tabs."""
    def __init__(self, editor_tab, viewer_tab):
        self.editor_tab = editor_tab
        self.viewer_tab = viewer_tab
        self.drawing_canvas = None
        self.viewer_canvas = None
        self.map_photo_image = None # To prevent garbage collection

    def setup_editor_ui(self, controller):
        """Builds the UI for the Map Editor."""
        # --- Main Layout ---
        self.editor_tab.grid_columnconfigure(1, weight=1)
        self.editor_tab.grid_rowconfigure(0, weight=1)
        
        # --- Toolbar ---
        toolbar = ctk.CTkFrame(self.editor_tab, width=150)
        # --- FIX: Changed sticky from "nswy" to "ns" to make it stretch vertically ---
        toolbar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        
        ctk.CTkLabel(toolbar, text="Tools", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkButton(toolbar, text="Brush", command=lambda: controller.set_tool("brush")).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Rectangle", command=lambda: controller.set_tool("rect")).pack(pady=5, padx=10, fill="x")
        ctk.CTkButton(toolbar, text="Eraser", command=lambda: controller.set_tool("eraser")).pack(pady=5, padx=10, fill="x")
        
        # --- Color Palette ---
        ctk.CTkLabel(toolbar, text="Color", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        self.color_var = ctk.StringVar(value="#999999") # Default stone color
        colors = {"Stone": "#999999", "Grass": "#6B8E23", "Water": "#4682B4", "Wood": "#8B4513", "Black": "#000000"}
        for name, code in colors.items():
            ctk.CTkRadioButton(toolbar, text=name, variable=self.color_var, value=code).pack(anchor="w", padx=20, pady=2)
            
        # --- Save Controls ---
        ctk.CTkLabel(toolbar, text="Map Name", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        self.map_name_entry = ctk.CTkEntry(toolbar)
        self.map_name_entry.pack(pady=5, padx=10, fill="x")
        self.map_name_entry.insert(0, "My New Dungeon")
        ctk.CTkButton(toolbar, text="Save Map", command=controller.save_map).pack(pady=10, padx=10, fill="x")
        
        # --- Generator Controls ---
        gen_frame = ctk.CTkFrame(toolbar)
        gen_frame.pack(pady=20, padx=10, fill="x")
        ctk.CTkLabel(gen_frame, text="Generator", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        ctk.CTkButton(gen_frame, text="Generate Dungeon", command=controller.generate_dungeon).pack(pady=10, padx=10, fill="x")

        # --- Canvas ---
        canvas_frame = ctk.CTkFrame(self.editor_tab)
        canvas_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.drawing_canvas = ctk.CTkCanvas(canvas_frame, bg="#202020", highlightthickness=0)
        self.drawing_canvas.pack(fill="both", expand=True)
        self.drawing_canvas.bind("<B1-Motion>", controller.on_canvas_drag)
        self.drawing_canvas.bind("<ButtonPress-1>", controller.on_canvas_press)
        self.drawing_canvas.bind("<ButtonRelease-1>", controller.on_canvas_release)
        
    def setup_viewer_ui(self, controller):
        """Builds the UI for the Map Viewer."""
        self.viewer_tab.grid_columnconfigure(0, weight=1)
        self.viewer_tab.grid_rowconfigure(1, weight=1)
        
        # --- Top Controls ---
        controls_frame = ctk.CTkFrame(self.viewer_tab)
        controls_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        ctk.CTkLabel(controls_frame, text="Select Map:").pack(side="left", padx=10)
        self.map_selection_list = ctk.CTkComboBox(controls_frame, command=controller.load_map_for_viewing)
        self.map_selection_list.pack(side="left", padx=10, fill="x", expand=True)
        
        # --- Viewer Canvas ---
        self.viewer_canvas = ctk.CTkCanvas(self.viewer_tab, bg="#101010", highlightthickness=0)
        self.viewer_canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def draw_map_on_canvas(self, map_model):
        """Clears and redraws all elements from the map model onto the editor canvas."""
        self.drawing_canvas.delete("all")
        grid_size = map_model.grid_size
        for elem in map_model.map_elements:
            coords = tuple(c * grid_size for c in elem['coords'])
            if elem['type'] == 'rect':
                self.drawing_canvas.create_rectangle(coords, fill=elem['color'], outline="")
            elif elem['type'] == 'line':
                self.drawing_canvas.create_line(coords, fill=elem['color'], width=elem.get('width', 1))

    def update_map_list(self, maps):
        """Updates the dropdown list in the viewer tab."""
        self.map_selection_list.configure(values=maps or ["No maps found"])
        if not maps:
            self.map_selection_list.set("")
        
    def display_map_image(self, map_name):
        """Loads and displays a rendered map PNG in the viewer."""
        self.viewer_canvas.delete("all")
        if not map_name: return

        map_path = os.path.join("data/maps", f"{map_name.lower().replace(' ', '_')}.png")
        if os.path.exists(map_path):
            try:
                img = Image.open(map_path)
                self.map_photo_image = ImageTk.PhotoImage(img) # Must keep a reference
                self.viewer_canvas.create_image(0, 0, anchor="nw", image=self.map_photo_image)
            except Exception as e:
                print(f"Error loading map image: {e}")