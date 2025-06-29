# System Information Logger - Learning Version
# This script demonstrates how to gather system information step by step

import platform  # For OS and system info
import socket    # For network/IP information  
import psutil    # For detailed system info (CPU, memory, etc.)
import datetime  # For timestamps
import json      # For saving data in readable format

def get_hostname():
    """
    Get the computer's hostname (name on the network)
    
    Why this matters: Every computer has a name that identifies it
    on a network. This is useful for identifying which machine
    generated the log.
    """
    try:
        hostname = socket.gethostname()
        print(f"✓ Hostname found: {hostname}")
        return hostname
    except Exception as e:
        print(f"✗ Error getting hostname: {e}")
        return "Unknown"

def get_ip_address():
    """
    Get the computer's IP address
    
    Why this matters: IP address is how other devices communicate
    with your computer. We use a trick here - we connect to a 
    remote address to find our local IP.
    """
    try:
        # This is a clever trick: we create a connection to Google's DNS
        # but we don't actually send data. This tells us what IP we'd use
        # to reach the internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's DNS server
        ip = s.getsockname()[0]     # Get our IP from this connection
        s.close()
        print(f"✓ IP Address found: {ip}")
        return ip
    except Exception as e:
        print(f"✗ Error getting IP: {e}")
        return "Unknown"

def get_os_info():
    """
    Get detailed operating system information
    
    Why this matters: Different OS versions have different capabilities
    and limitations. This info is crucial for compatibility.
    """
    try:
        os_info = {
            'system': platform.system(),        # Windows, Darwin (Mac), Linux
            'release': platform.release(),      # Version number (10, 11, etc.)
            'version': platform.version(),      # Detailed version info
            'machine': platform.machine(),      # Architecture (x86_64, ARM, etc.)
            'processor': platform.processor()   # CPU type
        }
        print(f"✓ OS Info gathered: {os_info['system']} {os_info['release']}")
        return os_info
    except Exception as e:
        print(f"✗ Error getting OS info: {e}")
        return {}

def get_cpu_info():
    """
    Get CPU information and usage
    
    Why this matters: CPU info tells us processing power and current load.
    This is essential for performance monitoring.
    """
    try:
        cpu_info = {
            'physical_cores': psutil.cpu_count(logical=False),  # Actual CPU cores
            'total_cores': psutil.cpu_count(logical=True),      # Including hyperthreading
            'max_frequency': f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "Unknown",
            'current_frequency': f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "Unknown",
            'cpu_usage_percent': f"{psutil.cpu_percent(interval=1):.1f}%"  # Current usage
        }
        print(f"✓ CPU Info gathered: {cpu_info['total_cores']} cores, {cpu_info['cpu_usage_percent']} usage")
        return cpu_info
    except Exception as e:
        print(f"✗ Error getting CPU info: {e}")
        return {}

def get_memory_info():
    """
    Get memory (RAM) information
    
    Why this matters: Memory info tells us how much RAM we have
    and how much is being used. Critical for performance monitoring.
    """
    try:
        # Get virtual memory info (RAM)
        virtual_mem = psutil.virtual_memory()
        
        # Convert bytes to GB for readability
        def bytes_to_gb(bytes_value):
            return round(bytes_value / (1024**3), 2)
        
        memory_info = {
            'total_ram_gb': bytes_to_gb(virtual_mem.total),
            'available_ram_gb': bytes_to_gb(virtual_mem.available),
            'used_ram_gb': bytes_to_gb(virtual_mem.used),
            'ram_usage_percent': f"{virtual_mem.percent:.1f}%"
        }
        print(f"✓ Memory Info gathered: {memory_info['used_ram_gb']}GB/{memory_info['total_ram_gb']}GB used")
        return memory_info
    except Exception as e:
        print(f"✗ Error getting memory info: {e}")
        return {}

def collect_all_system_info():
    """
    Main function that collects all system information
    
    This function orchestrates all our data collection and
    returns a complete system profile.
    """
    print("🔍 Starting system information collection...")
    print("-" * 50)
    
    # Collect all information
    system_info = {
        'timestamp': datetime.datetime.now().isoformat(),  # When this was collected
        'hostname': get_hostname(),
        'ip_address': get_ip_address(),
        'operating_system': get_os_info(),
        'cpu_information': get_cpu_info(),
        'memory_information': get_memory_info()
    }
    
    print("-" * 50)
    print("✅ System information collection complete!")
    return system_info

def save_to_file(data, filename="system_info.json"):
    """
    Save the collected data to a JSON file
    
    Why JSON: JSON is human-readable and can be easily parsed
    by other programs. It's perfect for storing structured data.
    """
    try:
        with open(filename, 'w') as file:
            # indent=4 makes the JSON file nicely formatted and readable
            json.dump(data, file, indent=4)
        print(f"💾 Data saved to {filename}")
        return True
    except Exception as e:
        print(f"✗ Error saving file: {e}")
        return False

def display_info(data):
    """
    Display the collected information in a nice format
    
    This makes the information easy to read in the terminal
    """
    print("\n" + "="*60)
    print("           SYSTEM INFORMATION REPORT")
    print("="*60)
    
    print(f"Report Generated: {data['timestamp']}")
    print(f"Hostname: {data['hostname']}")
    print(f"IP Address: {data['ip_address']}")
    
    print(f"\n🖥️  Operating System:")
    os_info = data['operating_system']
    for key, value in os_info.items():
        print(f"    {key.title()}: {value}")
    
    print(f"\n⚡ CPU Information:")
    cpu_info = data['cpu_information']
    for key, value in cpu_info.items():
        print(f"    {key.replace('_', ' ').title()}: {value}")
    
    print(f"\n🧠 Memory Information:")
    memory_info = data['memory_information']
    for key, value in memory_info.items():
        print(f"    {key.replace('_', ' ').title()}: {value}")
    
    print("="*60)

# Main execution
if __name__ == "__main__":
    """
    This is where our program starts running
    
    The __name__ == "__main__" check ensures this code only runs
    when we execute this file directly, not when it's imported.
    """
    try:
        # Collect all system information
        system_data = collect_all_system_info()
        
        # Display the information nicely
        display_info(system_data)
        
        # Save to file
        save_to_file(system_data)
        
        # Ask user if they want to see the raw JSON
        print(f"\n📄 Raw JSON data saved to 'system_info.json'")
        show_json = input("Would you like to see the raw JSON data? (y/n): ").lower().strip()
        
        if show_json == 'y':
            print(f"\n📋 Raw JSON Data:")
            print(json.dumps(system_data, indent=2))
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Program interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("This might happen due to permissions or missing libraries")

# Learning Extensions - Try these challenges:
"""
🎯 BEGINNER CHALLENGES:
1. Add disk space information using psutil.disk_usage('/')
2. Add network interface information
3. Create a function to log information every 60 seconds
4. Add battery information for laptops

🎯 INTERMEDIATE CHALLENGES:
1. Create a web interface to display the information
2. Send the information to a remote server
3. Compare current info with previous logs to detect changes
4. Add alerts when CPU or memory usage is too high

🎯 ADVANCED CHALLENGES:
1. Create a monitoring dashboard
2. Add historical data tracking
3. Implement real-time monitoring with graphs
4. Create a distributed system to monitor multiple computers
"""
