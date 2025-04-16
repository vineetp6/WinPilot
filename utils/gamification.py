#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Gamification utilities for Windows System Manager.
Provides achievements, points, and rewards for system maintenance tasks.
"""

import os
import json
import time
from datetime import datetime

# Define achievements
ACHIEVEMENTS = {
    'system_optimizer': {
        'id': 'system_optimizer',
        'name': 'System Optimizer',
        'description': 'Optimize system memory for the first time',
        'icon': 'trophy',
        'points': 50,
        'one_time': True
    },
    'disk_cleanup': {
        'id': 'disk_cleanup',
        'name': 'Disk Cleanup Master',
        'description': 'Free up disk space by cleaning temporary files',
        'icon': 'disk',
        'points': 75,
        'one_time': False
    },
    'process_manager': {
        'id': 'process_manager',
        'name': 'Process Manager',
        'description': 'End a non-responding process',
        'icon': 'process',
        'points': 30,
        'one_time': False
    },
    'drive_organizer': {
        'id': 'drive_organizer',
        'name': 'Drive Organizer',
        'description': 'Change a drive label for better organization',
        'icon': 'drive',
        'points': 25,
        'one_time': True
    },
    'file_custodian': {
        'id': 'file_custodian',
        'name': 'File Custodian',
        'description': 'Organize files into folders',
        'icon': 'folder',
        'points': 40,
        'one_time': False
    },
    'app_manager': {
        'id': 'app_manager',
        'name': 'Application Manager',
        'description': 'Uninstall unused applications to save space',
        'icon': 'app',
        'points': 60,
        'one_time': False
    },
    'maintenance_streak': {
        'id': 'maintenance_streak',
        'name': 'Maintenance Streak',
        'description': 'Use Windows System Manager for 5 consecutive days',
        'icon': 'calendar',
        'points': 100,
        'one_time': True
    },
    'startup_cleaner': {
        'id': 'startup_cleaner',
        'name': 'Startup Optimized',
        'description': 'Disable unnecessary startup items',
        'icon': 'startup',
        'points': 45,
        'one_time': False
    },
    'memory_guardian': {
        'id': 'memory_guardian',
        'name': 'Memory Guardian',
        'description': 'Keep memory usage below 70% for a session',
        'icon': 'memory',
        'points': 55,
        'one_time': False
    }
}

# Define levels
LEVELS = {
    1: {'min_points': 0, 'name': 'Novice', 'icon': 'level1'},
    2: {'min_points': 200, 'name': 'Apprentice', 'icon': 'level2'},
    3: {'min_points': 500, 'name': 'Proficient', 'icon': 'level3'},
    4: {'min_points': 1000, 'name': 'Expert', 'icon': 'level4'},
    5: {'min_points': 2000, 'name': 'Master', 'icon': 'level5'}
}

class GamificationSystem:
    """Gamification system for Windows System Manager."""
    
    def __init__(self, data_dir=None):
        # Default to user's appdata directory 
        if data_dir is None:
            # This would use %APPDATA% on Windows
            data_dir = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'WindowsSystemManager')
        
        self.data_dir = data_dir
        self.data_file = os.path.join(data_dir, 'gamification_data.json')
        
        # Create directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Load or initialize user data
        self.user_data = self._load_user_data()
        
        # Check for streak
        self._check_streak()
    
    def _load_user_data(self):
        """Load user data from file or create default if doesn't exist."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # File is corrupted or can't be read, create new data
                pass
        
        # Create default user data
        return {
            'points': 0,
            'achievements': {},
            'last_login': None,
            'streak_days': 0,
            'streak_last_date': None
        }
    
    def _save_user_data(self):
        """Save user data to file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.user_data, f, indent=2)
            return True
        except IOError:
            return False
    
    def _check_streak(self):
        """Check and update login streak."""
        today = datetime.now().strftime('%Y-%m-%d')
        last_login = self.user_data.get('streak_last_date')
        
        # First time login
        if last_login is None:
            self.user_data['streak_days'] = 1
            self.user_data['streak_last_date'] = today
            self._save_user_data()
            return
        
        # Already logged in today
        if last_login == today:
            return
        
        # Calculate days between logins
        last_date = datetime.strptime(last_login, '%Y-%m-%d')
        today_date = datetime.strptime(today, '%Y-%m-%d')
        days_diff = (today_date - last_date).days
        
        # Consecutive day
        if days_diff == 1:
            self.user_data['streak_days'] += 1
            
            # Check for streak achievement
            if self.user_data['streak_days'] >= 5:
                self.unlock_achievement('maintenance_streak')
        # Streak broken
        elif days_diff > 1:
            self.user_data['streak_days'] = 1
        
        self.user_data['streak_last_date'] = today
        self._save_user_data()
    
    def unlock_achievement(self, achievement_id):
        """
        Unlock an achievement and award points.
        
        Args:
            achievement_id: ID of the achievement to unlock
            
        Returns:
            dict: Achievement data if newly unlocked, None if already unlocked or invalid
        """
        # Check if achievement exists
        if achievement_id not in ACHIEVEMENTS:
            return None
        
        achievement = ACHIEVEMENTS[achievement_id]
        
        # Check if one-time achievement is already unlocked
        if achievement['one_time'] and achievement_id in self.user_data['achievements']:
            return None
        
        # Get current timestamp
        timestamp = time.time()
        
        # Add or update achievement
        if achievement_id not in self.user_data['achievements']:
            self.user_data['achievements'][achievement_id] = {
                'first_unlocked': timestamp,
                'last_unlocked': timestamp,
                'count': 1
            }
        else:
            self.user_data['achievements'][achievement_id]['last_unlocked'] = timestamp
            self.user_data['achievements'][achievement_id]['count'] += 1
        
        # Add points
        self.user_data['points'] += achievement['points']
        
        # Save data
        self._save_user_data()
        
        # Return achievement data for notification
        return achievement
    
    def get_level(self):
        """
        Get current user level based on points.
        
        Returns:
            dict: Level data including name, icon, and level number
        """
        points = self.user_data['points']
        current_level = 1
        
        for level, data in sorted(LEVELS.items()):
            if points >= data['min_points']:
                current_level = level
            else:
                break
        
        level_data = LEVELS[current_level].copy()
        level_data['level'] = current_level
        
        # Calculate progress to next level
        if current_level < max(LEVELS.keys()):
            next_level = current_level + 1
            min_points = LEVELS[current_level]['min_points']
            next_points = LEVELS[next_level]['min_points']
            level_data['progress'] = (points - min_points) / (next_points - min_points)
            level_data['next_level'] = LEVELS[next_level]['name']
            level_data['points_to_next'] = next_points - points
        else:
            level_data['progress'] = 1.0
            level_data['next_level'] = None
            level_data['points_to_next'] = 0
        
        return level_data
    
    def get_points(self):
        """Get current user points."""
        return self.user_data['points']
    
    def get_achievements(self):
        """
        Get all achievements with unlock status.
        
        Returns:
            list: List of achievement dictionaries with unlock status
        """
        result = []
        
        for ach_id, ach_data in ACHIEVEMENTS.items():
            achievement = ach_data.copy()
            if ach_id in self.user_data['achievements']:
                achievement['unlocked'] = True
                achievement['count'] = self.user_data['achievements'][ach_id]['count']
                achievement['last_unlocked'] = self.user_data['achievements'][ach_id]['last_unlocked']
            else:
                achievement['unlocked'] = False
                achievement['count'] = 0
            
            result.append(achievement)
        
        return result
    
    def get_streak(self):
        """
        Get current login streak information.
        
        Returns:
            dict: Streak information
        """
        return {
            'days': self.user_data['streak_days'],
            'last_date': self.user_data['streak_last_date']
        }
    
    def record_action(self, action):
        """
        Record a user action and check for achievements.
        
        Args:
            action: Action identifier string
            
        Returns:
            dict: Achievement data if unlocked, None otherwise
        """
        # Map actions to achievements
        action_achievements = {
            'memory_optimize': 'system_optimizer',
            'disk_cleanup': 'disk_cleanup',
            'end_process': 'process_manager',
            'change_drive_label': 'drive_organizer',
            'organize_files': 'file_custodian',
            'uninstall_app': 'app_manager',
            'disable_startup': 'startup_cleaner',
            'memory_usage_low': 'memory_guardian'
        }
        
        # Check if action maps to an achievement
        if action in action_achievements:
            return self.unlock_achievement(action_achievements[action])
        
        return None