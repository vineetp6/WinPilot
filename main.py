#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows System Manager - Main Application Entry Point
A comprehensive system management tool for Windows operating systems.
"""

import sys
import os
import platform

# Check if running on Windows
if platform.system() != 'Windows':
    print("This application is designed for Windows operating systems only.")
    sys.exit(1)

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QIcon
    from ui.main_window import MainWindow
except ImportError as e:
    print(f"Error: Required dependency not found: {e}")
    print("Please install the required dependencies: PyQt5, psutil, pywin32")
    sys.exit(1)

def main():
    """Main entry point for the application."""
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("Windows System Manager")
    app.setStyle("Fusion")  # Use Fusion style for a modern look
    
    # Create the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
