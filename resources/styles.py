#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Style definitions for Windows System Manager.
Contains CSS-style definitions for the application UI.
"""

# Main application style
MAIN_STYLE = """
QMainWindow {
    background-color: #f0f0f0;
}

QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
}

QLabel {
    padding: 2px;
}

QPushButton {
    background-color: #0078d7;
    color: white;
    border: 1px solid #0078d7;
    border-radius: 3px;
    padding: 5px 10px;
    min-width: 80px;
}

QPushButton:hover {
    background-color: #1e88e5;
    border: 1px solid #1e88e5;
}

QPushButton:pressed {
    background-color: #0060ac;
    border: 1px solid #0060ac;
}

QPushButton:disabled {
    background-color: #cccccc;
    color: #888888;
    border: 1px solid #cccccc;
}

QTabWidget::pane {
    border: 1px solid #cccccc;
    background-color: white;
}

QTabBar::tab {
    background-color: #e0e0e0;
    border: 1px solid #cccccc;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 6px 12px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: white;
    border-bottom: 1px solid white;
}

QTabBar::tab:hover:!selected {
    background-color: #eaeaea;
}

QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 4px;
    margin-top: 8px;
    padding-top: 8px;
    background-color: #fafafa;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 5px;
    color: #0078d7;
    font-weight: bold;
}

QTableWidget {
    border: 1px solid #cccccc;
    gridline-color: #e0e0e0;
    selection-background-color: #ddeeff;
    selection-color: black;
}

QTableWidget::item {
    padding: 3px;
}

QHeaderView::section {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    padding: 4px;
    font-weight: bold;
}

QToolBar {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
    spacing: 3px;
}

QToolButton {
    background-color: transparent;
    border-radius: 3px;
}

QToolButton:hover {
    background-color: #ddeeff;
}

QToolButton:pressed {
    background-color: #c0d8f0;
}

QLineEdit {
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px;
    background-color: white;
}

QLineEdit:focus {
    border: 1px solid #0078d7;
}

QProgressBar {
    border: 1px solid #cccccc;
    border-radius: 3px;
    text-align: center;
    background-color: #f0f0f0;
}

QProgressBar::chunk {
    background-color: #2196f3;
    width: 10px;
    margin: 1px;
}

QComboBox {
    border: 1px solid #cccccc;
    border-radius: 3px;
    padding: 3px 5px;
    min-width: 100px;
    background-color: white;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #cccccc;
}

QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}

QComboBox:on {
    border: 1px solid #0078d7;
}

QComboBox QAbstractItemView {
    border: 1px solid #cccccc;
    selection-background-color: #ddeeff;
    selection-color: black;
    background-color: white;
}

QStatusBar {
    background-color: #f0f0f0;
    border-top: 1px solid #cccccc;
    color: #333333;
}

QTreeView {
    border: 1px solid #cccccc;
    background-color: white;
    selection-background-color: #ddeeff;
    selection-color: black;
}

QTreeView::item {
    padding: 3px;
}

QSplitter::handle {
    background-color: #f0f0f0;
    border: 1px solid #cccccc;
}

QMenuBar {
    background-color: #f5f5f5;
    border-bottom: 1px solid #e0e0e0;
}

QMenuBar::item {
    padding: 5px 10px;
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #ddeeff;
}

QMenu {
    background-color: white;
    border: 1px solid #cccccc;
}

QMenu::item {
    padding: 5px 25px 5px 25px;
}

QMenu::item:selected {
    background-color: #ddeeff;
}

QScrollBar:vertical {
    border: 1px solid #cccccc;
    background: #f0f0f0;
    width: 15px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 20px;
}

QScrollBar:horizontal {
    border: 1px solid #cccccc;
    background: #f0f0f0;
    height: 15px;
}

QScrollBar::handle:horizontal {
    background: #c0c0c0;
    min-width: 20px;
}

QCheckBox {
    spacing: 5px;
}

QCheckBox::indicator {
    width: 13px;
    height: 13px;
}

QCheckBox::indicator:unchecked {
    border: 1px solid #cccccc;
    background-color: white;
}

QCheckBox::indicator:checked {
    border: 1px solid #0078d7;
    background-color: #0078d7;
}
"""

# Style for the memory tab
MEMORY_TAB_STYLE = """
MemoryProgressBar {
    text-align: center;
    height: 25px;
    font-weight: bold;
}
"""

# Style for process monitoring
PROCESS_TAB_STYLE = """
QPushButton#endProcessButton {
    background-color: #d32f2f;
    border: 1px solid #b71c1c;
}

QPushButton#endProcessButton:hover {
    background-color: #f44336;
    border: 1px solid #d32f2f;
}

QPushButton#endProcessButton:pressed {
    background-color: #b71c1c;
    border: 1px solid #b71c1c;
}
"""

# Style for application tab
APP_TAB_STYLE = """
QPushButton#uninstallButton {
    background-color: #d32f2f;
    border: 1px solid #b71c1c;
}

QPushButton#uninstallButton:hover {
    background-color: #f44336;
    border: 1px solid #d32f2f;
}

QPushButton#uninstallButton:pressed {
    background-color: #b71c1c;
    border: 1px solid #b71c1c;
}

QPushButton#installButton {
    background-color: #388e3c;
    border: 1px solid #2e7d32;
}

QPushButton#installButton:hover {
    background-color: #4caf50;
    border: 1px solid #388e3c;
}

QPushButton#installButton:pressed {
    background-color: #2e7d32;
    border: 1px solid #2e7d32;
}
"""
