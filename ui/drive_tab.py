#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Drive management tab for Windows System Manager.
Allows viewing and modifying drive labels and information.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QInputDialog, QLineEdit, QDialog, QFormLayout)
from PyQt5.QtCore import Qt, QTimer, QDateTime
from PyQt5.QtGui import QFont, QIcon

from utils.drive_utils import (get_drive_info, change_drive_label, 
                              format_drive_size)

class DriveDetailDialog(QDialog):
    """Dialog for displaying detailed drive information."""
    
    def __init__(self, drive_info, parent=None):
        super().__init__(parent)
        self.drive_info = drive_info
        self.setWindowTitle(f"Drive Details - {drive_info['letter']}")
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Drive information form
        form_layout = QFormLayout()
        
        form_layout.addRow("Drive:", QLabel(f"{self.drive_info['letter']} ({self.drive_info['label']})"))
        form_layout.addRow("File System:", QLabel(self.drive_info.get('file_system', 'N/A')))
        form_layout.addRow("Total Size:", QLabel(format_drive_size(self.drive_info['total'])))
        form_layout.addRow("Used Space:", QLabel(format_drive_size(self.drive_info['used'])))
        form_layout.addRow("Free Space:", QLabel(format_drive_size(self.drive_info['free'])))
        form_layout.addRow("Usage:", QLabel(f"{self.drive_info['percent']}%"))
        form_layout.addRow("Type:", QLabel(self.drive_info.get('drive_type', 'N/A')))
        form_layout.addRow("Status:", QLabel(self.drive_info.get('status', 'Healthy')))
        form_layout.addRow("Serial Number:", QLabel(self.drive_info.get('serial', 'N/A')))
        
        layout.addLayout(form_layout)
        
        # Drive usage progress bar
        usage_label = QLabel("Usage:")
        usage_bar = QProgressBar()
        usage_bar.setValue(int(self.drive_info['percent']))
        usage_bar.setFormat("%p%")
        
        # Change color based on usage
        if self.drive_info['percent'] < 70:
            usage_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif self.drive_info['percent'] < 90:
            usage_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            usage_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        
        layout.addWidget(usage_label)
        layout.addWidget(usage_bar)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

class DriveTab(QWidget):
    """Drive management tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Setup timer for auto-refresh (10 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(10000)  # 10 seconds
        
        # Initial data load
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Drive List Section
        drives_group = QGroupBox("Drive Information")
        drives_layout = QVBoxLayout(drives_group)
        
        # Create table for drive information
        self.drives_table = QTableWidget()
        self.drives_table.setColumnCount(6)
        self.drives_table.setHorizontalHeaderLabels([
            "Drive", "Label", "Type", "Total Size", "Free Space", "Usage"
        ])
        self.drives_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.drives_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.drives_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.drives_table.setAlternatingRowColors(True)
        self.drives_table.doubleClicked.connect(self.show_drive_details)
        
        drives_layout.addWidget(self.drives_table)
        main_layout.addWidget(drives_group)
        
        # Drive Actions Section
        actions_group = QGroupBox("Drive Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.label_btn = QPushButton("Change Drive Label")
        self.label_btn.clicked.connect(self.change_drive_label)
        
        self.details_btn = QPushButton("View Drive Details")
        self.details_btn.clicked.connect(self.show_selected_drive_details)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        actions_layout.addWidget(self.label_btn)
        actions_layout.addWidget(self.details_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        main_layout.addWidget(actions_group)
        
        # Status information
        self.status_label = QLabel("Ready. Select a drive to perform actions.")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh drive information."""
        try:
            self.drives_info = get_drive_info()
            
            # Clear current table contents
            self.drives_table.setRowCount(0)
            
            # Add drives to table
            for i, drive in enumerate(self.drives_info):
                self.drives_table.insertRow(i)
                
                # Drive letter
                letter_item = QTableWidgetItem(drive['letter'])
                letter_item.setData(Qt.UserRole, drive)  # Store full drive info
                self.drives_table.setItem(i, 0, letter_item)
                
                # Label
                self.drives_table.setItem(i, 1, QTableWidgetItem(drive['label'] or "No Label"))
                
                # Type
                self.drives_table.setItem(i, 2, QTableWidgetItem(drive.get('drive_type', 'Local Disk')))
                
                # Total size
                self.drives_table.setItem(i, 3, QTableWidgetItem(format_drive_size(drive['total'])))
                
                # Free space
                self.drives_table.setItem(i, 4, QTableWidgetItem(format_drive_size(drive['free'])))
                
                # Usage - create a progress bar cell item
                usage_item = QTableWidgetItem(f"{drive['percent']}%")
                
                # Colorize based on usage
                if drive['percent'] < 70:
                    usage_item.setForeground(Qt.darkGreen)
                elif drive['percent'] < 90:
                    usage_item.setForeground(Qt.darkYellow)
                else:
                    usage_item.setForeground(Qt.darkRed)
                    
                self.drives_table.setItem(i, 5, usage_item)
            
            self.status_label.setText(f"Found {len(self.drives_info)} drives. Last updated: {QDateTime.currentDateTime().toString('hh:mm:ss')}")
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing drive information: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def get_selected_drive(self):
        """Get the currently selected drive information."""
        selected_items = self.drives_table.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a drive first.")
            return None
        
        row = selected_items[0].row()
        drive_item = self.drives_table.item(row, 0)
        return drive_item.data(Qt.UserRole)
    
    def change_drive_label(self):
        """Change the label of the selected drive."""
        drive_info = self.get_selected_drive()
        if not drive_info:
            return
        
        current_label = drive_info['label'] or ""
        
        new_label, ok = QInputDialog.getText(
            self,
            "Change Drive Label",
            f"Enter new label for drive {drive_info['letter']}:",
            QLineEdit.Normal,
            current_label
        )
        
        if ok and new_label != current_label:
            try:
                result = change_drive_label(drive_info['letter'], new_label)
                if result:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Drive {drive_info['letter']} label changed to '{new_label}'."
                    )
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"Failed to change drive label. Make sure you have administrator permissions."
                    )
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error changing drive label: {str(e)}")
    
    def show_selected_drive_details(self):
        """Show details for the selected drive."""
        drive_info = self.get_selected_drive()
        if drive_info:
            self.show_drive_details(None, drive_info)
    
    def show_drive_details(self, index=None, drive_info=None):
        """Show detailed information about a drive."""
        if not drive_info and index is not None:
            item = self.drives_table.item(index.row(), 0)
            drive_info = item.data(Qt.UserRole)
        
        if drive_info:
            dialog = DriveDetailDialog(drive_info, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No drive information available.")
