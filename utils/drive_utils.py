#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Drive utility functions for Windows System Manager.
Provides functionality for drive management and information.
"""

import os
import psutil
import ctypes
import win32api
import win32con
import win32file
from datetime import datetime

def get_drive_info():
    """
    Get information about all connected drives.
    
    Returns:
        list: List of drive dictionaries with letter, label, total size, used space, etc.
    """
    drives = []
    
    # Get all physical drives
    drive_letters = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    
    for drive_letter in drive_letters:
        try:
            # Get drive type
            drive_type = win32file.GetDriveType(drive_letter)
            drive_type_str = "Unknown"
            
            if drive_type == win32file.DRIVE_FIXED:
                drive_type_str = "Local Disk"
            elif drive_type == win32file.DRIVE_CDROM:
                drive_type_str = "CD/DVD Drive"
            elif drive_type == win32file.DRIVE_REMOVABLE:
                drive_type_str = "Removable Drive"
            elif drive_type == win32file.DRIVE_REMOTE:
                drive_type_str = "Network Drive"
            elif drive_type == win32file.DRIVE_RAMDISK:
                drive_type_str = "RAM Disk"
            
            # Only process physical drives
            if drive_type in [win32file.DRIVE_FIXED, win32file.DRIVE_REMOVABLE, win32file.DRIVE_CDROM]:
                # Get volume information
                try:
                    volume_name, volume_serial, max_component_length, fs_flags, fs_name = \
                        win32api.GetVolumeInformation(drive_letter)
                except:
                    volume_name = ""
                    volume_serial = ""
                    fs_name = ""
                
                # Get disk usage
                try:
                    total, free = ctypes.c_ulonglong(0), ctypes.c_ulonglong(0)
                    
                    if drive_type == win32file.DRIVE_CDROM and not win32file.GetDiskFreeSpaceEx(drive_letter, None, total, free):
                        # CD/DVD might not be inserted
                        total, free = 0, 0
                    else:
                        ret = win32file.GetDiskFreeSpaceEx(drive_letter, None, total, free)
                        if not ret:
                            total, free = 0, 0
                        else:
                            total, free = total.value, free.value
                    
                    used = total - free
                    if total > 0:
                        percent = int((used / total) * 100)
                    else:
                        percent = 0
                        
                except:
                    total, used, free, percent = 0, 0, 0, 0
                
                # Get drive letter without trailing backslash
                letter = drive_letter.rstrip('\\')
                
                # Add to drives list
                drives.append({
                    'letter': letter,
                    'label': volume_name,
                    'drive_type': drive_type_str,
                    'file_system': fs_name,
                    'serial': volume_serial,
                    'total': total,
                    'used': used,
                    'free': free,
                    'percent': percent
                })
        except Exception as e:
            print(f"Error getting info for drive {drive_letter}: {str(e)}")
    
    return drives

def change_drive_label(drive_letter, new_label):
    """
    Change the label of a drive.
    
    Args:
        drive_letter: The drive letter (e.g., 'C')
        new_label: The new label for the drive
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure drive letter is just a letter without colon or slash
    drive_letter = drive_letter.rstrip(':\\')
    
    try:
        # Format drive path
        drive_path = f"{drive_letter}:\\"
        
        # Set the volume label
        win32api.SetVolumeLabel(drive_path, new_label)
        return True
    except Exception as e:
        print(f"Error changing drive label: {str(e)}")
        return False

def format_drive_size(size_bytes):
    """
    Format drive size in bytes to a human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"
