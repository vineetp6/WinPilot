#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Process utility functions for Windows System Manager.
Provides functionality for process monitoring and control.
"""

import psutil
import os
import sys
import win32process
import win32con
import win32api
import win32security
import pywintypes
from datetime import datetime

def get_processes():
    """
    Get list of running processes with details.
    
    Returns:
        list: List of process dictionaries with pid, name, cpu, memory usage, etc.
    """
    processes = []
    
    # Use thread with timeout to prevent UI freezing
    import threading
    
    def safe_collect():
        nonlocal processes
        try:
            # Get current Windows user SID - with error handling
            current_user_sid = None
            try:
                current_user_sid = win32security.GetTokenInformation(
                    win32security.OpenProcessToken(win32api.GetCurrentProcess(), win32con.TOKEN_QUERY),
                    win32security.TokenUser
                )[0]
            except Exception as e:
                print(f"Could not get current user SID: {str(e)}")
            
            # Iterate through processes with timeout protection
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status']):
                try:
                    # Get basic process info first
                    proc_info = proc.info
                    
                    # Skip system processes that often cause freezes
                    if proc_info['pid'] < 10:
                        continue
                    
                    # Get memory info separately to handle exceptions
                    memory_mb = 0
                    try:
                        if hasattr(proc, 'memory_info') and proc.memory_info():
                            memory_mb = proc.memory_info().rss / (1024**2)
                    except:
                        pass
                    
                    # Get CPU usage separately with minimal interval
                    cpu_percent = 0
                    try:
                        cpu_percent = proc.cpu_percent(interval=0.05)
                    except:
                        pass
                    
                    # Determine if this is a system or user process - with timeout protection
                    proc_type = "System"
                    if current_user_sid and proc_info.get('username'):
                        try:
                            proc_handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, proc_info['pid'])
                            proc_token = win32security.OpenProcessToken(proc_handle, win32con.TOKEN_QUERY)
                            proc_user_sid = win32security.GetTokenInformation(proc_token, win32security.TokenUser)[0]
                            
                            if proc_user_sid == current_user_sid:
                                proc_type = "User"
                        except:
                            pass
                    
                    # Add process to list
                    processes.append({
                        'pid': proc_info['pid'],
                        'name': proc_info.get('name', 'Unknown'),
                        'username': proc_info.get('username', 'N/A'),
                        'status': proc_info.get('status', 'Unknown'),
                        'cpu_percent': cpu_percent,
                        'memory_mb': memory_mb,
                        'type': proc_type
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                except Exception as e:
                    # Catch any other errors to prevent freezing
                    print(f"Error processing PID {proc.pid if hasattr(proc, 'pid') else 'unknown'}: {str(e)}")
                    continue
        except Exception as e:
            print(f"Error collecting processes: {str(e)}")
    
    # Run process collection in a thread with timeout
    collector_thread = threading.Thread(target=safe_collect)
    collector_thread.daemon = True
    collector_thread.start()
    collector_thread.join(timeout=3)  # 3 second timeout
    
    # Return at least a minimal set
    if not processes:
        processes = [{
            'pid': 0,
            'name': 'System Monitor',
            'username': 'System',
            'status': 'running',
            'cpu_percent': 0,
            'memory_mb': 0,
            'type': 'System'
        }]
    
    return processes

def kill_process(pid):
    """
    Terminate a process by PID.
    
    Args:
        pid: Process ID to terminate
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        process = psutil.Process(pid)
        process.terminate()
        
        # Wait for process to terminate
        gone, still_alive = psutil.wait_procs([process], timeout=3)
        
        if process in still_alive:
            # Force kill if termination didn't work
            process.kill()
        
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        print(f"Error killing process {pid}: {str(e)}")
        return False

def get_process_details(pid):
    """
    Get detailed information about a specific process with timeout protection.
    
    Args:
        pid: Process ID
        
    Returns:
        dict: Process details including path, threads, etc.
    """
    import threading
    
    result = [None]  # Use list to store result from thread
    
    def collect_details():
        try:
            process = psutil.Process(pid)
            
            # Build process details with error handling for each component
            details = {'pid': pid}
            
            # Basic process name - essential
            try:
                details['name'] = process.name()
            except:
                details['name'] = "Unknown"
            
            # Get process creation time
            try:
                create_time = datetime.fromtimestamp(process.create_time())
                details['create_time'] = create_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                details['create_time'] = "Unknown"
            
            # Get process priority
            # Windows priority constants (not part of psutil)
            priority_map = {
                win32process.IDLE_PRIORITY_CLASS: "Idle",
                win32process.BELOW_NORMAL_PRIORITY_CLASS: "Below Normal",
                win32process.NORMAL_PRIORITY_CLASS: "Normal",
                win32process.ABOVE_NORMAL_PRIORITY_CLASS: "Above Normal",
                win32process.HIGH_PRIORITY_CLASS: "High",
                win32process.REALTIME_PRIORITY_CLASS: "Realtime"
            }
            
            try:
                win_proc = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                priority = win32process.GetPriorityClass(win_proc)
                details['priority'] = priority_map.get(priority, "Unknown")
            except:
                details['priority'] = "Unknown"
            
            # Get executable path
            try:
                details['path'] = process.exe()
            except:
                details['path'] = "Access denied"
            
            # Status
            try:
                details['status'] = process.status()
            except:
                details['status'] = "Unknown"
            
            # Username
            try:
                details['username'] = process.username()
            except:
                details['username'] = "N/A"
            
            # CPU usage - with minimal interval
            try:
                details['cpu_percent'] = process.cpu_percent(interval=0.05)
            except:
                details['cpu_percent'] = 0
            
            # Memory usage
            try:
                details['memory_mb'] = process.memory_info().rss / (1024**2)
            except:
                details['memory_mb'] = 0
            
            # Thread count
            try:
                details['num_threads'] = process.num_threads()
            except:
                details['num_threads'] = 0
            
            result[0] = details
            
        except Exception as e:
            print(f"Error getting process details for {pid}: {str(e)}")
            # Return basic info even if we fail
            result[0] = {
                'pid': pid,
                'name': "Process information unavailable",
                'path': "Unknown",
                'status': "Unknown",
                'username': "N/A",
                'cpu_percent': 0,
                'memory_mb': 0,
                'num_threads': 0,
                'priority': "Unknown",
                'create_time': "Unknown"
            }
    
    # Run with timeout protection
    collector_thread = threading.Thread(target=collect_details)
    collector_thread.daemon = True
    collector_thread.start()
    collector_thread.join(timeout=2)  # 2 second timeout
    
    return result[0]

def set_process_priority(pid, priority):
    """
    Set the priority of a process.
    
    Args:
        pid: Process ID
        priority: Priority level ('idle', 'below_normal', 'normal', 'above_normal', 'high', 'realtime')
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Windows priority constants via win32process
    priority_map = {
        'idle': win32process.IDLE_PRIORITY_CLASS,
        'below_normal': win32process.BELOW_NORMAL_PRIORITY_CLASS,
        'normal': win32process.NORMAL_PRIORITY_CLASS,
        'above_normal': win32process.ABOVE_NORMAL_PRIORITY_CLASS,
        'high': win32process.HIGH_PRIORITY_CLASS,
        'realtime': win32process.REALTIME_PRIORITY_CLASS
    }
    
    if priority not in priority_map:
        return False
    
    try:
        win_proc = win32api.OpenProcess(win32con.PROCESS_SET_INFORMATION, False, pid)
        win32process.SetPriorityClass(win_proc, priority_map[priority])
        return True
    except (pywintypes.error, psutil.NoSuchProcess, psutil.AccessDenied) as e:
        print(f"Error setting process priority for {pid}: {str(e)}")
        return False
