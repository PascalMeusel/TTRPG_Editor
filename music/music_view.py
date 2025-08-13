import customtkinter as ctk

class MusicView:
    """Manages the UI for the Music Player panel."""
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame

    def setup_ui(self, controller):
        music_frame = ctk.CTkFrame(self.parent_frame)
        music_frame.pack(pady=(0, 20), padx=20, fill="x")
        ctk.CTkLabel(music_frame, text="Music Player", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)
        
        # Add Music button
        ctk.CTkButton(music_frame, text="Add Music from PC...", command=controller.add_music).pack(pady=(5, 10))

        self.music_list = ctk.CTkComboBox(music_frame)
        self.music_list.pack(pady=5, padx=10, fill="x")

        music_controls = ctk.CTkFrame(music_frame, fg_color="transparent")
        music_controls.pack(pady=5)
        ctk.CTkButton(music_controls, text="Play", width=70, command=controller.play_song).pack(side="left", padx=5)
        ctk.CTkButton(music_controls, text="Pause", width=70, command=controller.pause_song).pack(side="left")
        ctk.CTkButton(music_controls, text="Stop", width=70, command=controller.stop_song).pack(side="left", padx=5)
        
        volume_slider = ctk.CTkSlider(music_frame, from_=0, to=1, command=controller.set_volume)
        volume_slider.set(0.5)
        volume_slider.pack(pady=10, padx=10, fill="x")
        
    def update_music_list(self, songs):
        """Refreshes the combobox with the list of available songs."""
        current_song = self.music_list.get()
        self.music_list.configure(values=songs or ["No music files found"])
        
        # If the currently selected song still exists, keep it selected. Otherwise, default to the first song.
        if current_song in songs:
            self.music_list.set(current_song)
        elif songs:
            self.music_list.set(songs[0])
        else:
            self.music_list.set("")