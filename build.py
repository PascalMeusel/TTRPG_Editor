import os
import shutil
import subprocess
import platform

APP_NAME = "TTRPG_Editor"
MAIN_SCRIPT = "main.py"  # change if your entry file is different
ICON_FILE = None         # e.g., "icon.ico" for Windows, "icon.png" for Linux

def clean():
    for folder in ["build", "dist", "output"]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
    os.makedirs("output", exist_ok=True)

def build_linux():
    print("=== Building Linux executable ===")
    cmd = [
        "pyinstaller", "--onefile", "--noconfirm",
        "--name", APP_NAME
    ]
    if ICON_FILE:
        cmd += ["--icon", ICON_FILE]
    cmd.append(MAIN_SCRIPT)
    subprocess.check_call(cmd)
    shutil.move(os.path.join("dist", APP_NAME), f"output/{APP_NAME}_linux")

def build_windows():
    print("=== Building Windows executable (via Wine) ===")
    cmd = [
        "wine", "python", "-m", "PyInstaller",
        "--onefile", "--noconfirm",
        "--name", APP_NAME
    ]
    if ICON_FILE:
        cmd += ["--icon", ICON_FILE]
    cmd.append(MAIN_SCRIPT)
    subprocess.check_call(cmd)
    shutil.move(os.path.join("dist", f"{APP_NAME}.exe"), f"output/{APP_NAME}_windows.exe")

if __name__ == "__main__":
    clean()
    build_linux()
    build_windows()
    print("\n✅ Build complete! Check the 'output' folder.")
