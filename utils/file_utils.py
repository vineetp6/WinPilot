#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File utility functions for Windows System Manager.
Provides functionality for file and folder operations.
"""

import os
import shutil
import stat
import time
import win32api
import win32con
import win32file
import pywintypes
from datetime import datetime

def get_drives():
    """
    Get list of available drives.
    
    Returns:
        list: List of drive dictionaries with letter and label.
    """
    drives = []
    
    # Get all physical drives
    drive_letters = win32api.GetLogicalDriveStrings().split('\x00')[:-1]
    
    for drive_letter in drive_letters:
        try:
            # Get drive type
            drive_type = win32file.GetDriveType(drive_letter)
            
            # Only process physical drives
            if drive_type in [win32file.DRIVE_FIXED, win32file.DRIVE_REMOVABLE, win32file.DRIVE_CDROM, win32file.DRIVE_REMOTE]:
                # Get volume information
                try:
                    volume_name, volume_serial, max_component_length, fs_flags, fs_name = \
                        win32api.GetVolumeInformation(drive_letter)
                except:
                    volume_name = ""
                
                # Get drive letter without trailing backslash
                letter = drive_letter.rstrip('\\')
                
                # Add to drives list
                drives.append({
                    'letter': letter[0],  # Just the letter part (e.g., 'C')
                    'label': volume_name
                })
        except Exception as e:
            print(f"Error getting info for drive {drive_letter}: {str(e)}")
    
    return drives

def get_item_size(path):
    """
    Get the size of a file or folder.
    
    Args:
        path: Path to the file or folder
        
    Returns:
        int: Size in bytes
    """
    if os.path.isfile(path):
        return os.path.getsize(path)
    
    elif os.path.isdir(path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except:
                    pass
        return total_size
    
    return 0

def format_size(size_bytes):
    """
    Format size in bytes to a human-readable format.
    
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

def get_file_info(path):
    """
    Get detailed information about a file or folder.
    
    Args:
        path: Path to the file or folder
        
    Returns:
        dict: File information including name, size, type, dates, attributes
    """
    try:
        if not os.path.exists(path):
            return None
        
        name = os.path.basename(path)
        size = get_item_size(path)
        
        # Get file type
        if os.path.isdir(path):
            type_str = "Folder"
        else:
            ext = os.path.splitext(path)[1].lower()
            if ext:
                type_str = f"{ext[1:].upper()} File"
            else:
                type_str = "File"
        
        # Get timestamps
        created = datetime.fromtimestamp(os.path.getctime(path)).strftime("%Y-%m-%d %H:%M:%S")
        modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y-%m-%d %H:%M:%S")
        accessed = datetime.fromtimestamp(os.path.getatime(path)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Get file attributes
        attr_flags = win32api.GetFileAttributes(path)
        attributes = []
        
        if attr_flags & win32con.FILE_ATTRIBUTE_READONLY:
            attributes.append("Read-only")
        if attr_flags & win32con.FILE_ATTRIBUTE_HIDDEN:
            attributes.append("Hidden")
        if attr_flags & win32con.FILE_ATTRIBUTE_SYSTEM:
            attributes.append("System")
        if attr_flags & win32con.FILE_ATTRIBUTE_ARCHIVE:
            attributes.append("Archive")
        if attr_flags & win32con.FILE_ATTRIBUTE_ENCRYPTED:
            attributes.append("Encrypted")
        if attr_flags & win32con.FILE_ATTRIBUTE_COMPRESSED:
            attributes.append("Compressed")
        
        attr_str = ", ".join(attributes) if attributes else "Normal"
        
        return {
            'name': name,
            'size': format_size(size),
            'type': type_str,
            'created': created,
            'modified': modified,
            'accessed': accessed,
            'attributes': attr_str
        }
    
    except Exception as e:
        print(f"Error getting file info for {path}: {str(e)}")
        return None

def create_folder(path):
    """
    Create a new folder.
    
    Args:
        path: Path where to create the folder
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating folder {path}: {str(e)}")
        return False

def rename_item(old_path, new_path):
    """
    Rename a file or folder.
    
    Args:
        old_path: Current path of the item
        new_path: New path for the item
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # If the destination exists, can't rename
        if os.path.exists(new_path):
            return False
        
        os.rename(old_path, new_path)
        return True
    except Exception as e:
        print(f"Error renaming {old_path} to {new_path}: {str(e)}")
        return False

def delete_item(path):
    """
    Delete a file or folder.
    
    Args:
        path: Path to the item to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            return False
        
        return True
    except Exception as e:
        print(f"Error deleting {path}: {str(e)}")
        return False

def copy_item(source, dest_dir):
    """
    Copy a file or folder to a destination directory.
    
    Args:
        source: Path to the source file or folder
        dest_dir: Destination directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the basename for creating the destination path
        base_name = os.path.basename(source)
        dest_path = os.path.join(dest_dir, base_name)
        
        # Check if destination already exists
        if os.path.exists(dest_path):
            # Create a new name with a timestamp
            name, ext = os.path.splitext(base_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{name} - Copy ({timestamp}){ext}"
            dest_path = os.path.join(dest_dir, new_name)
        
        # Copy based on type
        if os.path.isfile(source):
            shutil.copy2(source, dest_path)
        elif os.path.isdir(source):
            shutil.copytree(source, dest_path)
        else:
            return False
        
        return True
    except Exception as e:
        print(f"Error copying {source} to {dest_dir}: {str(e)}")
        return False

def move_item(source, dest_dir):
    """
    Move a file or folder to a destination directory.
    
    Args:
        source: Path to the source file or folder
        dest_dir: Destination directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the basename for creating the destination path
        base_name = os.path.basename(source)
        dest_path = os.path.join(dest_dir, base_name)
        
        # Check if destination already exists
        if os.path.exists(dest_path):
            # Create a new name with a timestamp
            name, ext = os.path.splitext(base_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{name} - Moved ({timestamp}){ext}"
            dest_path = os.path.join(dest_dir, new_name)
        
        # Move the item
        shutil.move(source, dest_path)
        return True
    except Exception as e:
        print(f"Error moving {source} to {dest_dir}: {str(e)}")
        return False
