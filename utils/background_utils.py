#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Background tasks utility functions for Windows System Manager.
Provides functionality for services, startup items, and scheduled tasks.
"""

import os
import sys
import winreg
import win32service
import win32serviceutil
import win32con
import win32security
import win32api
import win32ts
import subprocess
import pythoncom
from datetime import datetime
# Different systems might have different taskscheduler imports
# Silence the error message by redirecting stdout temporarily
import os
import sys
original_stderr = sys.stderr
try:
    # Temporarily redirect stderr to suppress error messages during import attempt
    sys.stderr = open(os.devnull, 'w')
    # Try the common import path
    from win32com.taskscheduler import taskscheduler
    # Check if it has the TaskScheduler attribute
    if not hasattr(taskscheduler, 'TaskScheduler'):
        taskscheduler = None
except (ImportError, AttributeError):
    # Fallback - some systems don't have the taskscheduler module properly available
    taskscheduler = None
finally:
    # Restore stderr
    sys.stderr = original_stderr

def get_services():
    """
    Get list of Windows services.
    
    Returns:
        list: List of service dictionaries with name, display name, status, etc.
    """
    services = []
    
    # Connect to the Service Control Manager
    sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ENUMERATE_SERVICE)
    
    # Get list of services
    try:
        # Get both win32 and device driver services
        service_type = win32service.SERVICE_WIN32 | win32service.SERVICE_DRIVER
        service_state = win32service.SERVICE_STATE_ALL
        
        # Get services list
        services_list = win32service.EnumServicesStatus(sc_handle, service_type, service_state)
        
        for service in services_list:
            # Extract basic service info
            name = service[0]
            display_name = service[1]
            status = service[2]
            
            # Map status code to string
            status_str = "Unknown"
            if status[1] == win32service.SERVICE_STOPPED:
                status_str = "Stopped"
            elif status[1] == win32service.SERVICE_START_PENDING:
                status_str = "Starting"
            elif status[1] == win32service.SERVICE_STOP_PENDING:
                status_str = "Stopping"
            elif status[1] == win32service.SERVICE_RUNNING:
                status_str = "Running"
            elif status[1] == win32service.SERVICE_CONTINUE_PENDING:
                status_str = "Continuing"
            elif status[1] == win32service.SERVICE_PAUSE_PENDING:
                status_str = "Pausing"
            elif status[1] == win32service.SERVICE_PAUSED:
                status_str = "Paused"
            
            # Get additional service configuration
            try:
                service_handle = win32service.OpenService(
                    sc_handle, name, win32service.SERVICE_QUERY_CONFIG
                )
                service_config = win32service.QueryServiceConfig(service_handle)
                
                # Map start type to string
                start_type = "Unknown"
                if service_config[1] == win32service.SERVICE_AUTO_START:
                    start_type = "Automatic"
                elif service_config[1] == win32service.SERVICE_DEMAND_START:
                    start_type = "Manual"
                elif service_config[1] == win32service.SERVICE_DISABLED:
                    start_type = "Disabled"
                elif service_config[1] == win32service.SERVICE_BOOT_START:
                    start_type = "Boot"
                elif service_config[1] == win32service.SERVICE_SYSTEM_START:
                    start_type = "System"
                
                # Get description
                try:
                    description = win32service.QueryServiceConfig2(
                        service_handle, win32service.SERVICE_CONFIG_DESCRIPTION
                    )
                    if description:
                        description = description[0] or ""
                except:
                    description = ""
                
                win32service.CloseServiceHandle(service_handle)
                
            except:
                start_type = "Unknown"
                description = ""
            
            # Add service to the list
            services.append({
                'name': name,
                'display_name': display_name,
                'status': status_str,
                'start_type': start_type,
                'description': description
            })
        
    finally:
        win32service.CloseServiceHandle(sc_handle)
    
    return services

def get_service_details(service_name):
    """
    Get detailed information about a specific service.
    
    Args:
        service_name: Name of the service
        
    Returns:
        dict: Service details
    """
    try:
        # Connect to the Service Control Manager
        sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        
        # Open the service
        service_handle = win32service.OpenService(
            sc_handle, service_name, win32service.SERVICE_QUERY_CONFIG | win32service.SERVICE_QUERY_STATUS
        )
        
        # Get service configuration
        service_config = win32service.QueryServiceConfig(service_handle)
        
        # Map start type to string
        start_type = "Unknown"
        if service_config[1] == win32service.SERVICE_AUTO_START:
            start_type = "Automatic"
        elif service_config[1] == win32service.SERVICE_DEMAND_START:
            start_type = "Manual"
        elif service_config[1] == win32service.SERVICE_DISABLED:
            start_type = "Disabled"
        elif service_config[1] == win32service.SERVICE_BOOT_START:
            start_type = "Boot"
        elif service_config[1] == win32service.SERVICE_SYSTEM_START:
            start_type = "System"
        
        # Get description
        try:
            description = win32service.QueryServiceConfig2(
                service_handle, win32service.SERVICE_CONFIG_DESCRIPTION
            )
            if description:
                description = description[0] or ""
        except:
            description = ""
        
        # Get service status
        status = win32service.QueryServiceStatus(service_handle)
        
        # Map status code to string
        status_str = "Unknown"
        if status[1] == win32service.SERVICE_STOPPED:
            status_str = "Stopped"
        elif status[1] == win32service.SERVICE_START_PENDING:
            status_str = "Starting"
        elif status[1] == win32service.SERVICE_STOP_PENDING:
            status_str = "Stopping"
        elif status[1] == win32service.SERVICE_RUNNING:
            status_str = "Running"
        elif status[1] == win32service.SERVICE_CONTINUE_PENDING:
            status_str = "Continuing"
        elif status[1] == win32service.SERVICE_PAUSE_PENDING:
            status_str = "Pausing"
        elif status[1] == win32service.SERVICE_PAUSED:
            status_str = "Paused"
        
        # Get service display name
        display_name = win32serviceutil.GetServiceDisplayName(None, service_name)
        
        # Additional details
        binary_path = service_config[3]
        username = service_config[7]
        
        # Get PID if running
        pid = 0
        if status[1] == win32service.SERVICE_RUNNING:
            try:
                # This is a hacky way to get the PID since direct methods 
                # might require higher privileges
                for proc in subprocess.check_output(['tasklist', '/svc', '/fo', 'csv']).decode().splitlines()[1:]:
                    parts = proc.strip('"').split('","')
                    if len(parts) >= 3 and service_name in parts[2]:
                        pid = int(parts[1])
                        break
            except:
                pid = 0
        
        # Pack service details
        details = {
            'name': service_name,
            'display_name': display_name,
            'description': description,
            'status': status_str,
            'start_type': start_type,
            'binary_path': binary_path,
            'username': username,
            'pid': pid
        }
        
        win32service.CloseServiceHandle(service_handle)
        win32service.CloseServiceHandle(sc_handle)
        
        return details
    
    except Exception as e:
        print(f"Error getting service details for {service_name}: {str(e)}")
        return {
            'name': service_name,
            'display_name': service_name,
            'description': "Error getting service details",
            'status': "Unknown",
            'start_type': "Unknown",
            'binary_path': "",
            'username': "",
            'pid': 0
        }

def toggle_service(service_name, action):
    """
    Start or stop a service.
    
    Args:
        service_name: Name of the service
        action: Either 'start' or 'stop'
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if action == 'start':
            win32serviceutil.StartService(service_name)
        elif action == 'stop':
            win32serviceutil.StopService(service_name)
        else:
            return False
        
        return True
    except Exception as e:
        print(f"Error {action}ing service {service_name}: {str(e)}")
        return False

def get_startup_items():
    """
    Get list of startup programs.
    
    Returns:
        list: List of startup item dictionaries
    """
    startup_items = []
    
    # Get startup items from registry
    # HKLM\Software\Microsoft\Windows\CurrentVersion\Run
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
        
        i = 0
        while True:
            try:
                name, value, type = winreg.EnumValue(reg_key, i)
                startup_items.append({
                    'name': name,
                    'command': value,
                    'location': "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    'user': "All Users",
                    'enabled': True
                })
                i += 1
            except WindowsError:
                break
    except:
        pass
    
    # HKCU\Software\Microsoft\Windows\CurrentVersion\Run
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
        
        i = 0
        while True:
            try:
                name, value, type = winreg.EnumValue(reg_key, i)
                startup_items.append({
                    'name': name,
                    'command': value,
                    'location': "HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                    'user': "Current User",
                    'enabled': True
                })
                i += 1
            except WindowsError:
                break
    except:
        pass
    
    # Get startup items from Startup folder
    all_users_startup = os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    current_user_startup = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    
    # All users startup folder
    if os.path.exists(all_users_startup):
        for item in os.listdir(all_users_startup):
            if item.endswith(".lnk") or item.endswith(".url"):
                startup_items.append({
                    'name': os.path.splitext(item)[0],
                    'command': os.path.join(all_users_startup, item),
                    'location': "Startup Folder",
                    'user': "All Users",
                    'enabled': True
                })
    
    # Current user startup folder
    if os.path.exists(current_user_startup):
        for item in os.listdir(current_user_startup):
            if item.endswith(".lnk") or item.endswith(".url"):
                startup_items.append({
                    'name': os.path.splitext(item)[0],
                    'command': os.path.join(current_user_startup, item),
                    'location': "Startup Folder",
                    'user': "Current User",
                    'enabled': True
                })
    
    # Get disabled startup items
    # HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run")
        
        i = 0
        while True:
            try:
                name, value, type = winreg.EnumValue(reg_key, i)
                # Check if this item is in our list
                for item in startup_items:
                    if item['name'].lower() == name.lower() and item['location'].startswith("HKEY_LOCAL_MACHINE"):
                        # Check the first byte of the value to determine if enabled or disabled
                        # 02 00 00 00... = enabled, 03 00 00 00... = disabled
                        item['enabled'] = value[0] != 3
                i += 1
            except WindowsError:
                break
    except:
        pass
    
    # HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run")
        
        i = 0
        while True:
            try:
                name, value, type = winreg.EnumValue(reg_key, i)
                # Check if this item is in our list
                for item in startup_items:
                    if item['name'].lower() == name.lower() and item['location'].startswith("HKEY_CURRENT_USER"):
                        # Check the first byte of the value to determine if enabled or disabled
                        item['enabled'] = value[0] != 3
                i += 1
            except WindowsError:
                break
    except:
        pass
    
    return startup_items

def get_startup_details(item):
    """
    Get detailed information about a startup item.
    
    Args:
        item: Startup item dictionary
        
    Returns:
        dict: Enhanced startup item details
    """
    # Clone the original item
    details = item.copy()
    
    # Try to get manufacturer info
    if 'command' in item:
        try:
            # Extract the executable part from the command line
            cmd = item['command'].strip('"')
            if " " in cmd:
                cmd = cmd.split(" ")[0]
            
            # Get file information
            if os.path.exists(cmd):
                try:
                    # Get file version info
                    info = win32api.GetFileVersionInfo(cmd, "\\")
                    ms = info['FileVersionMS']
                    ls = info['FileVersionLS']
                    version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
                    
                    # Get company name
                    lang, codepage = win32api.GetFileVersionInfo(cmd, '\\VarFileInfo\\Translation')[0]
                    company_name = win32api.GetFileVersionInfo(
                        cmd, f'\\StringFileInfo\\{lang:04x}{codepage:04x}\\CompanyName')
                    
                    details['version'] = version
                    details['manufacturer'] = company_name
                except:
                    details['version'] = "Unknown"
                    details['manufacturer'] = "Unknown"
            else:
                details['version'] = "Unknown"
                details['manufacturer'] = "Unknown"
        except:
            details['version'] = "Unknown"
            details['manufacturer'] = "Unknown"
    
    return details

def toggle_startup_item(item, enable):
    """
    Enable or disable a startup item.
    
    Args:
        item: Startup item dictionary
        enable: True to enable, False to disable
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Handle registry items
        if item['location'].startswith("HKEY_LOCAL_MACHINE"):
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
            root_key = winreg.HKEY_LOCAL_MACHINE
        elif item['location'].startswith("HKEY_CURRENT_USER"):
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run"
            root_key = winreg.HKEY_CURRENT_USER
        else:
            # Startup folder items can't be disabled, only removed
            return False
        
        # Open the key for writing
        reg_key = winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE)
        
        # The value is 12 bytes. First byte is the state:
        # 02 00 00 00... = enabled, 03 00 00 00... = disabled
        value = bytearray(12)
        value[0] = 2 if enable else 3
        
        # Write the value
        winreg.SetValueEx(reg_key, item['name'], 0, winreg.REG_BINARY, bytes(value))
        winreg.CloseKey(reg_key)
        
        return True
    except Exception as e:
        print(f"Error setting startup item state: {str(e)}")
        return False

def get_scheduled_tasks():
    """
    Get list of scheduled tasks.
    
    Returns:
        list: List of scheduled task dictionaries
    """
    tasks = []
    
    # Check if taskscheduler module is available
    if taskscheduler is None:
        # Return a placeholder message when the module is not available
        tasks.append({
            'name': 'Task Scheduler Not Available',
            'path': '/',
            'status': 'Error',
            'next_run': 'N/A',
            'last_run': 'N/A',
            'author': 'N/A',
            'description': 'The Task Scheduler module is not available on this system. Install the correct version of pywin32.'
        })
        return tasks
    
    try:
        pythoncom.CoInitialize()
        scheduler = taskscheduler.TaskScheduler()
        
        # Helper function to recursively get tasks
        def get_tasks_from_folder(folder_path):
            folder_tasks = []
            try:
                # Get all tasks in the folder
                folder = scheduler.GetFolder(folder_path)
                tasks_collection = folder.GetTasks(0)
                
                for task in tasks_collection:
                    try:
                        name = task.Name
                        
                        # Get task state
                        state = task.State
                        status = "Unknown"
                        
                        if state == 1:
                            status = "Disabled"
                        elif state == 2:
                            status = "Queued"
                        elif state == 3:
                            status = "Ready"
                        elif state == 4:
                            status = "Running"
                        
                        # Get last run time
                        try:
                            last_run_time = task.LastRunTime.Format("%Y-%m-%d %H:%M:%S")
                            if last_run_time == "0001-01-01 00:00:00":
                                last_run_time = "Never"
                        except:
                            last_run_time = "Never"
                        
                        # Get next run time
                        try:
                            next_run_time = task.NextRunTime.Format("%Y-%m-%d %H:%M:%S")
                            if next_run_time == "0001-01-01 00:00:00":
                                next_run_time = "N/A"
                        except:
                            next_run_time = "N/A"
                        
                        folder_tasks.append({
                            'name': name,
                            'path': folder_path,
                            'status': status,
                            'last_run_time': last_run_time,
                            'next_run_time': next_run_time
                        })
                    except:
                        continue
                
                # Get subfolders
                folders = folder.GetFolders(0)
                for subfolder in folders:
                    subfolder_path = f"{folder_path}\\{subfolder.Name}"
                    folder_tasks.extend(get_tasks_from_folder(subfolder_path))
                
            except Exception as e:
                print(f"Error getting tasks from folder {folder_path}: {str(e)}")
            
            return folder_tasks
        
        # Get all tasks starting from root
        tasks = get_tasks_from_folder("\\")
        
    except Exception as e:
        error_message = str(e)
        
        # Create a more user-friendly error message
        if "has no attribute 'TaskScheduler'" in error_message:
            print("Task Scheduler API not properly installed. This is a common issue with some pywin32 installations.")
            tasks.append({
                'name': 'Windows Task Scheduler',
                'path': '/',
                'status': 'Not Available',
                'next_run': 'N/A',
                'last_run': 'N/A',
                'description': 'The Task Scheduler API is not properly installed. This is a common issue with some pywin32 installations.'
            })
        else:
            print(f"Note: Windows Task Scheduler not available: {error_message}")
            tasks.append({
                'name': 'Windows Task Scheduler',
                'path': '/',
                'status': 'Not Available',
                'next_run': 'N/A',
                'last_run': 'N/A',
                'description': 'Unable to connect to the Windows Task Scheduler service. This feature requires administrator privileges.'
            })
    
    finally:
        try:
            pythoncom.CoUninitialize()
        except:
            pass  # Ignore errors on uninitialize
    
    return tasks

def get_scheduled_task_details(path, name):
    """
    Get detailed information about a scheduled task.
    
    Args:
        path: Path to the task folder
        name: Name of the task
        
    Returns:
        dict: Task details
    """
    # Check if taskscheduler module is available
    if taskscheduler is None:
        return {
            'name': name,
            'path': path,
            'description': "Windows Task Scheduler API not available. Install correct version of pywin32.",
            'author': "N/A",
            'status': "Not Available",
            'last_run_time': "N/A",
            'next_run_time': "N/A",
            'actions': "N/A",
            'triggers': "N/A",
            'run_as': "N/A",
            'enabled': False
        }
        
    try:
        pythoncom.CoInitialize()
        scheduler = taskscheduler.TaskScheduler()
        
        # Get the task
        folder = scheduler.GetFolder(path)
        task = folder.GetTask(name)
        
        # Get task definition
        definition = task.Definition
        
        # Get actions
        actions = []
        for i in range(definition.Actions.Count):
            action = definition.Actions.Item(i+1)
            if action.Type == 0:  # TASK_ACTION_EXEC
                actions.append(f"Execute: {action.Path} {action.Arguments}")
            elif action.Type == 5:  # TASK_ACTION_COM_HANDLER
                actions.append(f"COM Handler: {action.ClassId}")
            elif action.Type == 6:  # TASK_ACTION_SEND_EMAIL
                actions.append(f"Send Email to: {action.To}")
            elif action.Type == 7:  # TASK_ACTION_SHOW_MESSAGE
                actions.append(f"Show Message: {action.Title}")
        
        # Get triggers
        triggers = []
        for i in range(definition.Triggers.Count):
            trigger = definition.Triggers.Item(i+1)
            trigger_info = f"Type: {trigger.Type}"
            
            # Add start boundary
            if hasattr(trigger, 'StartBoundary') and trigger.StartBoundary:
                start = trigger.StartBoundary.replace('T', ' ').split('.')[0]
                trigger_info += f", Start: {start}"
            
            triggers.append(trigger_info)
        
        # Get principal (who the task runs as)
        principal = definition.Principal
        
        # Get registration info
        reg_info = definition.RegistrationInfo
        
        # Create detailed info
        details = {
            'name': name,
            'path': path,
            'description': reg_info.Description if reg_info.Description else "No description",
            'author': reg_info.Author if reg_info.Author else "Unknown",
            'status': "Disabled" if task.State == 1 else "Ready" if task.State == 3 else "Running" if task.State == 4 else "Unknown",
            'last_run_time': task.LastRunTime.Format("%Y-%m-%d %H:%M:%S") if task.LastRunTime.Year > 1601 else "Never",
            'next_run_time': task.NextRunTime.Format("%Y-%m-%d %H:%M:%S") if task.NextRunTime.Year > 1601 else "N/A",
            'actions': ", ".join(actions) if actions else "None",
            'triggers': ", ".join(triggers) if triggers else "None",
            'run_as': principal.UserId if principal.UserId else "SYSTEM",
            'enabled': task.Enabled
        }
        
        pythoncom.CoUninitialize()
        return details
    
    except Exception as e:
        pythoncom.CoUninitialize()
        print(f"Error getting task details for {path}\\{name}: {str(e)}")
        return {
            'name': name,
            'path': path,
            'description': "Error getting task details",
            'author': "Unknown",
            'status': "Unknown",
            'last_run_time': "Unknown",
            'next_run_time': "Unknown",
            'actions': "Unknown",
            'triggers': "Unknown",
            'run_as': "Unknown",
            'enabled': False
        }
