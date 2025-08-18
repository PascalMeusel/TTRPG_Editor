import os
import shutil
from utils import resource_path
try:
    import pygame
except ImportError:
    print("Pygame not found. Music player functionality will be disabled.")
    pygame = None

class MusicModel:
    """Model for handling audio playback and file management."""
    def __init__(self, music_dir_name='assets/music'):
        self.music_dir = resource_path(music_dir_name)
        if not os.path.exists(self.music_dir):
            os.makedirs(self.music_dir)
        if pygame:
            pygame.mixer.init()
        
        self.paused = False
        self.current_song = None

    def get_music_files(self):
        """Returns a sorted list of music files in the assets directory."""
        if not pygame: return ["Pygame not installed"]
        try:
            return sorted([f for f in os.listdir(self.music_dir) if f.endswith(('.mp3', '.wav'))])
        except FileNotFoundError:
            return []
            
    def add_music_files(self, source_paths):
        """Copies music files from a list of source paths to the assets directory."""
        copied_count = 0
        for src_path in source_paths:
            if not os.path.exists(src_path):
                continue
            
            filename = os.path.basename(src_path)
            dest_path = os.path.join(self.music_dir, filename)
            
            try:
                shutil.copy(src_path, dest_path)
                copied_count += 1
            except shutil.Error as e:
                print(f"Error copying file {filename}: {e}")
            except IOError as e:
                print(f"I/O error copying file {filename}: {e}")
        return copied_count

    def play(self, song_name):
        """Loads and plays a new song, resetting the paused state."""
        if not pygame or not song_name: return
        filepath = os.path.join(self.music_dir, song_name)
        if os.path.exists(filepath):
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play(-1)
            self.paused = False
            self.current_song = song_name

    def toggle_pause(self):
        """Correctly toggles pause/unpause using a state flag."""
        if not pygame: return
        
        # --- FIX: Removed the flawed get_busy() check ---
        # This allows the function to work correctly when unpausing.

        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
        else:
            # Only try to pause if a song is actually loaded and playing
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.pause()
                self.paused = True

    def stop(self):
        """Stops the music and unloads the file to fully clear the state."""
        if not pygame: return
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.paused = False
        self.current_song = None

    def set_volume(self, volume):
        if not pygame: return
        pygame.mixer.music.set_volume(float(volume))