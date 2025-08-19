# TTRPG Campaign Editor

A versatile, feature-rich desktop application designed for Game Masters to create, manage, and run their tabletop role-playing game campaigns. Built with Python and the modern `customtkinter` library, this tool provides a powerful, all-in-one solution for world-building, character management, and in-session support.
---

## ✨ Key Features

This project has been architecturally designed to be modular and highly functional, providing a fluid experience for the user.

#### Core Engine & UI
*   **Dynamic Two-Pane Layout:** Open and view any two features side-by-side for maximum productivity.
*   **Resizable Panes:** A draggable central divider allows you to resize the panes to your liking.
*   **Pane Pinning:** Pin a feature in one pane to keep it visible while you cycle through other tools in the second pane.
*   **Fullscreen Map Mode:** The map editor can be expanded to take over the entire content area, providing maximum space for drawing and viewing.
*   **Caching System:** Features are loaded into memory once per session, making subsequent switching between them instantaneous.
*   **Cross-Platform Build Script:** Includes a `build.sh` script to easily compile executables for both Linux and Windows.

#### Campaign & Ruleset Management
*   **System-Agnostic Ruleset Creator:** Define your own game system by creating custom attributes, skills, and formulas.
*   **Campaign Management:** Create and load distinct campaigns, each with its own set of characters, NPCs, items, and maps.

#### Character, NPC & Item Management
*   **Character & NPC Creator:** Create detailed characters and NPCs based on your campaign's custom ruleset.
*   **Advanced Character Sheets:** View and edit character stats, which are automatically recalculated based on equipped items.
*   **Full Inventory System:** Add items from a central database to characters and NPCs, manage quantities, and toggle their "equipped" state.
*   **Item Editor:** A dedicated editor to create custom items with unique descriptions, types, and stat-modifying properties.
*   **Procedural NPC Generator:** Instantly generate a unique, fully-fleshed-out NPC with plausible stats, a detailed multi-part backstory, personality traits, and thematically appropriate starting items.

#### World Building & In-Session Tools
*   **Multi-Level Map Editor:** Draw and edit maps with simple brush and rectangle tools. For "inside" maps like dungeons, create and switch between multiple floors.
*   **Procedural Map Generators:**
    *   **Dungeon:** Creates a classic dungeon crawl with interconnected rooms and corridors.
    *   **Town:** Generates believable town layouts with roads, zones, and intelligently placed buildings. Features multiple templates (Crossroads, Main Street, Riverside) for variety.
    *   **Winding Road:** Creates a path through a wilderness area, complete with scenery.
*   **Generator-Specific Settings:** Fine-tune the procedural generation with sliders and options for room count, building density, path width, and more.
*   **Landmarks & Tokens:** Place text-based landmarks and PC/NPC tokens on the map to track points of interest and positions.
*   **Integrated Music Player:** A compact audio player in the header to manage background music and set the mood for your sessions.

---

## 🚀 Setup & Installation

To run or build the project from the source, you will need a few prerequisites.

#### Prerequisites
*   **Python 3.10+:** Download from [python.org](https://www.python.org/downloads/).
*   **Git:** Required to clone the repository. For Windows users, it is **essential** to install **[Git for Windows](https://git-scm.com/download/win)**, as this includes **Git Bash**, which is necessary to run the build script.
*   **(For Building on Linux for Windows):** You must have `wine` and a Python installation inside your Wine environment.

#### Installation Steps
1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd TTRPG_Editor
    ```

2.  **Create and activate a Python virtual environment:**
    ```bash
    # On Linux / macOS
    python3 -m venv venv
    source venv/bin/activate

    # On Windows (using Git Bash or Command Prompt)
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Create and install dependencies:**
    First, create a `requirements.txt` file from your active virtual environment. This should be done once and committed to the repository.
    ```bash
    pip freeze > requirements.txt
    ```
    Now, anyone (including your future self) can install the necessary packages with a single command:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🛠️ Building the Executables

The included `build.sh` script automates the creation of executables for both Linux and Windows.

#### Dependencies
The following Python packages must be installed in **both** your native environment and your **Wine** Python environment for the script to succeed:
*   `customtkinter`
*   `pygame`
*   `Pillow`

You can install them in Wine by running:
```bash
wine python -m pip install customtkinter pygame Pillow