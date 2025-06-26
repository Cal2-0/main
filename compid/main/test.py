'''import socket
import platform as p
import psutil as pu
import datetime
import sys
from flask import Flask, render_template
import os


# Convert bytes to GB
def gb(bytes_value):
    return round(bytes_value / (1024**3), 2)

# System + network info
host = socket.gethostname()
ip = socket.gethostbyname(host)
fqdn = socket.getfqdn()

from flask import Flask, render_template
import socket
app = Flask(__name__, template_folder='.')

@app.route("/")
def home():
    host = socket.gethostname()
    return render_template("main.html", result=host,ip=ip,fqdn=fqdn)

if __name__ == "__main__":
    app.run(debug=True)


print(f"Python Executable: {sys.executable}")
print(f"Host Name: {host}")
print(f"IP Address: {ip}")
print(f"FQDN: {fqdn}")

# OS info
print("\n--- OS Info ---")
print(f"OS: {p.system()}")
print(f"Release: {p.release()}")
print(f"Version: {p.version()}")
print(f"Architecture: {p.machine()}")
print(f"CPU: {p.processor()}")
print(f"Node: {p.node()}")

# CPU Info
print("\n--- CPU Info ---")
print(f"Physical Cores: {pu.cpu_count(logical=False)}")
print(f"Total Cores: {pu.cpu_count(logical=True)}")
print(f"CPU Max Frequency: {pu.cpu_freq().max:.2f} MHz")
print(f"CPU Current Frequency: {pu.cpu_freq().current:.2f} MHz")
print(f"CPU Usage: {pu.cpu_percent(interval=1)} %")

# Disk Usage
disk = pu.disk_usage("C:\\")
print(f"\n--- Disk Info ---")
print(f"Total Disk Space: {gb(disk.total)} GB")
print(f"Used Disk Space: {gb(disk.used)} GB")
print(f"Free Disk Space: {gb(disk.free)} GB")

# RAM Usage
mem = pu.virtual_memory()
print(f"\n--- RAM Info ---")
print(f"Available RAM: {gb(mem.available)} GB")
print(f"Total RAM: {gb(mem.total)} GB")
print(f"Used RAM: {gb(mem.used)} GB")

# Boot time
boot_time = datetime.datetime.fromtimestamp(pu.boot_time())
print(f"\n--- Boot Time ---")
print(f"System Booted On: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}")

# Current time
now = datetime.datetime.now()
print(f"\n--- Current Time ---")
print(f"Date and Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
'''
import socket
import platform as p
import psutil as pu
import datetime
from flask import Flask, render_template

app = Flask(__name__)  # default templates folder

# Convert bytes to GB
def gb(bytes_value):
    return round(bytes_value / (1024**3), 2)

# Get system + network info
host = socket.gethostname()
ip = socket.gethostbyname(host)
fqdn = socket.getfqdn()

# OS info
os_info = {
    "system": p.system(),
    "release": p.release(),
    "version": p.version(),
    "architecture": p.machine(),
    "cpu": p.processor(),
    "node": p.node()
}

# CPU Info
cpu_info = {
    "physical_cores": pu.cpu_count(logical=False),
    "total_cores": pu.cpu_count(logical=True),
    "max_freq": f"{pu.cpu_freq().max:.2f} MHz",
    "current_freq": f"{pu.cpu_freq().current:.2f} MHz",
    "usage": f"{pu.cpu_percent(interval=1)} %"
}

# Get valid disk info safely
def get_valid_disk():
    for part in pu.disk_partitions():
        try:
            usage = pu.disk_usage(part.mountpoint)
            return {
                "mount": part.mountpoint,
                "total": f"{gb(usage.total)} GB",
                "used": f"{gb(usage.used)} GB",
                "free": f"{gb(usage.free)} GB"
            }
        except:
            continue
    return {
        "mount": "N/A",
        "total": "N/A",
        "used": "N/A",
        "free": "N/A"
    }

disk_info = get_valid_disk()

# RAM Info
mem = pu.virtual_memory()
ram_info = {
    "available": f"{gb(mem.available)} GB",
    "total": f"{gb(mem.total)} GB",
    "used": f"{gb(mem.used)} GB"
}

# Boot and current time
boot_time = datetime.datetime.fromtimestamp(pu.boot_time())
now = datetime.datetime.now()
time_info = {
    "boot": boot_time.strftime('%Y-%m-%d %H:%M:%S'),
    "now": now.strftime('%Y-%m-%d %H:%M:%S')
}

@app.route("/")
def home():
    return render_template("main.html", host=host, ip=ip, fqdn=fqdn,
                           os_info=os_info, cpu_info=cpu_info,
                           disk_info=disk_info, ram_info=ram_info,
                           time_info=time_info)

if __name__ == "__main__":
    app.run(debug=True)
