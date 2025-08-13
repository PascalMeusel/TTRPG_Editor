import customtkinter as ctk
from app_controller import AppController

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("TTRPG Campaign Editor")

    # --- FIX: Set the window to start in fullscreen mode ---
    root.attributes('-fullscreen', True)
    
    # These are still good to have as fallbacks if the user exits fullscreen
    root.geometry("1200x800")
    root.minsize(1000, 700)

    # The AppController now manages everything, including screen switching
    app = AppController(root)
    app.run()