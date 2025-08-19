import customtkinter as ctk
from custom_dialogs import MessageBox

class MapGenerationDialog(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.result = None

        self.title("New Map Generator")
        self.geometry("450x550") # Increased height for new options
        self.resizable(False, False)
        self.configure(fg_color="#2B2B2B")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Generate a New Map", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 10))

        # --- REFACTORED: Add a command to the generator combo box ---
        ctk.CTkLabel(main_frame, text="Generator Type:", anchor="w").pack(fill="x")
        self.gen_type_combo = ctk.CTkComboBox(
            main_frame, 
            values=["Blank Map", "Dungeon", "Winding Road", "Simple Town"], 
            state="readonly",
            command=self._on_generator_selected # This is the key change
        )
        self.gen_type_combo.pack(fill="x", pady=(0, 15))
        self.gen_type_combo.set("Blank Map")

        # --- Generic Settings (always visible) ---
        generic_settings_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        generic_settings_frame.pack(fill="x", pady=5)
        generic_settings_frame.grid_columnconfigure((1, 3), weight=1)
        ctk.CTkLabel(generic_settings_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        self.width_entry = ctk.CTkEntry(generic_settings_frame)
        self.width_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.width_entry.insert(0, "50")
        ctk.CTkLabel(generic_settings_frame, text="Height:").grid(row=0, column=2, padx=5, pady=5)
        self.height_entry = ctk.CTkEntry(generic_settings_frame)
        self.height_entry.grid(row=0, column=3, sticky="ew", padx=5)
        self.height_entry.insert(0, "50")
        ctk.CTkLabel(generic_settings_frame, text="Grid Scale (m):").grid(row=1, column=0, padx=5, pady=5)
        self.scale_entry = ctk.CTkEntry(generic_settings_frame)
        self.scale_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5)
        self.scale_entry.insert(0, "1.5")

        # --- NEW: Container for generator-specific settings ---
        self.specific_settings_container = ctk.CTkFrame(main_frame, fg_color="gray20")
        self.specific_settings_container.pack(fill="both", expand=True, pady=10)
        
        # --- NEW: Create frames for each generator type ---
        self._create_dungeon_settings()
        self._create_road_settings()
        self._create_town_settings()

        # Action Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", pady=(10, 0))
        ctk.CTkButton(button_frame, text="Generate Map", command=self._on_generate).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=self._on_cancel, fg_color="gray50").pack(side="left", padx=10)

        # Show the initial correct settings
        self._on_generator_selected("Blank Map")

        self.transient(parent)
        self.update_idletasks()
        self.grab_set()
        self.wait_window()

    def _create_dungeon_settings(self):
        self.dungeon_frame = ctk.CTkFrame(self.specific_settings_container, fg_color="transparent")
        self.dungeon_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Num Rooms
        ctk.CTkLabel(self.dungeon_frame, text="Number of Rooms:").pack(anchor="w")
        self.dungeon_rooms_slider = ctk.CTkSlider(self.dungeon_frame, from_=5, to=50, number_of_steps=45)
        self.dungeon_rooms_slider.set(30)
        self.dungeon_rooms_slider.pack(fill="x", pady=(0,10))
        # Room Size
        ctk.CTkLabel(self.dungeon_frame, text="Room Size (Min/Max):").pack(anchor="w")
        size_frame = ctk.CTkFrame(self.dungeon_frame, fg_color="transparent")
        size_frame.pack(fill="x")
        self.dungeon_min_size_slider = ctk.CTkSlider(size_frame, from_=3, to=10, number_of_steps=7)
        self.dungeon_min_size_slider.set(5)
        self.dungeon_min_size_slider.pack(side="left", fill="x", expand=True, padx=(0,5))
        self.dungeon_max_size_slider = ctk.CTkSlider(size_frame, from_=8, to=20, number_of_steps=12)
        self.dungeon_max_size_slider.set(12)
        self.dungeon_max_size_slider.pack(side="left", fill="x", expand=True, padx=(5,0))

    def _create_road_settings(self):
        self.road_frame = ctk.CTkFrame(self.specific_settings_container, fg_color="transparent")
        self.road_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Path Width
        ctk.CTkLabel(self.road_frame, text="Path Width:").pack(anchor="w")
        self.road_width_slider = ctk.CTkSlider(self.road_frame, from_=1, to=5, number_of_steps=4)
        self.road_width_slider.set(3)
        self.road_width_slider.pack(fill="x", pady=(0,10))
        # Scenery Density
        ctk.CTkLabel(self.road_frame, text="Scenery Density:").pack(anchor="w")
        self.road_scenery_slider = ctk.CTkSlider(self.road_frame, from_=10, to=200, number_of_steps=19)
        self.road_scenery_slider.set(70)
        self.road_scenery_slider.pack(fill="x", pady=(0,10))

    def _create_town_settings(self):
        self.town_frame = ctk.CTkFrame(self.specific_settings_container, fg_color="transparent")
        self.town_frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Layout Type
        ctk.CTkLabel(self.town_frame, text="Road Layout:").pack(anchor="w")
        self.town_layout_combo = ctk.CTkComboBox(self.town_frame, values=["Crossroads", "Main Street", "Riverside"], state="readonly")
        self.town_layout_combo.set("Crossroads")
        self.town_layout_combo.pack(fill="x", pady=(0,10))
        # Building Count
        ctk.CTkLabel(self.town_frame, text="Number of Buildings:").pack(anchor="w")
        self.town_buildings_slider = ctk.CTkSlider(self.town_frame, from_=5, to=25, number_of_steps=20)
        self.town_buildings_slider.set(15)
        self.town_buildings_slider.pack(fill="x", pady=(0,10))

    def _on_generator_selected(self, selection):
        """Hides all specific settings frames and shows the correct one."""
        self.dungeon_frame.pack_forget()
        self.road_frame.pack_forget()
        self.town_frame.pack_forget()
        
        if selection == "Dungeon":
            self.dungeon_frame.pack(fill="both", expand=True, padx=10, pady=10)
        elif selection == "Winding Road":
            self.road_frame.pack(fill="both", expand=True, padx=10, pady=10)
        elif selection == "Simple Town":
            self.town_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _on_generate(self):
        try:
            settings = {
                "width": int(self.width_entry.get()),
                "height": int(self.height_entry.get()),
                "grid_scale": float(self.scale_entry.get())
            }
            gen_type = self.gen_type_combo.get()
            
            # --- NEW: Add the specific settings based on generator type ---
            if gen_type == "Dungeon":
                settings["dungeon_rooms"] = int(self.dungeon_rooms_slider.get())
                settings["dungeon_min_size"] = int(self.dungeon_min_size_slider.get())
                settings["dungeon_max_size"] = int(self.dungeon_max_size_slider.get())
            elif gen_type == "Winding Road":
                settings["road_path_width"] = int(self.road_width_slider.get())
                settings["road_scenery_density"] = int(self.road_scenery_slider.get())
            elif gen_type == "Simple Town":
                settings["town_layout"] = self.town_layout_combo.get()
                settings["town_buildings"] = int(self.town_buildings_slider.get())

            self.result = { "gen_type": gen_type, "settings": settings }
            self.grab_release()
            self.destroy()
        except ValueError:
            MessageBox.showerror("Invalid Input", "Please ensure width, height, and scale are valid numbers.", parent=self)

    def _on_cancel(self):
        self.result = None
        self.grab_release()
        self.destroy()

    def get_result(self):
        return self.result