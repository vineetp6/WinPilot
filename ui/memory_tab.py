#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory management tab for Windows System Manager.
Displays memory usage and provides optimization tools.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from utils.memory_utils import (get_memory_info, optimize_memory, 
                               get_memory_diagnostics, get_memory_processes)

class MemoryProgressBar(QProgressBar):
    """Custom progress bar for memory display with color gradient."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(True)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setFormat("%p% used")
        self.setMinimumHeight(25)
        self.setValue(0)
        self.update_style()
    
    def setValue(self, value):
        super().setValue(value)
        self.update_style()
    
    def update_style(self):
        """Update progress bar color based on value."""
        value = self.value()
        if value < 60:
            color = "green"
        elif value < 85:
            color = "orange"
        else:
            color = "red"
        
        self.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid grey;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }}
            
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 5px;
            }}
        """)

class MemoryTab(QWidget):
    """Memory management tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
        # Setup timer for auto-refresh (5 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(5000)  # 5 seconds
        
        # Initial data load
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Memory Overview Section
        overview_group = QGroupBox("Memory Overview")
        overview_layout = QVBoxLayout(overview_group)
        
        # Memory usage bar
        usage_layout = QHBoxLayout()
        self.usage_label = QLabel("Memory Usage:")
        self.usage_label.setFont(QFont("Arial", 10, QFont.Bold))
        usage_layout.addWidget(self.usage_label)
        
        self.memory_bar = MemoryProgressBar()
        usage_layout.addWidget(self.memory_bar)
        
        overview_layout.addLayout(usage_layout)
        
        # Memory details grid
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_layout = QGridLayout(details_frame)
        
        # Labels for memory details
        self.total_label = QLabel("Total Memory:")
        self.used_label = QLabel("Used Memory:")
        self.available_label = QLabel("Available Memory:")
        self.percent_label = QLabel("Percent Used:")
        
        # Values for memory details
        self.total_value = QLabel("Loading...")
        self.used_value = QLabel("Loading...")
        self.available_value = QLabel("Loading...")
        self.percent_value = QLabel("Loading...")
        
        # Add to grid layout
        details_layout.addWidget(self.total_label, 0, 0)
        details_layout.addWidget(self.total_value, 0, 1)
        details_layout.addWidget(self.used_label, 1, 0)
        details_layout.addWidget(self.used_value, 1, 1)
        details_layout.addWidget(self.available_label, 2, 0)
        details_layout.addWidget(self.available_value, 2, 1)
        details_layout.addWidget(self.percent_label, 3, 0)
        details_layout.addWidget(self.percent_value, 3, 1)
        
        overview_layout.addWidget(details_frame)
        main_layout.addWidget(overview_group)
        
        # Memory Processes Group
        processes_group = QGroupBox("Top Memory Processes")
        processes_layout = QVBoxLayout(processes_group)
        
        # Memory processes table
        self.processes_frame = QFrame()
        self.processes_frame.setFrameShape(QFrame.StyledPanel)
        self.processes_layout = QGridLayout(self.processes_frame)
        
        # Headers
        process_header = QLabel("Process Name")
        pid_header = QLabel("PID")
        memory_header = QLabel("Memory Usage")
        
        process_header.setFont(QFont("Arial", 9, QFont.Bold))
        pid_header.setFont(QFont("Arial", 9, QFont.Bold))
        memory_header.setFont(QFont("Arial", 9, QFont.Bold))
        
        self.processes_layout.addWidget(process_header, 0, 0)
        self.processes_layout.addWidget(pid_header, 0, 1)
        self.processes_layout.addWidget(memory_header, 0, 2)
        
        # Will be populated dynamically
        processes_layout.addWidget(self.processes_frame)
        main_layout.addWidget(processes_group)
        
        # Actions Group
        actions_group = QGroupBox("Memory Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.optimize_btn = QPushButton("Optimize Memory")
        self.optimize_btn.clicked.connect(self.optimize_memory)
        
        self.diagnostics_btn = QPushButton("Run Diagnostics")
        self.diagnostics_btn.clicked.connect(self.run_diagnostics)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        
        actions_layout.addWidget(self.optimize_btn)
        actions_layout.addWidget(self.diagnostics_btn)
        actions_layout.addWidget(self.refresh_btn)
        
        main_layout.addWidget(actions_group)
        
        # Add spacer at the bottom
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
    
    def refresh(self):
        """Refresh memory information."""
        try:
            # Get memory info
            memory_info = get_memory_info()
            
            # Update progress bar
            self.memory_bar.setValue(int(memory_info['percent']))
            
            # Update memory details
            self.total_value.setText(f"{memory_info['total']} GB")
            self.used_value.setText(f"{memory_info['used']} GB")
            self.available_value.setText(f"{memory_info['available']} GB")
            self.percent_value.setText(f"{memory_info['percent']}%")
            
            # Update process list - first clear existing items
            for i in reversed(range(self.processes_layout.count())):
                item = self.processes_layout.itemAt(i)
                if item.widget() and i > 2:  # Skip the headers
                    item.widget().deleteLater()
            
            # Add new process items
            processes = get_memory_processes()
            for i, proc in enumerate(processes[:10], 1):  # Show top 10
                self.processes_layout.addWidget(QLabel(proc['name']), i, 0)
                self.processes_layout.addWidget(QLabel(str(proc['pid'])), i, 1)
                self.processes_layout.addWidget(QLabel(f"{proc['memory']} MB"), i, 2)
            
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", f"Error refreshing memory information: {str(e)}")
    
    def optimize_memory(self):
        """Run memory optimization routines."""
        try:
            result = optimize_memory()
            QMessageBox.information(
                self, 
                "Memory Optimization", 
                f"Memory optimization completed.\n\n{result['message']}\n\nRecovered: {result['recovered']} MB"
            )
            self.refresh()
        except Exception as e:
            QMessageBox.warning(self, "Optimization Error", f"Error during memory optimization: {str(e)}")
    
    def run_diagnostics(self):
        """Run memory diagnostics."""
        try:
            diagnostics = get_memory_diagnostics()
            
            # Create a formatted message
            message = "Memory Diagnostics Results:\n\n"
            message += f"• Overall Health: {diagnostics['health']}\n"
            message += f"• Page File Size: {diagnostics['page_file_size']} MB\n"
            message += f"• Page File Usage: {diagnostics['page_file_usage']}%\n"
            message += f"• Memory Fragmentation: {diagnostics['fragmentation']}%\n"
            message += f"• Cache Memory: {diagnostics['cache']} MB\n\n"
            
            if diagnostics['issues']:
                message += "Issues Detected:\n"
                for issue in diagnostics['issues']:
                    message += f"• {issue}\n"
            else:
                message += "No issues detected."
            
            QMessageBox.information(self, "Memory Diagnostics", message)
            
        except Exception as e:
            QMessageBox.warning(self, "Diagnostics Error", f"Error running memory diagnostics: {str(e)}")
