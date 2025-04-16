#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File operations tab for Windows System Manager.
Allows basic file and folder management operations.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QFileDialog, QLineEdit, QListWidget,
                            QListWidgetItem, QMenu, QAction, QInputDialog, QTreeView,
                            QHeaderView, QAbstractItemView, QSplitter, QComboBox,
                            QToolBar, QSizePolicy)
from PyQt5.QtCore import Qt, QDir, QFileInfo, QFile, QIODevice, QModelIndex, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon, QCursor, QStandardItemModel, QStandardItem

import os
import shutil
import datetime

from utils.file_utils import (create_folder, rename_item, delete_item, 
                            copy_item, move_item, get_file_info,
                            get_drives, get_item_size, format_size)

class FileSystemModel(QStandardItemModel):
    """Custom model for file system view with additional functionality."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_path = ""
        self.setHorizontalHeaderLabels(["Name", "Size", "Type", "Modified"])
    
    def setup_model(self, path):
        """Setup the model with the given path."""
        self.root_path = path
        self.clear()
        self.setHorizontalHeaderLabels(["Name", "Size", "Type", "Modified"])
        self.populate_model(path)
    
    def populate_model(self, path):
        """Populate the model with items from the path."""
        try:
            # Get all items in the directory
            dir = QDir(path)
            dir.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
            dir.setSorting(QDir.DirsFirst | QDir.Name)
            
            entries = dir.entryInfoList()
            
            folders = []
            files = []
            
            # Separate folders and files for sorting
            for entry in entries:
                if entry.isDir():
                    folders.append(entry)
                else:
                    files.append(entry)
            
            # Add folders first
            for info in folders:
                self.add_item(info)
            
            # Then add files
            for info in files:
                self.add_item(info)
            
        except Exception as e:
            print(f"Error populating model: {str(e)}")
    
    def add_item(self, file_info):
        """Add an item to the model."""
        name_item = QStandardItem(file_info.fileName())
        name_item.setData(file_info.filePath(), Qt.UserRole)
        
        if file_info.isDir():
            name_item.setIcon(QIcon.fromTheme("folder", QIcon(":/icons/folder")))
            size_item = QStandardItem("")
            type_item = QStandardItem("Folder")
        else:
            name_item.setIcon(QIcon.fromTheme("text-x-generic", QIcon(":/icons/file")))
            size = get_item_size(file_info.filePath())
            size_item = QStandardItem(format_size(size))
            size_item.setData(size, Qt.UserRole)
            type_item = QStandardItem(file_info.suffix().upper() + " File")
        
        modified_item = QStandardItem(file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss"))
        
        self.appendRow([name_item, size_item, type_item, modified_item])

class PathSelector(QWidget):
    """Widget for selecting and navigating through file paths."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Drive selector
        self.drive_combo = QComboBox()
        self.populate_drives()
        self.drive_combo.currentIndexChanged.connect(self.drive_changed)
        layout.addWidget(self.drive_combo)
        
        # Path field
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        layout.addWidget(self.path_edit)
        
        # Go up button
        self.up_btn = QPushButton("↑")
        self.up_btn.setToolTip("Go up one level")
        self.up_btn.clicked.connect(self.go_up)
        layout.addWidget(self.up_btn)
        
        # Home button
        self.home_btn = QPushButton("Home")
        self.home_btn.clicked.connect(self.go_home)
        layout.addWidget(self.home_btn)
        
        # Refresh button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setToolTip("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)
    
    def populate_drives(self):
        """Populate drive selector with available drives."""
        self.drive_combo.clear()
        
        drives = get_drives()
        for drive in drives:
            if drive['label']:
                self.drive_combo.addItem(f"{drive['letter']} ({drive['label']})", drive['letter'])
            else:
                self.drive_combo.addItem(drive['letter'], drive['letter'])
    
    def drive_changed(self, index):
        """Handle drive change event."""
        if index >= 0:
            drive = self.drive_combo.itemData(index)
            if drive:
                drive_path = drive + ":\\"
                self.path_edit.setText(drive_path)
                self.parent().navigate_to(drive_path)
    
    def go_up(self):
        """Navigate up one directory level."""
        current_path = self.path_edit.text()
        parent_path = os.path.dirname(current_path.rstrip("\\"))
        
        # Check if we're at the root of a drive
        if parent_path.endswith(":"):
            parent_path += "\\"
        
        if parent_path and parent_path != current_path:
            self.path_edit.setText(parent_path)
            self.parent().navigate_to(parent_path)
    
    def go_home(self):
        """Navigate to the user's home directory."""
        home_path = os.path.expanduser("~")
        self.path_edit.setText(home_path)
        self.parent().navigate_to(home_path)
    
    def refresh(self):
        """Refresh the current directory."""
        self.parent().refresh_view()
    
    def set_path(self, path):
        """Set the current path in the path edit."""
        self.path_edit.setText(path)
        
        # Update the drive selector if the drive has changed
        if path:
            drive_letter = path[0].upper()
            for i in range(self.drive_combo.count()):
                if self.drive_combo.itemData(i) == drive_letter:
                    self.drive_combo.setCurrentIndex(i)
                    break

class FileOperationDialog(QInputDialog):
    """Custom dialog for file operations."""
    
    def __init__(self, title, label, text="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setLabelText(label)
        self.setTextValue(text)
        self.setInputMode(QInputDialog.TextInput)
        
        # Make it a bit wider
        self.resize(400, self.height())

class FileTab(QWidget):
    """File operations tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.current_path = ""
        self.init_ui()
        
        # Navigate to the home directory initially
        self.navigate_to(os.path.expanduser("~"))
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Path navigation
        self.path_selector = PathSelector(self)
        main_layout.addWidget(self.path_selector)
        
        # File view
        self.file_model = FileSystemModel(self)
        self.file_view = QTreeView()
        self.file_view.setModel(self.file_model)
        self.file_view.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_view.customContextMenuRequested.connect(self.show_context_menu)
        self.file_view.doubleClicked.connect(self.item_double_clicked)
        
        # Set up columns
        self.file_view.header().setSectionResizeMode(0, QHeaderView.Stretch)  # Name column stretches
        self.file_view.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Size column
        self.file_view.header().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Type column
        self.file_view.header().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Modified column
        
        # Create a splitter with file view on left and file info panel on right
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.file_view)
        
        # File details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_group = QGroupBox("Item Details")
        details_form = QGridLayout(details_group)
        
        # Labels for file details
        self.name_label = QLabel("Name:")
        self.size_label = QLabel("Size:")
        self.type_label = QLabel("Type:")
        self.created_label = QLabel("Created:")
        self.modified_label = QLabel("Modified:")
        self.accessed_label = QLabel("Accessed:")
        self.attributes_label = QLabel("Attributes:")
        
        # Values for file details
        self.name_value = QLabel("Select a file or folder")
        self.size_value = QLabel("")
        self.type_value = QLabel("")
        self.created_value = QLabel("")
        self.modified_value = QLabel("")
        self.accessed_value = QLabel("")
        self.attributes_value = QLabel("")
        
        # Add to grid layout
        details_form.addWidget(self.name_label, 0, 0)
        details_form.addWidget(self.name_value, 0, 1)
        details_form.addWidget(self.type_label, 1, 0)
        details_form.addWidget(self.type_value, 1, 1)
        details_form.addWidget(self.size_label, 2, 0)
        details_form.addWidget(self.size_value, 2, 1)
        details_form.addWidget(self.created_label, 3, 0)
        details_form.addWidget(self.created_value, 3, 1)
        details_form.addWidget(self.modified_label, 4, 0)
        details_form.addWidget(self.modified_value, 4, 1)
        details_form.addWidget(self.accessed_label, 5, 0)
        details_form.addWidget(self.accessed_value, 5, 1)
        details_form.addWidget(self.attributes_label, 6, 0)
        details_form.addWidget(self.attributes_value, 6, 1)
        
        details_layout.addWidget(details_group)
        
        # Add a spacer to the details layout
        details_layout.addStretch()
        
        splitter.addWidget(details_widget)
        
        # Set the initial sizes of the splitter
        splitter.setSizes([600, 200])
        
        main_layout.addWidget(splitter)
        
        # File operations toolbar
        operations_toolbar = QToolBar()
        operations_toolbar.setIconSize(QSize(24, 24))
        
        self.new_folder_action = QAction("New Folder", self)
        self.new_folder_action.triggered.connect(self.create_new_folder)
        operations_toolbar.addAction(self.new_folder_action)
        
        operations_toolbar.addSeparator()
        
        self.copy_action = QAction("Copy", self)
        self.copy_action.triggered.connect(self.copy_selected)
        operations_toolbar.addAction(self.copy_action)
        
        self.move_action = QAction("Move", self)
        self.move_action.triggered.connect(self.move_selected)
        operations_toolbar.addAction(self.move_action)
        
        self.rename_action = QAction("Rename", self)
        self.rename_action.triggered.connect(self.rename_selected)
        operations_toolbar.addAction(self.rename_action)
        
        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self.delete_selected)
        operations_toolbar.addAction(self.delete_action)
        
        main_layout.addWidget(operations_toolbar)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(self.status_label)
    
    def navigate_to(self, path):
        """Navigate to the specified path."""
        if not os.path.exists(path):
            QMessageBox.warning(self, "Path Not Found", f"The path '{path}' does not exist.")
            return
        
        try:
            self.current_path = path
            self.file_model.setup_model(path)
            self.path_selector.set_path(path)
            
            # Update item count in status bar
            item_count = self.file_model.rowCount()
            self.status_label.setText(f"{item_count} items in {path}")
            
            # Clear file details
            self.clear_file_details()
            
        except Exception as e:
            QMessageBox.warning(self, "Navigation Error", f"Error navigating to path: {str(e)}")
    
    def refresh_view(self):
        """Refresh the current view."""
        self.navigate_to(self.current_path)
    
    def item_double_clicked(self, index):
        """Handle double-click on an item."""
        if not index.isValid():
            return
        
        # Get the file path from the model
        name_index = self.file_model.index(index.row(), 0)
        file_path = self.file_model.data(name_index, Qt.UserRole)
        
        if os.path.isdir(file_path):
            self.navigate_to(file_path)
    
    def get_selected_items(self):
        """Get the paths of all selected items."""
        selected_indexes = self.file_view.selectionModel().selectedRows()
        if not selected_indexes:
            return []
        
        selected_paths = []
        for index in selected_indexes:
            name_index = self.file_model.index(index.row(), 0)
            file_path = self.file_model.data(name_index, Qt.UserRole)
            selected_paths.append(file_path)
        
        return selected_paths
    
    def show_context_menu(self, position):
        """Show context menu for the file view."""
        selected_items = self.get_selected_items()
        if not selected_items:
            return
        
        menu = QMenu(self)
        
        # Open action (only for folders)
        if len(selected_items) == 1 and os.path.isdir(selected_items[0]):
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.navigate_to(selected_items[0]))
            menu.addAction(open_action)
            menu.addSeparator()
        
        # Common file operations
        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_selected)
        menu.addAction(copy_action)
        
        move_action = QAction("Move", self)
        move_action.triggered.connect(self.move_selected)
        menu.addAction(move_action)
        
        rename_action = QAction("Rename", self)
        rename_action.setEnabled(len(selected_items) == 1)
        rename_action.triggered.connect(self.rename_selected)
        menu.addAction(rename_action)
        
        menu.addSeparator()
        
        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Show file properties
        if len(selected_items) == 1:
            properties_action = QAction("Properties", self)
            properties_action.triggered.connect(lambda: self.show_file_details(selected_items[0]))
            menu.addAction(properties_action)
        
        menu.exec_(self.file_view.mapToGlobal(position))
    
    def create_new_folder(self):
        """Create a new folder in the current directory."""
        dialog = FileOperationDialog(
            "Create New Folder",
            "Enter folder name:",
            "New Folder",
            self
        )
        
        if dialog.exec_() == QInputDialog.Accepted:
            folder_name = dialog.textValue().strip()
            if folder_name:
                try:
                    full_path = os.path.join(self.current_path, folder_name)
                    result = create_folder(full_path)
                    
                    if result:
                        self.refresh_view()
                    else:
                        QMessageBox.warning(
                            self,
                            "Failed",
                            f"Failed to create folder '{folder_name}'."
                        )
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Error creating folder: {str(e)}"
                    )
    
    def copy_selected(self):
        """Copy selected items to a new location."""
        selected_items = self.get_selected_items()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select at least one item to copy.")
            return
        
        # Ask for destination directory
        dest_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder",
            self.current_path
        )
        
        if not dest_dir:
            return  # User cancelled
        
        try:
            for source_path in selected_items:
                result = copy_item(source_path, dest_dir)
                if not result:
                    QMessageBox.warning(
                        self,
                        "Copy Failed",
                        f"Failed to copy '{os.path.basename(source_path)}'."
                    )
            
            # If copying to the current directory, refresh view
            if dest_dir == self.current_path:
                self.refresh_view()
            
            QMessageBox.information(
                self,
                "Copy Complete",
                f"Successfully copied {len(selected_items)} item(s) to '{dest_dir}'."
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Copy Error",
                f"Error during copy operation: {str(e)}"
            )
    
    def move_selected(self):
        """Move selected items to a new location."""
        selected_items = self.get_selected_items()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select at least one item to move.")
            return
        
        # Ask for destination directory
        dest_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder",
            self.current_path
        )
        
        if not dest_dir:
            return  # User cancelled
        
        try:
            for source_path in selected_items:
                result = move_item(source_path, dest_dir)
                if not result:
                    QMessageBox.warning(
                        self,
                        "Move Failed",
                        f"Failed to move '{os.path.basename(source_path)}'."
                    )
            
            # Refresh view as items have been moved
            self.refresh_view()
            
            QMessageBox.information(
                self,
                "Move Complete",
                f"Successfully moved {len(selected_items)} item(s) to '{dest_dir}'."
            )
            
        except Exception as e:
            QMessageBox.warning(
                self,
                "Move Error",
                f"Error during move operation: {str(e)}"
            )
    
    def rename_selected(self):
        """Rename the selected item."""
        selected_items = self.get_selected_items()
        if not selected_items or len(selected_items) != 1:
            QMessageBox.information(self, "Invalid Selection", "Please select exactly one item to rename.")
            return
        
        old_path = selected_items[0]
        old_name = os.path.basename(old_path)
        
        dialog = FileOperationDialog(
            "Rename Item",
            "Enter new name:",
            old_name,
            self
        )
        
        if dialog.exec_() == QInputDialog.Accepted:
            new_name = dialog.textValue().strip()
            if new_name and new_name != old_name:
                try:
                    new_path = os.path.join(os.path.dirname(old_path), new_name)
                    result = rename_item(old_path, new_path)
                    
                    if result:
                        self.refresh_view()
                    else:
                        QMessageBox.warning(
                            self,
                            "Failed",
                            f"Failed to rename '{old_name}' to '{new_name}'."
                        )
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Error renaming item: {str(e)}"
                    )
    
    def delete_selected(self):
        """Delete the selected items."""
        selected_items = self.get_selected_items()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select at least one item to delete.")
            return
        
        # Confirm deletion
        confirm_message = f"Are you sure you want to delete the following {len(selected_items)} item(s)?\n\n"
        
        # List up to 5 items
        for i, path in enumerate(selected_items[:5]):
            confirm_message += f"• {os.path.basename(path)}\n"
        
        if len(selected_items) > 5:
            confirm_message += f"• ... and {len(selected_items) - 5} more\n"
        
        confirm_message += "\nThis action cannot be undone."
        
        confirm = QMessageBox.warning(
            self,
            "Confirm Deletion",
            confirm_message,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                for path in selected_items:
                    result = delete_item(path)
                    if not result:
                        QMessageBox.warning(
                            self,
                            "Delete Failed",
                            f"Failed to delete '{os.path.basename(path)}'."
                        )
                
                # Refresh view
                self.refresh_view()
                
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Delete Error",
                    f"Error during delete operation: {str(e)}"
                )
    
    def show_file_details(self, file_path):
        """Show details for the selected file or folder."""
        try:
            info = get_file_info(file_path)
            
            if info:
                self.name_value.setText(info['name'])
                self.type_value.setText(info['type'])
                self.size_value.setText(info['size'])
                self.created_value.setText(info['created'])
                self.modified_value.setText(info['modified'])
                self.accessed_value.setText(info['accessed'])
                self.attributes_value.setText(info['attributes'])
            else:
                self.clear_file_details()
                
        except Exception as e:
            self.clear_file_details()
            QMessageBox.warning(self, "Error", f"Error getting file details: {str(e)}")
    
    def clear_file_details(self):
        """Clear the file details panel."""
        self.name_value.setText("Select a file or folder")
        self.type_value.setText("")
        self.size_value.setText("")
        self.created_value.setText("")
        self.modified_value.setText("")
        self.accessed_value.setText("")
        self.attributes_value.setText("")
