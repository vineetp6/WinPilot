#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Application utility functions for Windows System Manager.
Provides functionality for managing installed applications.
"""

import os
import sys
import winreg
import subprocess
import ctypes
import win32com.client
from datetime import datetime
import re

def get_installed_apps():
    """
    Get list of installed desktop applications from the registry.
    
    Returns:
        list: List of application dictionaries with name, version, publisher, etc.
    """
    apps = []
    
    # Registry paths containing installed application information
    registry_paths = [
        # 64-bit applications
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Uninstall"),
        # 32-bit applications on 64-bit Windows
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        # Per-user applications
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    for reg_root, reg_path in registry_paths:
        try:
            reg_key = winreg.OpenKey(reg_root, reg_path)
            
            for i in range(winreg.QueryInfoKey(reg_key)[0]):
                try:
                    # Get subkey name
                    subkey_name = winreg.EnumKey(reg_key, i)
                    subkey = winreg.OpenKey(reg_key, subkey_name)
                    
                    try:
                        # Get display name
                        display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        
                        # Skip entries without a display name
                        if not display_name.strip():
                            continue
                        
                        # Get other details
                        app_info = {
                            'name': display_name,
                            'type': 'Desktop App'
                        }
                        
                        # Version
                        try:
                            app_info['version'] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        except:
                            app_info['version'] = ""
                        
                        # Publisher
                        try:
                            app_info['publisher'] = winreg.QueryValueEx(subkey, "Publisher")[0]
                        except:
                            app_info['publisher'] = ""
                        
                        # Install date
                        try:
                            install_date = winreg.QueryValueEx(subkey, "InstallDate")[0]
                            # Try to parse date from YYYYMMDD format
                            if install_date and len(install_date) == 8:
                                year = install_date[0:4]
                                month = install_date[4:6]
                                day = install_date[6:8]
                                app_info['install_date'] = f"{year}-{month}-{day}"
                            else:
                                app_info['install_date'] = install_date
                        except:
                            app_info['install_date'] = ""
                        
                        # Installation location
                        try:
                            app_info['install_location'] = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except:
                            app_info['install_location'] = ""
                        
                        # Uninstall string
                        try:
                            app_info['uninstall_string'] = winreg.QueryValueEx(subkey, "UninstallString")[0]
                        except:
                            app_info['uninstall_string'] = ""
                        
                        # Quiet uninstall string (if available)
                        try:
                            app_info['quiet_uninstall_string'] = winreg.QueryValueEx(subkey, "QuietUninstallString")[0]
                        except:
                            app_info['quiet_uninstall_string'] = ""
                        
                        # Installation size
                        try:
                            size_bytes = winreg.QueryValueEx(subkey, "EstimatedSize")[0] * 1024  # Convert from KB to bytes
                            app_info['size'] = format_size(size_bytes)
                        except:
                            app_info['size'] = ""
                        
                        # Product code (for MSI-based installers)
                        try:
                            app_info['product_code'] = subkey_name
                        except:
                            app_info['product_code'] = ""
                        
                        # Store the registry path for uninstallation
                        app_info['registry_path'] = f"{reg_path}\\{subkey_name}"
                        app_info['registry_root'] = "HKLM" if reg_root == winreg.HKEY_LOCAL_MACHINE else "HKCU"
                        
                        # Don't add Windows Updates
                        if "KB" in app_info['name'] and "Update for Microsoft" in app_info['name']:
                            app_info['type'] = "Update"
                        
                        # Add to the list
                        apps.append(app_info)
                        
                    except (WindowsError, ValueError):
                        continue
                        
                    finally:
                        winreg.CloseKey(subkey)
                        
                except WindowsError:
                    continue
                    
            winreg.CloseKey(reg_key)
            
        except WindowsError:
            pass
    
    # Sort applications by name
    apps.sort(key=lambda x: x['name'].lower())
    return apps

def get_windows_apps():
    """
    Get list of installed Windows Store apps.
    
    Returns:
        list: List of Windows Store application dictionaries
    """
    apps = []
    
    try:
        # Use PowerShell to get Windows Store apps
        ps_command = "Get-AppxPackage | Select-Object Name, PackageFullName, Publisher, Version, InstallLocation | ConvertTo-Json"
        result = subprocess.run(["powershell", "-Command", ps_command], 
                               capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode == 0 and result.stdout.strip():
            import json
            
            # Parse JSON output
            try:
                # Handle both single item and array outputs
                output = result.stdout.strip()
                
                # Sometimes PowerShell outputs invalid JSON with BOM or other issues
                # Try to clean it up
                output = output.replace('\ufeff', '')  # Remove BOM
                output = re.sub(r'[\x00-\x1F\x7F]', '', output)  # Remove control chars
                
                if output.startswith('{'):
                    # Single item
                    app_list = [json.loads(output)]
                else:
                    # Array of items
                    app_list = json.loads(output)
                
                for app in app_list:
                    # Skip system components
                    if (app.get('Name', '').startswith('Microsoft.') or 
                        app.get('Name', '').startswith('Windows.') or
                        app.get('Publisher', '').startswith('CN=Microsoft')):
                        continue
                    
                    # Format app info
                    apps.append({
                        'name': app.get('Name', 'Unknown'),
                        'type': 'Windows Store App',
                        'version': app.get('Version', ''),
                        'publisher': app.get('Publisher', ''),
                        'install_location': app.get('InstallLocation', ''),
                        'package_full_name': app.get('PackageFullName', ''),
                        'install_date': ''  # Not available from Get-AppxPackage
                    })
            except json.JSONDecodeError:
                pass
    except Exception as e:
        print(f"Error getting Windows Store apps: {str(e)}")
    
    return apps

def get_app_details(app_data):
    """
    Get additional details about an application.
    
    Args:
        app_data: Basic application info dictionary
        
    Returns:
        dict: Enhanced application details
    """
    # Start with the existing app data
    details = app_data.copy()
    
    # Try to get more info if available
    if 'install_location' in app_data and app_data['install_location']:
        try:
            # Look for executable files in the installation directory
            exe_files = []
            for root, dirs, files in os.walk(app_data['install_location']):
                for file in files:
                    if file.lower().endswith('.exe'):
                        exe_files.append(os.path.join(root, file))
                        
                # Limit directory traversal depth to avoid long searches
                if len(exe_files) > 5:
                    break
            
            # Try to get additional info from the main executable
            if exe_files:
                try:
                    main_exe = exe_files[0]
                    
                    # Get file information
                    file_info = win32com.client.Dispatch("Scripting.FileSystemObject").GetFileVersion(main_exe)
                    if file_info and file_info != app_data.get('version', ''):
                        details['file_version'] = file_info
                except:
                    pass
        except:
            pass
    
    # Try to get description from registry
    if app_data.get('registry_root') and app_data.get('registry_path'):
        try:
            root_key = winreg.HKEY_LOCAL_MACHINE if app_data['registry_root'] == 'HKLM' else winreg.HKEY_CURRENT_USER
            reg_key = winreg.OpenKey(root_key, app_data['registry_path'])
            
            try:
                details['description'] = winreg.QueryValueEx(reg_key, "DisplayIcon")[0]
            except:
                pass
                
            try:
                details['url_info'] = winreg.QueryValueEx(reg_key, "URLInfoAbout")[0]
            except:
                pass
                
            winreg.CloseKey(reg_key)
        except:
            pass
    
    return details

def uninstall_app(app_data):
    """
    Uninstall a desktop application.
    
    Args:
        app_data: Application info dictionary
        
    Returns:
        bool: True if uninstallation was initiated, False otherwise
    """
    try:
        # Check if app has an uninstall string
        uninstall_cmd = None
        
        # Prefer quiet uninstall if available
        if app_data.get('quiet_uninstall_string'):
            uninstall_cmd = app_data['quiet_uninstall_string']
        elif app_data.get('uninstall_string'):
            uninstall_cmd = app_data['uninstall_string']
        else:
            return False
        
        # Run the uninstaller
        if uninstall_cmd:
            # Check if it's an MSI uninstaller
            if 'msiexec' in uninstall_cmd.lower():
                # Add /quiet for silent uninstallation if not already present
                if '/quiet' not in uninstall_cmd.lower() and '/q' not in uninstall_cmd.lower():
                    uninstall_cmd += ' /quiet'
            
            # Execute the uninstaller
            subprocess.Popen(uninstall_cmd, shell=True)
            return True
    except Exception as e:
        print(f"Error uninstalling application: {str(e)}")
    
    return False

def uninstall_windows_app(package_full_name):
    """
    Uninstall a Windows Store application.
    
    Args:
        package_full_name: Full package name of the app
        
    Returns:
        bool: True if uninstallation was initiated, False otherwise
    """
    try:
        if not package_full_name:
            return False
        
        # Use PowerShell to uninstall the app
        ps_command = f"Remove-AppxPackage -Package '{package_full_name}'"
        result = subprocess.run(["powershell", "-Command", ps_command], 
                               capture_output=True, text=True)
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error uninstalling Windows Store app: {str(e)}")
        return False

def install_app(exe_path, args="", silent=True):
    """
    Install an application from an executable file.
    
    Args:
        exe_path: Path to the installer executable
        args: Additional command-line arguments for the installer
        silent: Whether to attempt a silent installation
        
    Returns:
        bool: True if installation was initiated, False otherwise
    """
    try:
        if not os.path.exists(exe_path):
            return False
        
        # Construct command
        cmd = f'"{exe_path}"'
        
        # Add silent installation flags if requested
        if silent:
            # MSI installers
            if exe_path.lower().endswith('.msi'):
                cmd = f'msiexec /i "{exe_path}" /quiet'
                if args:
                    cmd += f' {args}'
            # EXE installers - attempt common silent flags if no args provided
            elif not args:
                # Try to detect installer type and use appropriate silent flags
                if 'inno' in exe_path.lower() or 'setup' in exe_path.lower():
                    cmd += ' /SILENT /SUPPRESSMSGBOXES'
                elif 'nsis' in exe_path.lower():
                    cmd += ' /S'
                elif 'wise' in exe_path.lower():
                    cmd += ' /s'
                elif 'install' in exe_path.lower():
                    cmd += ' -s'
            
        # Add custom args if provided
        if args and not exe_path.lower().endswith('.msi'):
            cmd += f' {args}'
        
        # Run the installer
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"Error installing application: {str(e)}")
        return False

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
