#!/bin/bash

# ==============================================================================
# TTRPG Editor - Universal Build Script for Linux and Windows
# ==============================================================================

# --- Configuration ---
APP_NAME="TTRPG_Editor"
MAIN_SCRIPT="main.py"
OUTPUT_DIR="output"
LINUX_DIR="$OUTPUT_DIR/linux"
WINDOWS_DIR="$OUTPUT_DIR/windows"

# --- Pre-build Checks and Cleanup ---
echo "--- Cleaning up old builds ---"
rm -rf build dist "$OUTPUT_DIR" *.spec
mkdir -p "$LINUX_DIR" "$WINDOWS_DIR"
echo "Cleanup complete. Output directories are ready."
echo ""


# --- Build for Linux ---
echo "--- (1/2) Building for Linux ---"
# Check if PyInstaller is installed on the host system
if ! command -v pyinstaller &> /dev/null; then
    echo "[ERROR] PyInstaller not found on your Linux system."
    echo "Please run: pip install pyinstaller"
    exit 1
fi

pyinstaller \
    --name "$APP_NAME" \
    --onefile \
    --windowed \
    --clean \
    --add-data "data:data" \
    --add-data "assets:assets" \
    "$MAIN_SCRIPT"

# Check if build was successful and move the executable
if [ -f "dist/$APP_NAME" ]; then
    echo "Linux build successful."
    mv "dist/$APP_NAME" "$LINUX_DIR/"
    echo "Linux executable moved to '$LINUX_DIR'"
else
    echo "[ERROR] Linux build FAILED. Check the output above for errors."
    # We exit here because if the Linux build fails, something is likely wrong with the setup
    exit 1
fi
echo ""


# --- Build for Windows (using Wine) ---
echo "--- (2/2) Building for Windows using Wine ---"

# Auto-detect the path to pyinstaller.exe in the Wine environment for user 'pascal'
echo "Searching for pyinstaller.exe in your Wine environment... (this may take a moment)"
WINE_PYINSTALLER_PATH=$(find "$HOME/.wine/" -type f -name "pyinstaller.exe" 2>/dev/null | head -n 1)

# Check if the path was found
if [ -z "$WINE_PYINSTALLER_PATH" ]; then
    echo "[ERROR] Could not automatically find pyinstaller.exe in your .wine directory."
    echo "Please ensure you have installed Python and PyInstaller within your Wine environment."
    echo "You can do this by running: wine python -m pip install pyinstaller"
    exit 1
fi

echo "Found Windows PyInstaller at: $WINE_PYINSTALLER_PATH"

# Execute the Windows build using Wine
wine "$WINE_PYINSTALLER_PATH" \
    --name "$APP_NAME" \
    --onefile \
    --windowed \
    --clean \
    --add-data "data;data" \
    --add-data "assets;assets" \
    "$MAIN_SCRIPT"

# Check if build was successful and move the executable
if [ -f "dist/$APP_NAME.exe" ]; then
    echo "Windows build successful."
    mv "dist/$APP_NAME.exe" "$WINDOWS_DIR/"
    echo "Windows executable moved to '$WINDOWS_DIR'"
else
    echo "[ERROR] Windows build FAILED. Check the output above for errors."
    exit 1
fi
echo ""


# --- Final Cleanup ---
echo "--- Cleaning up intermediate files ---"
rm -rf build dist *.spec
echo "Build process complete!"
echo "You can find your executables in the '$OUTPUT_DIR' directory."