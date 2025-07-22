
import socket
import platform as p
import psutil as pu
import datetime
from flask import Flask, render_template,Blueprint

comp_bp = Blueprint('main',__name__)  # default templates folder

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

@comp_bp.route("/main")
def home():
    return render_template("main.html", host=host, ip=ip, fqdn=fqdn,
                           os_info=os_info, cpu_info=cpu_info,
                           disk_info=disk_info, ram_info=ram_info,
                           time_info=time_info)

if __name__ == "__main__":
    comp_bp.run(debug=True)
