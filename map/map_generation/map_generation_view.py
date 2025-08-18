import customtkinter as ctk
from custom_dialogs import MessageBox

class MapGenerationDialog(ctk.CTkToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.result = None

        self.title("New Map Generator")
        self.geometry("450x400")
        self.resizable(False, False)
        self.configure(fg_color="#2B2B2B")
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Generate a New Map", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(0, 20))

        # Generator Type Selection
        ctk.CTkLabel(main_frame, text="Generator Type:", anchor="w").pack(fill="x")
        self.gen_type_combo = ctk.CTkComboBox(main_frame, values=["Blank Map", "Dungeon"], state="readonly")
        self.gen_type_combo.pack(fill="x", pady=(0, 15))
        self.gen_type_combo.set("Blank Map")

        # Basic Settings
        settings_frame = ctk.CTkFrame(main_frame)
        settings_frame.pack(fill="x", pady=5)
        settings_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(settings_frame, text="Width:").grid(row=0, column=0, padx=5, pady=5)
        self.width_entry = ctk.CTkEntry(settings_frame)
        self.width_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.width_entry.insert(0, "50")

        ctk.CTkLabel(settings_frame, text="Height:").grid(row=0, column=2, padx=5, pady=5)
        self.height_entry = ctk.CTkEntry(settings_frame)
        self.height_entry.grid(row=0, column=3, sticky="ew", padx=5)
        self.height_entry.insert(0, "50")

        ctk.CTkLabel(settings_frame, text="Grid Scale (m):").grid(row=1, column=0, padx=5, pady=5)
        self.scale_entry = ctk.CTkEntry(settings_frame)
        self.scale_entry.grid(row=1, column=1, columnspan=3, sticky="ew", padx=5)
        self.scale_entry.insert(0, "1.5")
        
        # Action Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack(side="bottom", pady=(20, 0))
        ctk.CTkButton(button_frame, text="Generate Map", command=self._on_generate).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Cancel", command=self._on_cancel, fg_color="gray50").pack(side="left", padx=10)

        self.transient(parent)
        
        # --- FIX: Ensure the window is viewable before making it modal ---
        self.update_idletasks()
        
        self.grab_set()
        self.wait_window()

    def _on_generate(self):
        try:
            self.result = {
                "gen_type": self.gen_type_combo.get(),
                "settings": {
                    "width": int(self.width_entry.get()),
                    "height": int(self.height_entry.get()),
                    "grid_scale": float(self.scale_entry.get())
                }
            }
            self.grab_release()
            self.destroy()
        except ValueError:
            # Pass `self` so the error dialog appears on top of this one
            MessageBox.showerror("Invalid Input", "Please ensure width, height, and scale are valid numbers.", parent=self)

    def _on_cancel(self):
        self.result = None
        self.grab_release()
        self.destroy()

    def get_result(self):
        return self.result