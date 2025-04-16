#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Achievements and Gamification tab for Windows System Manager.
Displays user achievements, points, and level progress.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QProgressBar, QFrame, QGridLayout, QGroupBox,
                            QScrollArea, QListWidget, QListWidgetItem, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor

from utils.gamification import GamificationSystem
from resources.icons import get_icon

# Explicitly define what's exported from this module
__all__ = ['AchievementsTab']

class AchievementWidget(QFrame):
    """Widget for displaying a single achievement."""
    
    def __init__(self, achievement, parent=None):
        super().__init__(parent)
        self.achievement = achievement
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        
        # Icon on left - with error handling
        icon_label = QLabel()
        try:
            icon = get_icon(self.achievement['icon'])
            # Set a fixed size pixmap as fallback
            pixmap = icon.pixmap(64, 64)
            if pixmap.isNull():
                # Create a colored rectangle as fallback
                from PyQt5.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(64, 64)
                pixmap.fill(QColor(200, 200, 200))
            icon_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error displaying icon: {str(e)}")
            # Just show a text label instead
            icon_label.setText("🏆")
            icon_label.setStyleSheet("font-size: 32px;")
        layout.addWidget(icon_label)
        
        # Achievement details
        details_layout = QVBoxLayout()
        
        # Name with locked/unlocked status
        name_layout = QHBoxLayout()
        name_label = QLabel(self.achievement['name'])
        name_label.setFont(QFont('Arial', 12, QFont.Bold))
        name_layout.addWidget(name_label)
        
        status_label = QLabel()
        if self.achievement['unlocked']:
            status_label.setText("UNLOCKED")
            status_label.setStyleSheet("color: green; font-weight: bold;")
            self.setStyleSheet("background-color: #e7f5e7;") # Light green background
        else:
            status_label.setText("LOCKED")
            status_label.setStyleSheet("color: gray;")
            self.setStyleSheet("background-color: #f0f0f0;") # Light gray background
        
        name_layout.addWidget(status_label)
        name_layout.addStretch()
        details_layout.addLayout(name_layout)
        
        # Description
        desc_label = QLabel(self.achievement['description'])
        desc_label.setWordWrap(True)
        details_layout.addWidget(desc_label)
        
        # Points
        points_label = QLabel(f"Worth: {self.achievement['points']} points")
        points_label.setStyleSheet("color: #b8860b;") # Dark golden color
        details_layout.addWidget(points_label)
        
        # For unlocked achievements, show count and date
        if self.achievement['unlocked'] and self.achievement['count'] > 0:
            if not self.achievement['one_time']:
                count_label = QLabel(f"Completed {self.achievement['count']} times")
                details_layout.addWidget(count_label)
        
        layout.addLayout(details_layout)

class LevelProgressWidget(QWidget):
    """Widget for displaying level progress."""
    
    def __init__(self, gamification, parent=None):
        super().__init__(parent)
        self.gamification = gamification
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Level information
        level_data = self.gamification.get_level()
        
        title_layout = QHBoxLayout()
        
        # Level icon - with error handling
        icon_label = QLabel()
        try:
            icon = get_icon(level_data['icon'])
            # Set a fixed size pixmap as fallback
            pixmap = icon.pixmap(48, 48)
            if pixmap.isNull():
                # Create a colored rectangle as fallback
                from PyQt5.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(48, 48)
                pixmap.fill(QColor(200, 200, 200))
            icon_label.setPixmap(pixmap)
        except Exception as e:
            print(f"Error displaying level icon: {str(e)}")
            # Just show a text label instead
            icon_label.setText("🏅")
            icon_label.setStyleSheet("font-size: 28px;")
        title_layout.addWidget(icon_label)
        
        # Level name and number
        level_label = QLabel(f"Level {level_data['level']}: {level_data['name']}")
        level_label.setFont(QFont('Arial', 14, QFont.Bold))
        title_layout.addWidget(level_label)
        title_layout.addStretch()
        
        # Points
        points = self.gamification.get_points()
        points_label = QLabel(f"{points} Points")
        points_label.setFont(QFont('Arial', 14))
        points_label.setStyleSheet("color: #b8860b;") # Dark golden color
        title_layout.addWidget(points_label)
        
        layout.addLayout(title_layout)
        
        # Progress bar for next level
        if level_data['next_level']:
            progress_layout = QVBoxLayout()
            
            progress_label = QLabel(f"Progress to {level_data['next_level']}")
            progress_layout.addWidget(progress_label)
            
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(int(level_data['progress'] * 100))
            progress_layout.addWidget(progress_bar)
            
            points_to_next = QLabel(f"{level_data['points_to_next']} points needed for next level")
            points_to_next.setAlignment(Qt.AlignRight)
            progress_layout.addWidget(points_to_next)
            
            layout.addLayout(progress_layout)
        else:
            max_level_label = QLabel("Maximum Level Reached - Congratulations!")
            max_level_label.setStyleSheet("color: green; font-weight: bold;")
            max_level_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(max_level_label)
        
        # Streak information
        streak_data = self.gamification.get_streak()
        streak_frame = QFrame()
        streak_frame.setFrameShape(QFrame.StyledPanel)
        streak_frame.setFrameShadow(QFrame.Raised)
        streak_layout = QHBoxLayout(streak_frame)
        
        streak_icon = QLabel()
        try:
            icon = get_icon('calendar')
            pixmap = icon.pixmap(32, 32)
            if pixmap.isNull():
                streak_icon.setText("📅")
                streak_icon.setStyleSheet("font-size: 24px;")
            else:
                streak_icon.setPixmap(pixmap)
        except Exception:
            streak_icon.setText("📅")
            streak_icon.setStyleSheet("font-size: 24px;")
        streak_layout.addWidget(streak_icon)
        
        streak_label = QLabel(f"Login Streak: {streak_data['days']} days")
        streak_label.setFont(QFont('Arial', 11))
        streak_layout.addWidget(streak_label)
        
        layout.addWidget(streak_frame)

class AchievementsTab(QWidget):
    """Achievements and gamification tab for Windows System Manager."""
    
    def __init__(self):
        super().__init__()
        self.gamification = GamificationSystem()
        self.init_ui()
        
        # Setup timer for periodic refresh (30 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh)
        self.refresh_timer.start(30000)  # 30 seconds
        
        # Initial data load
        self.refresh()
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        
        # Header with level information
        header_group = QGroupBox("Your Progress")
        header_group.setObjectName("Your Progress")  # Important: set object name for reference
        self.level_widget = LevelProgressWidget(self.gamification)
        header_layout = QVBoxLayout(header_group)
        header_layout.addWidget(self.level_widget)
        main_layout.addWidget(header_group)
        
        # Achievements section
        achievements_group = QGroupBox("Achievements")
        achievements_layout = QVBoxLayout(achievements_group)
        
        # Create a scroll area for achievements
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Container for achievements
        self.achievements_container = QWidget()
        self.achievements_layout = QVBoxLayout(self.achievements_container)
        scroll_area.setWidget(self.achievements_container)
        
        achievements_layout.addWidget(scroll_area)
        main_layout.addWidget(achievements_group, 1)
        
        # Refresh button at bottom
        refresh_btn = QPushButton("Refresh Achievements")
        refresh_btn.clicked.connect(self.refresh)
        main_layout.addWidget(refresh_btn)
    
    def refresh(self):
        """Refresh achievements and progress display."""
        # Only start the refresh after initialization is complete
        if not hasattr(self, 'achievements_container') or not self.achievements_container:
            return
        
        try:
            # Make sure we have necessary components
            if not hasattr(self, 'gamification') or not self.gamification:
                return
                
            # Create achievements_layout if it doesn't exist yet
            if not hasattr(self, 'achievements_layout') or not self.achievements_layout:
                self.achievements_layout = QVBoxLayout(self.achievements_container)
                self.achievements_layout.setAlignment(Qt.AlignTop)
                
            # Get all achievements data
            achievements = self.gamification.get_achievements()
                
            # Then clear the existing layout safely
            try:
                while self.achievements_layout.count():
                    child = self.achievements_layout.takeAt(0)
                    if child:
                        if child.widget():
                            child.widget().deleteLater()
                        elif child.layout():
                            # Clear sublayouts too if needed
                            while child.layout().count():
                                subchild = child.layout().takeAt(0)
                                if subchild.widget():
                                    subchild.widget().deleteLater()
            except Exception as e:
                print(f"Notice: Layout already clear - {str(e)}")
                
            # Add a title label at the top
            title_label = QLabel("Your Achievements")
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
            title_label.setAlignment(Qt.AlignCenter)
            self.achievements_layout.addWidget(title_label)
                
            # Add unlocked achievements
            unlocked = [a for a in achievements if a.get('unlocked', False)]
            locked = [a for a in achievements if not a.get('unlocked', False)]
                
            # Add counts
            counts_label = QLabel(f"Unlocked: {len(unlocked)} | Locked: {len(locked)}")
            counts_label.setAlignment(Qt.AlignCenter)
            counts_label.setStyleSheet("font-size: 12px; color: #555; margin-bottom: 10px;")
            self.achievements_layout.addWidget(counts_label)
                
            # Add a separator
            separator = QFrame()
            separator.setFrameShape(QFrame.HLine)
            separator.setFrameShadow(QFrame.Sunken)
            separator.setStyleSheet("background-color: #ccc;")
            self.achievements_layout.addWidget(separator)
                
            # Add unlocked achievements with a header
            if unlocked:
                unlocked_label = QLabel("Unlocked Achievements")
                unlocked_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                self.achievements_layout.addWidget(unlocked_label)
                
                for achievement in sorted(unlocked, key=lambda x: x.get('last_unlocked', 0), reverse=True):
                    self.achievements_layout.addWidget(AchievementWidget(achievement))
                    
            # Add locked achievements with a header    
            if locked:
                locked_label = QLabel("Locked Achievements")
                locked_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                self.achievements_layout.addWidget(locked_label)
                
                for achievement in sorted(locked, key=lambda x: x.get('points', 0), reverse=True):
                    self.achievements_layout.addWidget(AchievementWidget(achievement))
                    
            # Add a spacer at the end
            self.achievements_layout.addStretch()
            
        except Exception as e:
            print(f"Notice: Normal achievement loading - will retry: {str(e)}")
            # Don't show error messages to the user as they're not important
            # The achievements will load on next refresh cycle
        
    def notify_achievement(self, achievement):
        """
        Display a notification for a newly unlocked achievement.
        
        Args:
            achievement: The achievement that was unlocked
        """
        if not achievement:
            return
            
        from PyQt5.QtWidgets import QMessageBox
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Achievement Unlocked!")
        msg.setText(f"Achievement Unlocked: {achievement['name']}")
        msg.setInformativeText(f"{achievement['description']}\n\nYou earned {achievement['points']} points!")
        msg.setIcon(QMessageBox.Information)
        msg.exec_()
        
        # Refresh display
        self.refresh()

# Export the class explicitly at module level
if __name__ != "__main__":
    # Make the class available at the module level
    AchievementsTab = AchievementsTab