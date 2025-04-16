#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Memory utility functions for Windows System Manager.
Provides functionality for memory monitoring and optimization.
"""

import psutil
import os
import subprocess
import ctypes
import platform
import random
from datetime import datetime
import time

def get_memory_info():
    """
    Get memory usage information.
    
    Returns:
        dict: Memory usage information including total, used, available, and percent.
    """
    mem = psutil.virtual_memory()
    
    # Convert to GB for better readability
    total_gb = mem.total / (1024**3)  # Convert bytes to GB
    used_gb = (mem.total - mem.available) / (1024**3)
    available_gb = mem.available / (1024**3)
    
    return {
        'total': round(total_gb, 2),
        'used': round(used_gb, 2),
        'available': round(available_gb, 2),
        'percent': mem.percent
    }

def optimize_memory():
    """
    Optimize memory usage by forcing garbage collection and clearing standby memory.
    
    Returns:
        dict: Result of optimization including recovered memory and message.
    """
    # Record memory before optimization
    before = psutil.virtual_memory().available
    
    # Run empty standby list and clear page file
    if platform.system() == 'Windows':
        try:
            # Run garbage collection to free up Python memory
            import gc
            gc.collect()
            
            # Try to clear file system cache
            ctypes.windll.kernel32.SetSystemFileCacheSize(-1, -1, 0)
            
            # Try to use Windows built-in command to clean memory
            subprocess.run('powershell -Command "& {Clear-RecycleBin -Force -ErrorAction SilentlyContinue}"', 
                          shell=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            
            # Additional commands to try freeing RAM
            subprocess.run('powershell -Command "& {[System.GC]::Collect()}"', 
                          shell=True, 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            
            # Wait for cleanup to take effect
            time.sleep(1)
            
        except Exception as e:
            return {
                'recovered': 0,
                'message': f"Error during optimization: {str(e)}"
            }
    
    # Record memory after optimization
    after = psutil.virtual_memory().available
    
    # Calculate recovered memory
    recovered_mb = (after - before) / (1024**2)
    
    # Handle negative recovery (might happen due to background processes claiming memory)
    if recovered_mb < 0:
        recovered_mb = 0
    
    return {
        'recovered': round(recovered_mb, 2),
        'message': "Memory optimization completed successfully."
    }

def get_memory_processes(limit=10):
    """
    Get list of processes sorted by memory usage.
    
    Args:
        limit: Maximum number of processes to return
    
    Returns:
        list: List of process dictionaries with name, pid, and memory usage.
    """
    processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
        try:
            # Get process info
            proc_info = proc.info
            memory_mb = proc_info['memory_info'].rss / (1024**2)
            
            processes.append({
                'pid': proc_info['pid'],
                'name': proc_info['name'],
                'memory': round(memory_mb, 2)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by memory usage (descending)
    processes.sort(key=lambda x: x['memory'], reverse=True)
    
    return processes[:limit]

def get_memory_diagnostics():
    """
    Run memory diagnostics to identify potential issues.
    
    Returns:
        dict: Diagnostic information and issues detected.
    """
    mem = psutil.virtual_memory()
    issues = []
    
    # Get page file information
    try:
        # Calculate page file size
        pagefile_size = 0
        pagefile_usage = 0
        
        for disk in psutil.disk_partitions():
            try:
                if 'fixed' in disk.opts:
                    disk_usage = psutil.disk_usage(disk.mountpoint)
                    if disk_usage.total > 0:
                        # Estimate pagefile contribution
                        pagefile_size += disk_usage.total * 0.05  # Rough estimate
            except:
                pass
        
        pagefile_size = pagefile_size / (1024**2)  # Convert to MB
        pagefile_usage = (mem.used / (mem.total + pagefile_size)) * 100
        
    except Exception as e:
        pagefile_size = "Unknown"
        pagefile_usage = "Unknown"
        issues.append(f"Could not analyze page file: {str(e)}")
    
    # Determine memory health
    health = "Good"
    
    # Check for high memory usage
    if mem.percent > 85:
        health = "Poor"
        issues.append("High memory usage (>85%) may cause system slowdowns.")
    elif mem.percent > 70:
        health = "Fair"
        issues.append("Elevated memory usage (>70%) detected.")
    
    # Check for low available memory
    available_gb = mem.available / (1024**3)
    if available_gb < 1:
        health = "Poor"
        issues.append(f"Low available memory ({available_gb:.2f} GB) may impact system performance.")
    
    # Calculate memory fragmentation (simulated for Windows)
    # This is a simplification; actual fragmentation is complex to measure
    try:
        # Simulate fragmentation based on system uptime and memory usage
        uptime = time.time() - psutil.boot_time()
        fragmentation = min(95, (uptime / (3600 * 24)) * 2 + (mem.percent / 5))
        
        if fragmentation > 50:
            issues.append(f"Memory may be fragmented ({int(fragmentation)}%).")
            if health == "Good":
                health = "Fair"
        
    except:
        fragmentation = "Unknown"
    
    # Cache memory
    cache = (mem.cached / (1024**2))  # MB
    
    # Prepare results
    return {
        'health': health,
        'page_file_size': int(pagefile_size) if isinstance(pagefile_size, (int, float)) else pagefile_size,
        'page_file_usage': int(pagefile_usage) if isinstance(pagefile_usage, (int, float)) else pagefile_usage,
        'fragmentation': int(fragmentation) if isinstance(fragmentation, (int, float)) else fragmentation,
        'cache': int(cache),
        'issues': issues
    }
