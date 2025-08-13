import sys
import os

def resource_path(relative_path):
    """
    Get the absolute path to a resource, works for dev and for PyInstaller.
    This is the standard, recommended way to handle assets in a bundled app.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not bundled, the base path is the directory of the main script
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)