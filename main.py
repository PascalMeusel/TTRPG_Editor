import customtkinter as ctk
from app_controller import AppController

if __name__ == "__main__":
    # Set the appearance mode and color theme
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Create the root window
    root = ctk.CTk()
    root.title("TTRPG Campaign Editor")
    root.geometry("1200x800")
    root.minsize(1000, 700)

    # Initialize and run the main application controller
    app = AppController(root)
    app.run()