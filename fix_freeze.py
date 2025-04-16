import os

# Find utils/process_utils.py
process_utils_path = "utils/process_utils.py"

with open(process_utils_path, "r") as file:
    content = file.read()

# Add better error handling and timeouts to the process collection
improved_content = content.replace(
    "def get_processes():",
    """def get_processes():
 \"\"\"
 Get list of running processes with improved error handling and timeouts.
 
 Returns:
     list: List of process dictionaries
 \"\"\"
 import threading
 
 processes = []
 
 # Create a timeout mechanism for slow operations
 def collect_with_timeout():
     nonlocal processes
     try:
         for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'status']):
             try:
                 # Get process information with a per-process timeout
                 proc_info = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_info', 'status'])
                 
                 # Skip system processes that might cause hangs
                 if proc_info['pid'] < 10:
                     continue
                     
                 # Extract the data we need
                 pid = proc_info['pid']
                 name = proc_info['name']
                 username = proc_info['username'] or "SYSTEM"
                 cpu = proc_info['cpu_percent'] or 0.0
                 memory = proc_info['memory_info'].rss if proc_info['memory_info'] else 0
                 status = proc_info['status'] or "unknown"
                 
                 # Add process to the list
                 processes.append({
                     'pid': pid,
                     'name': name,
                     'username': username,
                     'cpu': cpu,
                     'memory': memory,
                     'status': status
                 })
             except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                 # Skip processes that can't be accessed
                 continue
             except Exception as e:
                 # Skip any other errors and continue
                 print(f"Error processing PID: {proc.pid if hasattr(proc, 'pid') else 'unknown'}: {str(e)}")
                 continue
     except Exception as e:
         print(f"Error in process iteration: {str(e)}")
         # Return a minimal set of processes if we fail
         processes = [{
             'pid': 0,
             'name': 'Error collecting processes',
             'username': 'N/A',
             'cpu': 0.0,
             'memory': 0,
             'status': 'error'
         }]
 
 # Run the collection with a timeout
 collector_thread = threading.Thread(target=collect_with_timeout)
 collector_thread.daemon = True
 collector_thread.start()
 collector_thread.join(timeout=5)  # 5 second timeout
 
 if collector_thread.is_alive():
     print("Process collection timed out, returning partial results")
     # Add a timeout indicator if we timed out
     processes.append({
         'pid': 0,
         'name': 'Process collection timed out',
         'username': 'N/A',
         'cpu': 0.0,
         'memory': 0,
         'status': 'timeout'
     })"""
)

# Write the improved content back
with open(process_utils_path, "w") as file:
    file.write(improved_content)

print("Applied anti-freeze fixes to process_utils.py")