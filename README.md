# 🖥️ Windows Control Center (Python Desktop App)

A **Windows desktop application** built with Python that acts as an all-in-one **control center** for Windows OS operations.

---

## 🚀 Features

### 🧠 Memory Management
- Display current memory usage
- Run optimization routines
- Real-time memory diagnostics

### 💾 Drive Name Management
- View drive names
- Easily rename drives

### 🧩 Process Monitoring
- List all running processes
- Show CPU and memory usage for each process

### 🕵️ Background Information Display
- Real-time display of system activity
- Includes system services and background tasks

### 📁 Folder and File Operations
- Create, rename, and delete folders
- Basic file management functions

### 📦 Application Management
- Delete installed Windows apps
- Uninstall programs safely

---

## 🛠️ Built With

- Python
- Tkinter / PyQt / (your GUI framework)
- psutil, os, subprocess, etc.

---

## 📸 Screenshots

*(Include screenshots)*

---

## 📂 How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/windows-control-center.git

2. Run - Python main.py


## Folder Structure
WindowsMaster/
├── resources/
│   ├── icons.py         # SVG icon definitions for the application UI
│   └── styles.py        # CSS-style definitions for the application UI
├── ui/
│   ├── __init__.py      # UI package initialization
│   ├── app_tab.py       # Application management tab (install/uninstall apps)
│   ├── background_tab.py # Background tasks monitoring (services, startup items)
│   ├── drive_tab.py     # Drive management tab (view, label drives)
│   ├── file_tab.py      # File operations tab (copy, move, delete files)
│   ├── main_window.py   # Main application window with tab container
│   ├── memory_tab.py    # Memory management tab (view usage, optimize)
│   └── process_tab.py   # Process monitoring tab (view, end processes)
├── utils/
│   ├── __init__.py      # Utils package initialization
│   ├── app_utils.py     # Utilities for managing applications
│   ├── background_utils.py # Utilities for background tasks
│   ├── drive_utils.py   # Utilities for drive operations
│   ├── file_utils.py    # Utilities for file operations
│   ├── memory_utils.py  # Utilities for memory monitoring and optimization
│   └── process_utils.py # Utilities for process monitoring and control
├── main.py              # Main application entry point
└── pyproject.toml       # Project dependencies and metadata


## When Application freezes use fix_freeze.py before running pyinstaller command below 
## Build Executable with PyInstaller

To create a standalone Windows executable for **Windows System Manager**, use the following command:

```bash
pyinstaller --name "Windows System Manager" --windowed --icon=generated-icon.png \
--collect-all PyQt5 --collect-all win32com \
--hidden-import win32api --hidden-import win32con \
--hidden-import win32gui --hidden-import pythoncom --hidden-import pywintypes \
--add-data "resources;resources" --add-data "ui;ui" --add-data "utils;utils" main.py
