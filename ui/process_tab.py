#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Process monitoring tab for Windows System Manager.
Lists running processes with their resource usage and provides process control.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
                            QLineEdit, QComboBox, QMenu, QAction, QCheckBox,
                            QApplication)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QCursor

from utils.process_utils import (get_processes, kill_process, get_process_details, 
                               set_process_priority)
import traceback

class ProcessFilterWidget(QWidget):
    """Widget for filtering processes in the table."""
    
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
        self.filter_text.setPlaceholderText("Enter process name or PID")
        self.filter_text.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.filter_text)
        
        self.filter_type = QComboBox()
        self.filter_type.addItems(["All", "High CPU", "High Memory", "System Processes", "User Processes"])
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

class ProcessTab(QWidget):
    """Process monitoring tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.process_list = []
        self.selected_pid = None
        self.init_ui()
        
        # Setup timer for auto-refresh (3 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(3000)  # 3 seconds
        
        # Initial load
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Process filter widget
        self.filter_widget = ProcessFilterWidget()
        self.filter_widget.filterChanged.connect(self.apply_filter)
        main_layout.addWidget(self.filter_widget)
        
        # Process table
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(6)
        self.process_table.setHorizontalHeaderLabels([
            "PID", "Name", "CPU %", "Memory Usage", "Status", "Type"
        ])
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSortingEnabled(True)
        self.process_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.process_table.customContextMenuRequested.connect(self.show_context_menu)
        self.process_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        main_layout.addWidget(self.process_table)
        
        # Process details
        details_group = QGroupBox("Process Details")
        details_layout = QGridLayout(details_group)
        
        # Process info labels
        self.pid_label = QLabel("PID:")
        self.name_label = QLabel("Name:")
        self.path_label = QLabel("Path:")
        self.user_label = QLabel("User:")
        self.memory_label = QLabel("Memory:")
        self.cpu_label = QLabel("CPU:")
        self.threads_label = QLabel("Threads:")
        self.priority_label = QLabel("Priority:")
        self.started_label = QLabel("Started:")
        
        # Process info values
        self.pid_value = QLabel("Select a process")
        self.name_value = QLabel("")
        self.path_value = QLabel("")
        self.user_value = QLabel("")
        self.memory_value = QLabel("")
        self.cpu_value = QLabel("")
        self.threads_value = QLabel("")
        self.priority_value = QLabel("")
        self.started_value = QLabel("")
        
        # Add to grid
        details_layout.addWidget(self.pid_label, 0, 0)
        details_layout.addWidget(self.pid_value, 0, 1)
        details_layout.addWidget(self.name_label, 0, 2)
        details_layout.addWidget(self.name_value, 0, 3)
        details_layout.addWidget(self.path_label, 1, 0)
        details_layout.addWidget(self.path_value, 1, 1, 1, 3)
        details_layout.addWidget(self.user_label, 2, 0)
        details_layout.addWidget(self.user_value, 2, 1)
        details_layout.addWidget(self.memory_label, 2, 2)
        details_layout.addWidget(self.memory_value, 2, 3)
        details_layout.addWidget(self.cpu_label, 3, 0)
        details_layout.addWidget(self.cpu_value, 3, 1)
        details_layout.addWidget(self.threads_label, 3, 2)
        details_layout.addWidget(self.threads_value, 3, 3)
        details_layout.addWidget(self.priority_label, 4, 0)
        details_layout.addWidget(self.priority_value, 4, 1)
        details_layout.addWidget(self.started_label, 4, 2)
        details_layout.addWidget(self.started_value, 4, 3)
        
        main_layout.addWidget(details_group)
        
        # Actions Section
        actions_group = QGroupBox("Process Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.end_process_btn = QPushButton("End Process")
        self.end_process_btn.clicked.connect(self.end_selected_process)
        self.end_process_btn.setEnabled(False)
        
        self.set_priority_btn = QPushButton("Set Priority")
        self.set_priority_btn.clicked.connect(self.set_process_priority)
        self.set_priority_btn.setEnabled(False)
        
        self.refresh_btn = QPushButton("Refresh Now")
        self.refresh_btn.clicked.connect(self.refresh)
        
        self.auto_refresh_check = QCheckBox("Auto Refresh")
        self.auto_refresh_check.setChecked(True)
        self.auto_refresh_check.stateChanged.connect(self.toggle_auto_refresh)
        
        actions_layout.addWidget(self.end_process_btn)
        actions_layout.addWidget(self.set_priority_btn)
        actions_layout.addWidget(self.refresh_btn)
        actions_layout.addWidget(self.auto_refresh_check)
        
        main_layout.addWidget(actions_group)
        
        # Status label
        self.status_label = QLabel("Loading processes...")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
    
    def refresh(self):
        """Refresh the process list."""
        try:
            old_selection = None
            if self.selected_pid:
                old_selection = self.selected_pid
            
            # Get current processes
            self.process_list = get_processes()
            
            # Clear and rebuild table
            self.process_table.setSortingEnabled(False)  # Disable sorting temporarily
            self.process_table.setRowCount(0)
            
            for i, proc in enumerate(self.process_list):
                self.process_table.insertRow(i)
                
                # PID
                pid_item = QTableWidgetItem(str(proc['pid']))
                pid_item.setData(Qt.UserRole, proc['pid'])
                self.process_table.setItem(i, 0, pid_item)
                
                # Name
                self.process_table.setItem(i, 1, QTableWidgetItem(proc['name']))
                
                # CPU usage
                cpu_item = QTableWidgetItem(f"{proc['cpu_percent']:.1f}%")
                cpu_item.setData(Qt.UserRole, proc['cpu_percent'])
                # Colorize high CPU usage
                if proc['cpu_percent'] > 50:
                    cpu_item.setForeground(Qt.red)
                elif proc['cpu_percent'] > 20:
                    cpu_item.setForeground(Qt.darkYellow)
                self.process_table.setItem(i, 2, cpu_item)
                
                # Memory usage
                memory_item = QTableWidgetItem(f"{proc['memory_mb']:.1f} MB")
                memory_item.setData(Qt.UserRole, proc['memory_mb'])
                self.process_table.setItem(i, 3, memory_item)
                
                # Status
                self.process_table.setItem(i, 4, QTableWidgetItem(proc['status']))
                
                # Type (system or user)
                self.process_table.setItem(i, 5, QTableWidgetItem(proc['type']))
            
            # Re-enable sorting
            self.process_table.setSortingEnabled(True)
            
            # Update status
            self.status_label.setText(f"Found {len(self.process_list)} processes. Last updated: {QDateTime.currentDateTime().toString('hh:mm:ss')}")
            
            # Restore selection if possible
            if old_selection:
                for row in range(self.process_table.rowCount()):
                    pid_item = self.process_table.item(row, 0)
                    if pid_item and int(pid_item.text()) == old_selection:
                        self.process_table.selectRow(row)
                        break
            
            # Apply current filter
            self.apply_filter(
                self.filter_widget.filter_text.text(),
                self.filter_widget.filter_type.currentText()
            )
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing process list: {str(e)}")
            self.status_label.setText(f"Error: {str(e)}")
    
    def apply_filter(self, text, filter_type):
        """Apply filtering to the process table."""
        for row in range(self.process_table.rowCount()):
            show_row = True
            
            # Text filter
            if text:
                name_match = text.lower() in self.process_table.item(row, 1).text().lower()
                pid_match = text in self.process_table.item(row, 0).text()
                show_row = name_match or pid_match
            
            # Type filter
            if show_row and filter_type != "All":
                if filter_type == "High CPU":
                    cpu_item = self.process_table.item(row, 2)
                    cpu_value = cpu_item.data(Qt.UserRole)
                    show_row = cpu_value > 5.0  # Show processes using more than 5% CPU
                
                elif filter_type == "High Memory":
                    memory_item = self.process_table.item(row, 3)
                    memory_value = memory_item.data(Qt.UserRole)
                    show_row = memory_value > 100.0  # Show processes using more than 100MB
                
                elif filter_type == "System Processes":
                    show_row = self.process_table.item(row, 5).text() == "System"
                
                elif filter_type == "User Processes":
                    show_row = self.process_table.item(row, 5).text() == "User"
            
            self.process_table.setRowHidden(row, not show_row)
        
        # Update filtered count
        visible_count = sum(1 for row in range(self.process_table.rowCount()) 
                           if not self.process_table.isRowHidden(row))
        
        self.status_label.setText(f"Showing {visible_count} of {len(self.process_list)} processes")
    
    def on_selection_changed(self):
        """Handle process selection change."""
        selected_items = self.process_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            pid_item = self.process_table.item(row, 0)
            
            if pid_item:
                pid = int(pid_item.text())
                self.selected_pid = pid
                
                # Enable action buttons
                self.end_process_btn.setEnabled(True)
                self.set_priority_btn.setEnabled(True)
                
                # Update process details
                self.update_process_details(pid)
        else:
            self.clear_process_details()
    
    def update_process_details(self, pid):
        """Update the process details panel."""
        try:
            details = get_process_details(pid)
            
            if details:
                self.pid_value.setText(str(details['pid']))
                self.name_value.setText(details['name'])
                self.path_value.setText(details['path'])
                self.user_value.setText(details['username'])
                self.memory_value.setText(f"{details['memory_mb']:.1f} MB")
                self.cpu_value.setText(f"{details['cpu_percent']:.1f}%")
                self.threads_value.setText(str(details['num_threads']))
                self.priority_value.setText(details['priority'])
                self.started_value.setText(details['create_time'])
            else:
                self.clear_process_details()
                
        except Exception as e:
            self.pid_value.setText(f"Error: {str(e)}")
            self.clear_process_details(keep_pid=True)
    
    def clear_process_details(self, keep_pid=False):
        """Clear the process details panel."""
        if not keep_pid:
            self.pid_value.setText("Select a process")
            self.selected_pid = None
            
        self.name_value.setText("")
        self.path_value.setText("")
        self.user_value.setText("")
        self.memory_value.setText("")
        self.cpu_value.setText("")
        self.threads_value.setText("")
        self.priority_value.setText("")
        self.started_value.setText("")
        
        # Disable action buttons
        self.end_process_btn.setEnabled(False)
        self.set_priority_btn.setEnabled(False)
    
    def end_selected_process(self):
        """End the selected process."""
        if not self.selected_pid:
            return
        
        confirm = QMessageBox.question(
            self,
            "Confirm End Process",
            f"Are you sure you want to end process with PID {self.selected_pid}?\n\nThis may cause data loss if the application has unsaved work.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                result = kill_process(self.selected_pid)
                if result:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Process with PID {self.selected_pid} has been terminated."
                    )
                    self.refresh()
                else:
                    QMessageBox.warning(
                        self,
                        "Failed",
                        f"Could not terminate process with PID {self.selected_pid}.\nYou may not have sufficient privileges."
                    )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Error terminating process: {str(e)}"
                )
    
    def set_process_priority(self):
        """Set the priority of the selected process."""
        if not self.selected_pid:
            return
        
        # Create priority menu
        menu = QMenu(self)
        priorities = [
            ("Realtime", "realtime"),
            ("High", "high"),
            ("Above Normal", "above_normal"),
            ("Normal", "normal"),
            ("Below Normal", "below_normal"),
            ("Low", "idle")
        ]
        
        for name, value in priorities:
            action = QAction(name, self)
            action.setData(value)
            action.triggered.connect(lambda checked, p=value: self.change_priority(p))
            menu.addAction(action)
        
        # Show menu at button
        menu.exec_(QCursor.pos())
    
    def change_priority(self, priority):
        """Change the priority of the selected process."""
        if not self.selected_pid:
            return
        
        try:
            result = set_process_priority(self.selected_pid, priority)
            if result:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Process priority changed to {priority}."
                )
                self.update_process_details(self.selected_pid)
            else:
                QMessageBox.warning(
                    self,
                    "Failed",
                    f"Could not change process priority.\nYou may not have sufficient privileges."
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Error changing process priority: {str(e)}"
            )
    
    def show_context_menu(self, position):
        """Show context menu for process list."""
        if not self.process_table.selectedItems():
            return
        
        row = self.process_table.itemAt(position).row()
        self.process_table.selectRow(row)
        
        menu = QMenu(self)
        
        end_process_action = QAction("End Process", self)
        end_process_action.triggered.connect(self.end_selected_process)
        menu.addAction(end_process_action)
        
        priority_menu = QMenu("Set Priority", self)
        
        priorities = [
            ("Realtime", "realtime"),
            ("High", "high"),
            ("Above Normal", "above_normal"),
            ("Normal", "normal"),
            ("Below Normal", "below_normal"),
            ("Low", "idle")
        ]
        
        for name, value in priorities:
            action = QAction(name, self)
            action.setData(value)
            action.triggered.connect(lambda checked, p=value: self.change_priority(p))
            priority_menu.addAction(action)
        
        menu.addMenu(priority_menu)
        
        menu.addSeparator()
        
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)
        menu.addAction(refresh_action)
        
        menu.exec_(self.process_table.mapToGlobal(position))
    
    def toggle_auto_refresh(self, state):
        """Toggle auto-refresh on/off."""
        if state == Qt.Checked:
            self.refresh_timer.start()
        else:
            self.refresh_timer.stop()
