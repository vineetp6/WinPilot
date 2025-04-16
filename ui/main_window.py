#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Window for the Windows System Manager application.
Provides the main interface and tab container.
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout, 
                             QWidget, QLabel, QStatusBar, QToolBar, 
                             QAction, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from ui.memory_tab import MemoryTab
from ui.drive_tab import DriveTab
from ui.process_tab import ProcessTab
from ui.background_tab import BackgroundTab
from ui.file_tab import FileTab
from ui.app_tab import AppTab
from ui.achievements_tab import AchievementsTab

from resources.styles import MAIN_STYLE
from resources.icons import get_icon

class MainWindow(QMainWindow):
    """Main window class for the Windows System Manager application."""
    
    def __init__(self):
        super().__init__()
        
        # Setup window properties
        self.setWindowTitle("Windows System Manager")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(MAIN_STYLE)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add header
        header = QLabel("Windows System Manager")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(header)
        
        # Create tab widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabPosition(QTabWidget.North)
        
        # Add tabs
        self.memory_tab = MemoryTab()
        self.drive_tab = DriveTab()
        self.process_tab = ProcessTab()
        self.background_tab = BackgroundTab()
        self.file_tab = FileTab()
        self.app_tab = AppTab()
        self.achievements_tab = AchievementsTab()
        
        self.tabs.addTab(self.memory_tab, get_icon("memory"), "Memory Management")
        self.tabs.addTab(self.drive_tab, get_icon("drive"), "Drive Management")
        self.tabs.addTab(self.process_tab, get_icon("process"), "Process Monitor")
        self.tabs.addTab(self.background_tab, get_icon("background"), "Background Tasks")
        self.tabs.addTab(self.file_tab, get_icon("file"), "File Operations")
        self.tabs.addTab(self.app_tab, get_icon("app"), "Application Control")
        self.tabs.addTab(self.achievements_tab, get_icon("trophy"), "Achievements")
        
        main_layout.addWidget(self.tabs)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create toolbar
        self.create_toolbar()
        
        # Connect signals
        self.tabs.currentChanged.connect(self.tab_changed)
    
    def create_toolbar(self):
        """Create the main toolbar."""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Refresh action
        refresh_action = QAction(get_icon("refresh"), "Refresh", self)
        refresh_action.setStatusTip("Refresh current view")
        refresh_action.triggered.connect(self.refresh_current_tab)
        toolbar.addAction(refresh_action)
        
        toolbar.addSeparator()
        
        # About action
        about_action = QAction(get_icon("about"), "About", self)
        about_action.setStatusTip("About this application")
        about_action.triggered.connect(self.show_about)
        toolbar.addAction(about_action)
    
    def tab_changed(self, index):
        """Handle tab change event."""
        tab_name = self.tabs.tabText(index)
        self.status_bar.showMessage(f"Viewing {tab_name}")
        
        # Refresh the newly selected tab
        self.refresh_current_tab()
    
    def refresh_current_tab(self):
        """Refresh the currently active tab."""
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
    
    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Windows System Manager",
            "<h3>Windows System Manager</h3>"
            "<p>A comprehensive system management tool for Windows.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Memory optimization</li>"
            "<li>Drive management</li>"
            "<li>Process monitoring</li>"
            "<li>Background task inspection</li>"
            "<li>File operations</li>"
            "<li>Application management</li>"
            "<li>Achievement system with rewards</li>"
            "</ul>"
            "<p>Version 1.0</p>"
            "<p><small>Running with Administrator privileges</small></p>"
        )
