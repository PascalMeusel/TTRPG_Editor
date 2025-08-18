from tkinter import filedialog
from .music_model import MusicModel
from .music_view import MusicView
from custom_dialogs import MessageBox
try:
    import pygame
except ImportError:
    pygame = None

class MusicController:
    """Controller for the Music Player feature."""
    def __init__(self, app_controller, parent_frame):
        self.app_controller = app_controller
        self.model = MusicModel()
        self.view = MusicView(parent_frame)
        self.view.setup_ui(self)
        self.refresh_music_list()

    def refresh_music_list(self):
        """Gets the updated song list from the model and tells the view to display it."""
        songs = self.model.get_music_files()
        self.view.update_music_list(songs)

    def add_music(self):
        """Opens a file dialog for the user to select music files to add."""
        file_types = [("Audio Files", "*.mp3 *.wav"), ("All files", "*.*")]
        source_paths = filedialog.askopenfilenames(title="Select Music Files", filetypes=file_types)
        
        if not source_paths: return
            
        copied_count = self.model.add_music_files(source_paths)
        
        if copied_count > 0:
            MessageBox.showinfo("Music Added", f"Successfully added {copied_count} new song(s).", self.view.parent_frame)
            self.refresh_music_list()
        else:
            MessageBox.showwarning("No Music Added", "No new files were added. They may have already existed or there was an error.", self.view.parent_frame)
    
    def handle_play_pause(self):
        """Smart handler for the combined Play/Pause button."""
        if not pygame:
            return

        selected_song = self.view.music_list.get()
        if not selected_song or "No music" in selected_song:
            return

        # --- FIX: Simplified and corrected logic ---
        # If a different song is selected from the dropdown, it MUST be a fresh play.
        if self.model.current_song != selected_song:
            self.model.play(selected_song)
        # Otherwise, the song is the same, so we simply toggle between pause and unpause.
        else:
            self.model.toggle_pause()

    def stop_song(self):
        self.model.stop()

    def set_volume(self, volume):
        self.model.set_volume(volume)