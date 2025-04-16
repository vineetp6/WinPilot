#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Background tasks monitoring tab for Windows System Manager.
Displays system services, scheduled tasks, and startup programs.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QTabWidget, QComboBox, QLineEdit, QCheckBox,
                            QApplication, QMenu, QAction, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QCursor

from utils.background_utils import (get_services, get_startup_items, get_scheduled_tasks,
                                   toggle_service, toggle_startup_item, get_service_details,
                                   get_startup_details, get_scheduled_task_details)

class BackgroundItemDetailDialog(QDialog):
    """Dialog for displaying detailed information about background items."""
    
    def __init__(self, item_type, item_data, parent=None):
        super().__init__(parent)
        self.item_type = item_type
        self.item_data = item_data
        
        self.setWindowTitle(f"{item_type} Details - {item_data.get('name', 'Unknown')}")
        self.setMinimumWidth(500)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Create form layout for details
        form_layout = QFormLayout()
        
        # Different fields for different item types
        if self.item_type == "Service":
            form_layout.addRow("Name:", QLabel(self.item_data.get('name', 'N/A')))
            form_layout.addRow("Display Name:", QLabel(self.item_data.get('display_name', 'N/A')))
            form_layout.addRow("Description:", QLabel(self.item_data.get('description', 'N/A')))
            form_layout.addRow("Status:", QLabel(self.item_data.get('status', 'N/A')))
            form_layout.addRow("Startup Type:", QLabel(self.item_data.get('start_type', 'N/A')))
            form_layout.addRow("Binary Path:", QLabel(self.item_data.get('binary_path', 'N/A')))
            form_layout.addRow("Account:", QLabel(self.item_data.get('username', 'N/A')))
            form_layout.addRow("PID:", QLabel(str(self.item_data.get('pid', 'N/A'))))
            
        elif self.item_type == "Startup Item":
            form_layout.addRow("Name:", QLabel(self.item_data.get('name', 'N/A')))
            form_layout.addRow("Command:", QLabel(self.item_data.get('command', 'N/A')))
            form_layout.addRow("Location:", QLabel(self.item_data.get('location', 'N/A')))
            form_layout.addRow("User:", QLabel(self.item_data.get('user', 'N/A')))
            form_layout.addRow("Enabled:", QLabel("Yes" if self.item_data.get('enabled', False) else "No"))
            form_layout.addRow("Manufacturer:", QLabel(self.item_data.get('manufacturer', 'N/A')))
            
        elif self.item_type == "Scheduled Task":
            form_layout.addRow("Name:", QLabel(self.item_data.get('name', 'N/A')))
            form_layout.addRow("Path:", QLabel(self.item_data.get('path', 'N/A')))
            form_layout.addRow("Status:", QLabel(self.item_data.get('status', 'N/A')))
            form_layout.addRow("Last Run Time:", QLabel(self.item_data.get('last_run_time', 'N/A')))
            form_layout.addRow("Next Run Time:", QLabel(self.item_data.get('next_run_time', 'N/A')))
            form_layout.addRow("Author:", QLabel(self.item_data.get('author', 'N/A')))
            form_layout.addRow("Description:", QLabel(self.item_data.get('description', 'N/A')))
            form_layout.addRow("Actions:", QLabel(self.item_data.get('actions', 'N/A')))
            form_layout.addRow("Triggers:", QLabel(self.item_data.get('triggers', 'N/A')))
        
        layout.addLayout(form_layout)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class FilterBar(QWidget):
    """Filter bar for background items tables."""
    
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
        self.filter_text.setPlaceholderText("Enter name to filter")
        self.filter_text.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_text)
        
        self.filter_type = QComboBox()
        layout.addWidget(self.filter_type)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_filter)
        layout.addWidget(self.clear_btn)
    
    def set_filter_types(self, types):
        """Set the available filter types."""
        self.filter_type.clear()
        self.filter_type.addItems(types)
        self.filter_type.currentTextChanged.connect(self.on_filter_changed)
    
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

class ServicesTab(QWidget):
    """Tab for displaying and managing Windows services."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.services_list = []
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Filter bar
        self.filter_bar = FilterBar()
        self.filter_bar.set_filter_types(["All", "Running", "Stopped", "Automatic", "Manual", "Disabled"])
        self.filter_bar.filterChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_bar)
        
        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(5)
        self.services_table.setHorizontalHeaderLabels([
            "Name", "Display Name", "Status", "Startup Type", "Description"
        ])
        self.services_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.services_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.services_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setSortingEnabled(True)
        self.services_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.services_table.customContextMenuRequested.connect(self.show_context_menu)
        self.services_table.doubleClicked.connect(self.show_service_details)
        
        layout.addWidget(self.services_table)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.start_btn = QPushButton("Start Service")
        self.start_btn.clicked.connect(lambda: self.toggle_service("start"))
        
        self.stop_btn = QPushButton("Stop Service")
        self.stop_btn.clicked.connect(lambda: self.toggle_service("stop"))
        
        self.details_btn = QPushButton("View Details")
        self.details_btn.clicked.connect(self.show_selected_service_details)
        
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.start_btn)
        actions_layout.addWidget(self.stop_btn)
        actions_layout.addWidget(self.details_btn)
        
        layout.addLayout(actions_layout)
        
        # Status label
        self.status_label = QLabel("Loading services...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the services list."""
        try:
            self.services_list = get_services()
            
            # Clear and rebuild table
            self.services_table.setSortingEnabled(False)  # Disable sorting temporarily
            self.services_table.setRowCount(0)
            
            for i, service in enumerate(self.services_list):
                self.services_table.insertRow(i)
                
                # Name
                name_item = QTableWidgetItem(service['name'])
                name_item.setData(Qt.UserRole, service)
                self.services_table.setItem(i, 0, name_item)
                
                # Display Name
                self.services_table.setItem(i, 1, QTableWidgetItem(service['display_name']))
                
                # Status
                status_item = QTableWidgetItem(service['status'])
                if service['status'] == 'Running':
                    status_item.setForeground(Qt.darkGreen)
                elif service['status'] == 'Stopped':
                    status_item.setForeground(Qt.darkRed)
                self.services_table.setItem(i, 2, status_item)
                
                # Startup Type
                self.services_table.setItem(i, 3, QTableWidgetItem(service['start_type']))
                
                # Description
                self.services_table.setItem(i, 4, QTableWidgetItem(service.get('description', '')))
            
            # Re-enable sorting
            self.services_table.setSortingEnabled(True)
            
            # Update status
            self.status_label.setText(f"Found {len(self.services_list)} services")
            
            # Apply current filter
            self.apply_filter(
                self.filter_bar.filter_text.text(),
                self.filter_bar.filter_type.currentText()
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing services: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def apply_filter(self, text, filter_type):
        """Apply filtering to the services table."""
        for row in range(self.services_table.rowCount()):
            show_row = True
            
            # Text filter
            if text:
                name_match = text.lower() in self.services_table.item(row, 0).text().lower()
                display_name_match = text.lower() in self.services_table.item(row, 1).text().lower()
                desc_match = text.lower() in self.services_table.item(row, 4).text().lower()
                show_row = name_match or display_name_match or desc_match
            
            # Type filter
            if show_row and filter_type != "All":
                if filter_type in ["Running", "Stopped"]:
                    status = self.services_table.item(row, 2).text()
                    show_row = status == filter_type
                else:  # Startup type filters
                    startup_type = self.services_table.item(row, 3).text()
                    show_row = startup_type == filter_type
            
            self.services_table.setRowHidden(row, not show_row)
        
        # Update filtered count
        visible_count = sum(1 for row in range(self.services_table.rowCount()) 
                           if not self.services_table.isRowHidden(row))
        
        self.status_label.setText(f"Showing {visible_count} of {len(self.services_list)} services")
    
    def get_selected_service(self):
        """Get the currently selected service."""
        selected_items = self.services_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a service first.")
            return None
        
        row = selected_items[0].row()
        service_item = self.services_table.item(row, 0)
        return service_item.data(Qt.UserRole)
    
    def toggle_service(self, action):
        """Start or stop the selected service."""
        service = self.get_selected_service()
        if not service:
            return
        
        service_name = service['name']
        
        # Confirm action
        confirm_msg = f"Are you sure you want to {action} the service '{service['display_name']}'?"
        if action == "stop":
            confirm_msg += "\nStopping a critical service may impact system stability."
            
        confirm = QMessageBox.question(self, f"Confirm {action.title()} Service", 
                                       confirm_msg, QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                QApplication.setOverrideCursor(Qt.WaitCursor)
                result = toggle_service(service_name, action)
                QApplication.restoreOverrideCursor()
                
                if result:
                    QMessageBox.information(self, "Success", 
                                          f"Service '{service['display_name']}' {action}ed successfully.")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "Failed", 
                                     f"Failed to {action} service '{service['display_name']}'.\n"
                                     "You may not have sufficient privileges.")
            except Exception as e:
                QApplication.restoreOverrideCursor()
                QMessageBox.warning(self, "Error", f"Error {action}ing service: {str(e)}")
    
    def show_selected_service_details(self):
        """Show details for the selected service."""
        service = self.get_selected_service()
        if service:
            self.show_service_details(None, service)
    
    def show_service_details(self, index=None, service=None):
        """Show detailed information about a service."""
        try:
            if not service:
                item = self.services_table.item(index.row(), 0)
                service = item.data(Qt.UserRole)
            
            # Get detailed service info
            service_details = get_service_details(service['name'])
            
            dialog = BackgroundItemDetailDialog("Service", service_details, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting service details: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for service list."""
        if not self.services_table.selectedItems():
            return
        
        row = self.services_table.itemAt(position).row()
        self.services_table.selectRow(row)
        
        service = self.get_selected_service()
        if not service:
            return
        
        menu = QMenu(self)
        
        if service['status'] == 'Running':
            stop_action = QAction("Stop Service", self)
            stop_action.triggered.connect(lambda: self.toggle_service("stop"))
            menu.addAction(stop_action)
        else:
            start_action = QAction("Start Service", self)
            start_action.triggered.connect(lambda: self.toggle_service("start"))
            menu.addAction(start_action)
        
        menu.addSeparator()
        
        details_action = QAction("View Details", self)
        details_action.triggered.connect(self.show_selected_service_details)
        menu.addAction(details_action)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.services_table.mapToGlobal(position))

class StartupTab(QWidget):
    """Tab for displaying and managing Windows startup items."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.startup_list = []
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Filter bar
        self.filter_bar = FilterBar()
        self.filter_bar.set_filter_types(["All", "Enabled", "Disabled", "HKLM", "HKCU", "Startup Folder"])
        self.filter_bar.filterChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_bar)
        
        # Startup items table
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(5)
        self.startup_table.setHorizontalHeaderLabels([
            "Name", "Command", "Location", "User", "Status"
        ])
        self.startup_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.startup_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.startup_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.startup_table.setAlternatingRowColors(True)
        self.startup_table.setSortingEnabled(True)
        self.startup_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.startup_table.customContextMenuRequested.connect(self.show_context_menu)
        self.startup_table.doubleClicked.connect(self.show_startup_details)
        
        layout.addWidget(self.startup_table)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.enable_btn = QPushButton("Enable Item")
        self.enable_btn.clicked.connect(lambda: self.toggle_startup_item(True))
        
        self.disable_btn = QPushButton("Disable Item")
        self.disable_btn.clicked.connect(lambda: self.toggle_startup_item(False))
        
        self.details_btn = QPushButton("View Details")
        self.details_btn.clicked.connect(self.show_selected_startup_details)
        
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.enable_btn)
        actions_layout.addWidget(self.disable_btn)
        actions_layout.addWidget(self.details_btn)
        
        layout.addLayout(actions_layout)
        
        # Status label
        self.status_label = QLabel("Loading startup items...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the startup items list."""
        try:
            self.startup_list = get_startup_items()
            
            # Clear and rebuild table
            self.startup_table.setSortingEnabled(False)  # Disable sorting temporarily
            self.startup_table.setRowCount(0)
            
            for i, item in enumerate(self.startup_list):
                self.startup_table.insertRow(i)
                
                # Name
                name_item = QTableWidgetItem(item['name'])
                name_item.setData(Qt.UserRole, item)
                self.startup_table.setItem(i, 0, name_item)
                
                # Command
                self.startup_table.setItem(i, 1, QTableWidgetItem(item['command']))
                
                # Location
                self.startup_table.setItem(i, 2, QTableWidgetItem(item['location']))
                
                # User
                self.startup_table.setItem(i, 3, QTableWidgetItem(item['user']))
                
                # Status
                status_text = "Enabled" if item['enabled'] else "Disabled"
                status_item = QTableWidgetItem(status_text)
                if item['enabled']:
                    status_item.setForeground(Qt.darkGreen)
                else:
                    status_item.setForeground(Qt.darkRed)
                self.startup_table.setItem(i, 4, status_item)
            
            # Re-enable sorting
            self.startup_table.setSortingEnabled(True)
            
            # Update status
            self.status_label.setText(f"Found {len(self.startup_list)} startup items")
            
            # Apply current filter
            self.apply_filter(
                self.filter_bar.filter_text.text(),
                self.filter_bar.filter_type.currentText()
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing startup items: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def apply_filter(self, text, filter_type):
        """Apply filtering to the startup items table."""
        for row in range(self.startup_table.rowCount()):
            show_row = True
            
            # Text filter
            if text:
                name_match = text.lower() in self.startup_table.item(row, 0).text().lower()
                command_match = text.lower() in self.startup_table.item(row, 1).text().lower()
                show_row = name_match or command_match
            
            # Type filter
            if show_row and filter_type != "All":
                if filter_type in ["Enabled", "Disabled"]:
                    status = self.startup_table.item(row, 4).text()
                    show_row = status == filter_type
                else:  # Location filters
                    location = self.startup_table.item(row, 2).text()
                    show_row = location == filter_type or (
                        filter_type == "HKLM" and "HKEY_LOCAL_MACHINE" in location) or (
                        filter_type == "HKCU" and "HKEY_CURRENT_USER" in location)
            
            self.startup_table.setRowHidden(row, not show_row)
        
        # Update filtered count
        visible_count = sum(1 for row in range(self.startup_table.rowCount()) 
                           if not self.startup_table.isRowHidden(row))
        
        self.status_label.setText(f"Showing {visible_count} of {len(self.startup_list)} startup items")
    
    def get_selected_startup_item(self):
        """Get the currently selected startup item."""
        selected_items = self.startup_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a startup item first.")
            return None
        
        row = selected_items[0].row()
        item = self.startup_table.item(row, 0)
        return item.data(Qt.UserRole)
    
    def toggle_startup_item(self, enable):
        """Enable or disable the selected startup item."""
        item = self.get_selected_startup_item()
        if not item:
            return
        
        action = "enable" if enable else "disable"
        
        # Confirm action
        confirm = QMessageBox.question(self, f"Confirm {action.title()} Startup Item", 
                                      f"Are you sure you want to {action} the startup item '{item['name']}'?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                result = toggle_startup_item(item, enable)
                
                if result:
                    QMessageBox.information(self, "Success", 
                                          f"Startup item '{item['name']}' {action}d successfully.")
                    self.refresh()
                else:
                    QMessageBox.warning(self, "Failed", 
                                      f"Failed to {action} startup item '{item['name']}'.\n"
                                      "You may not have sufficient privileges.")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error {action}ing startup item: {str(e)}")
    
    def show_selected_startup_details(self):
        """Show details for the selected startup item."""
        item = self.get_selected_startup_item()
        if item:
            self.show_startup_details(None, item)
    
    def show_startup_details(self, index=None, item=None):
        """Show detailed information about a startup item."""
        try:
            if not item:
                table_item = self.startup_table.item(index.row(), 0)
                item = table_item.data(Qt.UserRole)
            
            # Get detailed startup item info
            item_details = get_startup_details(item)
            
            dialog = BackgroundItemDetailDialog("Startup Item", item_details, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting startup item details: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for startup items list."""
        if not self.startup_table.selectedItems():
            return
        
        row = self.startup_table.itemAt(position).row()
        self.startup_table.selectRow(row)
        
        item = self.get_selected_startup_item()
        if not item:
            return
        
        menu = QMenu(self)
        
        if item['enabled']:
            disable_action = QAction("Disable Item", self)
            disable_action.triggered.connect(lambda: self.toggle_startup_item(False))
            menu.addAction(disable_action)
        else:
            enable_action = QAction("Enable Item", self)
            enable_action.triggered.connect(lambda: self.toggle_startup_item(True))
            menu.addAction(enable_action)
        
        menu.addSeparator()
        
        details_action = QAction("View Details", self)
        details_action.triggered.connect(self.show_selected_startup_details)
        menu.addAction(details_action)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.startup_table.mapToGlobal(position))

class ScheduledTasksTab(QWidget):
    """Tab for displaying and managing Windows scheduled tasks."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks_list = []
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Filter bar
        self.filter_bar = FilterBar()
        self.filter_bar.set_filter_types(["All", "Ready", "Running", "Disabled", "System", "Microsoft", "User"])
        self.filter_bar.filterChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_bar)
        
        # Tasks table
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(5)
        self.tasks_table.setHorizontalHeaderLabels([
            "Name", "Path", "Status", "Last Run Time", "Next Run Time"
        ])
        self.tasks_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tasks_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tasks_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tasks_table.setAlternatingRowColors(True)
        self.tasks_table.setSortingEnabled(True)
        self.tasks_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tasks_table.customContextMenuRequested.connect(self.show_context_menu)
        self.tasks_table.doubleClicked.connect(self.show_task_details)
        
        layout.addWidget(self.tasks_table)
        
        # Actions bar
        actions_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.details_btn = QPushButton("View Details")
        self.details_btn.clicked.connect(self.show_selected_task_details)
        
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.details_btn)
        
        layout.addLayout(actions_layout)
        
        # Status label
        self.status_label = QLabel("Loading scheduled tasks...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the scheduled tasks list."""
        try:
            self.tasks_list = get_scheduled_tasks()
            
            # Clear and rebuild table
            self.tasks_table.setSortingEnabled(False)  # Disable sorting temporarily
            self.tasks_table.setRowCount(0)
            
            for i, task in enumerate(self.tasks_list):
                self.tasks_table.insertRow(i)
                
                # Name
                name_item = QTableWidgetItem(task['name'])
                name_item.setData(Qt.UserRole, task)
                self.tasks_table.setItem(i, 0, name_item)
                
                # Path
                self.tasks_table.setItem(i, 1, QTableWidgetItem(task['path']))
                
                # Status
                status_item = QTableWidgetItem(task['status'])
                if task['status'] == 'Ready' or task['status'] == 'Running':
                    status_item.setForeground(Qt.darkGreen)
                elif task['status'] == 'Disabled':
                    status_item.setForeground(Qt.darkRed)
                self.tasks_table.setItem(i, 2, status_item)
                
                # Last Run Time
                self.tasks_table.setItem(i, 3, QTableWidgetItem(task.get('last_run_time', 'Never')))
                
                # Next Run Time
                self.tasks_table.setItem(i, 4, QTableWidgetItem(task.get('next_run_time', 'N/A')))
            
            # Re-enable sorting
            self.tasks_table.setSortingEnabled(True)
            
            # Update status
            self.status_label.setText(f"Found {len(self.tasks_list)} scheduled tasks")
            
            # Apply current filter
            self.apply_filter(
                self.filter_bar.filter_text.text(),
                self.filter_bar.filter_type.currentText()
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing scheduled tasks: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def apply_filter(self, text, filter_type):
        """Apply filtering to the tasks table."""
        for row in range(self.tasks_table.rowCount()):
            show_row = True
            
            # Text filter
            if text:
                name_match = text.lower() in self.tasks_table.item(row, 0).text().lower()
                path_match = text.lower() in self.tasks_table.item(row, 1).text().lower()
                show_row = name_match or path_match
            
            # Type filter
            if show_row and filter_type != "All":
                if filter_type in ["Ready", "Running", "Disabled"]:
                    status = self.tasks_table.item(row, 2).text()
                    show_row = status == filter_type
                elif filter_type == "System":
                    path = self.tasks_table.item(row, 1).text()
                    show_row = path.startswith("\\Microsoft\\Windows\\") and not path.startswith("\\Microsoft\\Windows\\User")
                elif filter_type == "Microsoft":
                    path = self.tasks_table.item(row, 1).text()
                    show_row = path.startswith("\\Microsoft\\")
                elif filter_type == "User":
                    path = self.tasks_table.item(row, 1).text()
                    show_row = not (path.startswith("\\Microsoft\\") or path.startswith("\\Windows\\"))
            
            self.tasks_table.setRowHidden(row, not show_row)
        
        # Update filtered count
        visible_count = sum(1 for row in range(self.tasks_table.rowCount()) 
                           if not self.tasks_table.isRowHidden(row))
        
        self.status_label.setText(f"Showing {visible_count} of {len(self.tasks_list)} scheduled tasks")
    
    def get_selected_task(self):
        """Get the currently selected task."""
        selected_items = self.tasks_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a task first.")
            return None
        
        row = selected_items[0].row()
        task_item = self.tasks_table.item(row, 0)
        return task_item.data(Qt.UserRole)
    
    def show_selected_task_details(self):
        """Show details for the selected task."""
        task = self.get_selected_task()
        if task:
            self.show_task_details(None, task)
    
    def show_task_details(self, index=None, task=None):
        """Show detailed information about a task."""
        try:
            if not task:
                item = self.tasks_table.item(index.row(), 0)
                task = item.data(Qt.UserRole)
            
            # Get detailed task info
            task_details = get_scheduled_task_details(task['path'], task['name'])
            
            dialog = BackgroundItemDetailDialog("Scheduled Task", task_details, self)
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error getting task details: {str(e)}")
    
    def show_context_menu(self, position):
        """Show context menu for task list."""
        if not self.tasks_table.selectedItems():
            return
        
        row = self.tasks_table.itemAt(position).row()
        self.tasks_table.selectRow(row)
        
        task = self.get_selected_task()
        if not task:
            return
        
        menu = QMenu(self)
        
        details_action = QAction("View Details", self)
        details_action.triggered.connect(self.show_selected_task_details)
        menu.addAction(details_action)
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.tasks_table.mapToGlobal(position))

class BackgroundTab(QWidget):
    """Background tasks monitoring tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Create tab widget for different background item types
        self.tabs = QTabWidget()
        
        # Services tab
        self.services_tab = ServicesTab()
        self.tabs.addTab(self.services_tab, "Services")
        
        # Startup items tab
        self.startup_tab = StartupTab()
        self.tabs.addTab(self.startup_tab, "Startup Items")
        
        # Scheduled Tasks tab
        self.tasks_tab = ScheduledTasksTab()
        self.tabs.addTab(self.tasks_tab, "Scheduled Tasks")
        
        main_layout.addWidget(self.tabs)
        
        # Connect signals
        self.tabs.currentChanged.connect(self.tab_changed)
    
    def tab_changed(self, index):
        """Handle tab change event."""
        current_tab = self.tabs.widget(index)
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
    
    def refresh(self):
        """Refresh the current tab."""
        current_tab = self.tabs.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
