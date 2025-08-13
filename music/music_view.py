import customtkinter as ctk

class MusicView:
    """Manages the UI for the Music Player panel, designed for a compact header layout."""
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame

    def setup_ui(self, controller):
        """Builds a horizontal music player UI."""
        # Main frame for the music player, sits inside the header
        music_frame = ctk.CTkFrame(self.parent_frame, fg_color="transparent")
        music_frame.pack(side="right", padx=10, pady=5)
        
        # Song selection dropdown
        self.music_list = ctk.CTkComboBox(music_frame, width=150)
        self.music_list.pack(side="left", padx=5)

        # Play/Pause/Stop buttons
        ctk.CTkButton(music_frame, text="▶", width=30, command=controller.play_song).pack(side="left", padx=(5, 2))
        ctk.CTkButton(music_frame, text="❚❚", width=30, command=controller.pause_song).pack(side="left", padx=2)
        ctk.CTkButton(music_frame, text="■", width=30, command=controller.stop_song).pack(side="left", padx=2)
        
        # Volume slider
        volume_slider = ctk.CTkSlider(music_frame, from_=0, to=1, width=100, command=controller.set_volume)
        volume_slider.set(0.5)
        volume_slider.pack(side="left", padx=(10, 5))

        # Add Music button
        ctk.CTkButton(music_frame, text="+", width=30, command=controller.add_music).pack(side="left", padx=5)
        
    def update_music_list(self, songs):
        """Refreshes the combobox with the list of available songs."""
        current_song = self.music_list.get()
        self.music_list.configure(values=songs or ["No music files"])
        
        if current_song in songs:
            self.music_list.set(current_song)
        elif songs:
            self.music_list.set(songs[0])
        else:
            self.music_list.set("")