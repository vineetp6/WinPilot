#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application management tab for Windows System Manager.
Handles listing, uninstalling, and installing applications.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QLineEdit, QComboBox, QFileDialog, QDialog, QFormLayout,
                            QTextEdit, QApplication, QCheckBox, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QSize
from PyQt5.QtGui import QFont, QIcon, QCursor

from utils.app_utils import (get_installed_apps, get_windows_apps, uninstall_app, 
                           install_app, get_app_details, uninstall_windows_app)
import os

class InstallDialog(QDialog):
    """Dialog for installing applications from .exe files."""
    
    def __init__(self, exe_path=None, parent=None):
        super().__init__(parent)
        self.exe_path = exe_path
        self.args = ""
        self.silent = True
        
        self.setWindowTitle("Install Application")
        self.resize(500, 300)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # File selection
        file_group = QGroupBox("Installation File")
        file_layout = QHBoxLayout(file_group)
        
        self.file_edit = QLineEdit(self.exe_path if self.exe_path else "")
        self.file_edit.setPlaceholderText("Select an .exe file to install")
        self.file_edit.setReadOnly(True)
        
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(self.browse_btn)
        
        layout.addWidget(file_group)
        
        # Installation options
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout(options_group)
        
        # Arguments
        args_layout = QHBoxLayout()
        args_label = QLabel("Arguments:")
        self.args_edit = QLineEdit()
        self.args_edit.setPlaceholderText("Optional command line arguments")
        args_layout.addWidget(args_label)
        args_layout.addWidget(self.args_edit)
        options_layout.addLayout(args_layout)
        
        # Silent installation checkbox
        self.silent_check = QCheckBox("Silent Installation (if supported)")
        self.silent_check.setChecked(True)
        options_layout.addWidget(self.silent_check)
        
        # Warning note
        note_label = QLabel("Note: Installing applications may require administrative privileges. " +
                           "Some installers will show their own interface and may ignore the options above.")
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #555;")
        options_layout.addWidget(note_label)
        
        layout.addWidget(options_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.install_btn = QPushButton("Install")
        self.install_btn.clicked.connect(self.accept)
        self.install_btn.setEnabled(bool(self.exe_path))
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.install_btn)
        
        layout.addLayout(button_layout)
    
    def browse_file(self):
        """Browse for an executable file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Installation File",
            "",
            "Executable Files (*.exe);;All Files (*.*)"
        )
        
        if file_path:
            self.file_edit.setText(file_path)
            self.exe_path = file_path
            self.install_btn.setEnabled(True)
    
    def get_install_options(self):
        """Get the installation options."""
        return {
            'exe_path': self.exe_path,
            'args': self.args_edit.text(),
            'silent': self.silent_check.isChecked()
        }

class AppDetailDialog(QDialog):
    """Dialog for displaying application details."""
    
    def __init__(self, app_data, parent=None):
        super().__init__(parent)
        self.app_data = app_data
        self.setWindowTitle(f"Application Details - {app_data['name']}")
        self.resize(500, 300)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Basic info
        form_layout = QFormLayout()
        
        form_layout.addRow("Name:", QLabel(self.app_data.get('name', 'N/A')))
        form_layout.addRow("Version:", QLabel(self.app_data.get('version', 'N/A')))
        form_layout.addRow("Publisher:", QLabel(self.app_data.get('publisher', 'N/A')))
        form_layout.addRow("Install Date:", QLabel(self.app_data.get('install_date', 'N/A')))
        form_layout.addRow("Size:", QLabel(self.app_data.get('size', 'N/A')))
        form_layout.addRow("Type:", QLabel(self.app_data.get('type', 'N/A')))
        
        # Installation path (if available)
        if 'install_location' in self.app_data and self.app_data['install_location']:
            form_layout.addRow("Install Location:", QLabel(self.app_data['install_location']))
        
        # Uninstall string (if available)
        if 'uninstall_string' in self.app_data and self.app_data['uninstall_string']:
            uninstall_label = QLabel(self.app_data['uninstall_string'])
            uninstall_label.setWordWrap(True)
            form_layout.addRow("Uninstall Command:", uninstall_label)
        
        layout.addLayout(form_layout)
        
        # Additional info (if available)
        if 'description' in self.app_data and self.app_data['description']:
            group_box = QGroupBox("Description")
            group_layout = QVBoxLayout(group_box)
            
            desc_label = QLabel(self.app_data['description'])
            desc_label.setWordWrap(True)
            group_layout.addWidget(desc_label)
            
            layout.addWidget(group_box)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class AppFilterWidget(QWidget):
    """Widget for filtering applications in the table."""
    
    filterChanged = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.filter_label = QLabel("Filter:")
        layout.addWidget(self.filter_label)
        
        self.filter_text = QLineEdit()
        self.filter_text.setPlaceholderText("Enter app name or publisher")
        self.filter_text.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_text)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All Apps", "Desktop Apps", "Windows Store Apps", "System Updates"])
        self.filter_type.currentTextChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_type)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_filter)
        layout.addWidget(self.clear_btn)
    
    def on_filter_changed(self, *args):
        """Emit signal when filter changes."""
        self.filterChanged.emit(
            self.filter_text.text(),
            self.filter_type.currentText()
        )
    
    def clear_filter(self):
        """Clear all filters."""
        self.filter_text.clear()
        self.filter_type.setCurrentIndex(0)

class AppTab(QWidget):
    """Application management tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.apps_list = []
        self.windows_apps_list = []
        self.init_ui()
        
        # Initial data load
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # App filter
        self.filter_widget = AppFilterWidget()
        self.filter_widget.filterChanged.connect(self.apply_filter)
        main_layout.addWidget(self.filter_widget)
        
        # Apps table
        self.apps_table = QTableWidget()
        self.apps_table.setColumnCount(5)
        self.apps_table.setHorizontalHeaderLabels([
            "Name", "Version", "Publisher", "Install Date", "Type"
        ])
        self.apps_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.apps_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.apps_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.apps_table.setAlternatingRowColors(True)
        self.apps_table.setSortingEnabled(True)
        self.apps_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.apps_table.customContextMenuRequested.connect(self.show_context_menu)
        self.apps_table.doubleClicked.connect(self.show_app_details)
        
        main_layout.addWidget(self.apps_table)
        
        # Action buttons
        actions_group = QGroupBox("Application Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.refresh_btn = QPushButton("Refresh Apps List")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.uninstall_btn = QPushButton("Uninstall Selected")
        self.uninstall_btn.clicked.connect(self.uninstall_selected)
        self.uninstall_btn.setEnabled(False)
        
        self.install_btn = QPushButton("Install New App...")
        self.install_btn.clicked.connect(self.install_new_app)
        
        self.details_btn = QPushButton("View Details")
        self.details_btn.clicked.connect(self.show_selected_app_details)
        self.details_btn.setEnabled(False)
        
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.uninstall_btn)
        actions_layout.addWidget(self.install_btn)
        actions_layout.addWidget(self.details_btn)
        
        main_layout.addWidget(actions_group)
        
        # Status label
        self.status_label = QLabel("Loading applications...")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Enable/disable buttons based on selection
        self.apps_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def refresh(self):
        """Refresh the applications list."""
        self.status_label.setText("Loading applications...")
        QApplication.processEvents()
        
        try:
            # Get installed desktop applications
            self.apps_list = get_installed_apps()
            
            # Get Windows Store apps
            self.windows_apps_list = get_windows_apps()
            
            # Combine the lists
            combined_list = self.apps_list + self.windows_apps_list
            
            # Clear and rebuild table
            self.apps_table.setSortingEnabled(False)  # Disable sorting temporarily
            self.apps_table.setRowCount(0)
            
            for i, app in enumerate(combined_list):
                self.apps_table.insertRow(i)
                
                # Name
                name_item = QTableWidgetItem(app['name'])
                name_item.setData(Qt.UserRole, app)
                self.apps_table.setItem(i, 0, name_item)
                
                # Version
                self.apps_table.setItem(i, 1, QTableWidgetItem(app.get('version', 'N/A')))
                
                # Publisher
                self.apps_table.setItem(i, 2, QTableWidgetItem(app.get('publisher', 'N/A')))
                
                # Install Date
                self.apps_table.setItem(i, 3, QTableWidgetItem(app.get('install_date', 'N/A')))
                
                # Type
                self.apps_table.setItem(i, 4, QTableWidgetItem(app.get('type', 'Desktop App')))
            
            # Re-enable sorting
            self.apps_table.setSortingEnabled(True)
            
            # Update status
            self.status_label.setText(f"Found {len(combined_list)} applications")
            
            # Apply current filter
            self.apply_filter(
                self.filter_widget.filter_text.text(),
                self.filter_widget.filter_type.currentText()
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing applications list: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def apply_filter(self, text, filter_type):
        """Apply filtering to the applications table."""
        for row in range(self.apps_table.rowCount()):
            show_row = True
            
            # Text filter
            if text:
                name_match = text.lower() in self.apps_table.item(row, 0).text().lower()
                publisher_match = text.lower() in self.apps_table.item(row, 2).text().lower()
                show_row = name_match or publisher_match
            
            # Type filter
            if show_row and filter_type != "All Apps":
                app_type = self.apps_table.item(row, 4).text()
                if filter_type == "Desktop Apps":
                    show_row = app_type == "Desktop App"
                elif filter_type == "Windows Store Apps":
                    show_row = app_type == "Windows Store App"
                elif filter_type == "System Updates":
                    show_row = app_type == "Update" or "Update" in app_type
            
            self.apps_table.setRowHidden(row, not show_row)
        
        # Update filtered count
        visible_count = sum(1 for row in range(self.apps_table.rowCount()) 
                           if not self.apps_table.isRowHidden(row))
        
        self.status_label.setText(f"Showing {visible_count} of {self.apps_table.rowCount()} applications")
    
    def on_selection_changed(self):
        """Handle selection changes in the table."""
        has_selection = len(self.apps_table.selectedItems()) > 0
        self.uninstall_btn.setEnabled(has_selection)
        self.details_btn.setEnabled(has_selection)
    
    def get_selected_app(self):
        """Get the currently selected application."""
        selected_items = self.apps_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select an application first.")
            return None
        
        row = selected_items[0].row()
        app_item = self.apps_table.item(row, 0)
        return app_item.data(Qt.UserRole)
    
    def uninstall_selected(self):
        """Uninstall the selected application."""
        app_data = self.get_selected_app()
        if not app_data:
            return
        
        # Confirm uninstallation
        confirm = QMessageBox.warning(
            self,
            "Confirm Uninstallation",
            f"Are you sure you want to uninstall '{app_data['name']}'?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.status_label.setText(f"Uninstalling {app_data['name']}...")
                QApplication.processEvents()
                
                # Different uninstall methods based on app type
                if app_data.get('type') == 'Windows Store App':
                    result = uninstall_windows_app(app_data.get('package_full_name', ''))
                else:
                    result = uninstall_app(app_data)
                
                QApplication.restoreOverrideCursor()
                
                if result:
                    QMessageBox.information(
                        self,
                        "Uninstallation Complete",
                        f"'{app_data['name']}' has been uninstalled successfully."
                    )
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self,
                        "Uninstallation Failed",
                        f"Failed to uninstall '{app_data['name']}'.\n\nThis may require administrator privileges or the uninstaller requires manual interaction."
                    )
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(
                    self,
                    "Uninstallation Error",
                    f"Error during uninstallation: {str(e)}"
                )
                self.status_label.setText(f"Error: {str(e)}")
    
    def install_new_app(self):
        """Install a new application from an .exe file."""
        dialog = InstallDialog(parent=self)
        
        if dialog.exec_() == QDialog.Accepted:
            options = dialog.get_install_options()
            
            try:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                self.status_label.setText(f"Installing from {os.path.basename(options['exe_path'])}...")
                QApplication.processEvents()
                
                result = install_app(
                    options['exe_path'],
                    options['args'],
                    options['silent']
                )
                
                QApplication.restoreOverrideCursor()
                
                if result:
                    QMessageBox.information(
                        self,
                        "Installation Complete",
                        f"The application has been installed successfully."
                    )
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self,
                        "Installation Failed",
                        f"Failed to complete the installation.\n\nThis may require administrator privileges or the installer may have failed."
                    )
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(
                    self,
                    "Installation Error",
                    f"Error during installation: {str(e)}"
                )
                self.status_label.setText(f"Error: {str(e)}")
    
    def show_selected_app_details(self):
        """Show details for the selected application."""
        app_data = self.get_selected_app()
        if app_data:
            self.show_app_details(None, app_data)
    
    def show_app_details(self, index=None, app_data=None):
        """Show detailed information about an application."""
        try:
            if not app_data:
                item = self.apps_table.item(index.row(), 0)
                app_data = item.data(Qt.UserRole)
            
            # Get detailed app info if needed
            if app_data.get('type') != 'Windows Store App':
                app_details = get_app_details(app_data)
            else:
                app_details = app_data
            
            dialog = AppDetailDialog(app_details, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting application details: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for the apps table."""
        if not self.apps_table.selectedItems():
            return
        
        row = self.apps_table.itemAt(position).row()
        self.apps_table.selectRow(row)
        
        app_data = self.get_selected_app()
        if not app_data:
            return
        
        menu = QMenu(self)
        
        uninstall_action = QAction("Uninstall", self)
        uninstall_action.triggered.connect(self.uninstall_selected)
        menu.addAction(uninstall_action)
        
        menu.addSeparator()
        
        details_action = QAction("View Details", self)
        details_action.triggered.connect(self.show_selected_app_details)
        menu.addAction(details_action)
        
        refresh_action = QAction("Refresh List", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.apps_table.mapToGlobal(position))
