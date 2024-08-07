import platform
import socket
import psutil
import shutil
import datetime
import subprocess

def run_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_boot_time():
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    return bt.strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    boot_time = psutil.boot_time()
    now = datetime.datetime.now().timestamp()
    uptime_seconds = now - boot_time
    return str(datetime.timedelta(seconds=int(uptime_seconds)))

def get_last_reboot_logs():
    return run_command("journalctl -b -1 -n 50") or "No logs found for the last reboot."

def gather_system_info():
    system_info = {
        "Hostname": socket.gethostname(),
        "IP Address": run_command("hostname -I"),
        "OS": f"{platform.system()} {platform.release()}",
        "OS Version": platform.version(),
        "Architecture": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "Total Memory": f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GB",
        "Available Memory": f"{psutil.virtual_memory().available / (1024 ** 3):.2f} GB",
        "Used Memory": f"{psutil.virtual_memory().used / (1024 ** 3):.2f} GB",
        "Memory Usage": f"{psutil.virtual_memory().percent}%",
        "Total Disk Space": f"{shutil.disk_usage('/').total / (1024 ** 3):.2f} GB",
        "Used Disk Space": f"{shutil.disk_usage('/').used / (1024 ** 3):.2f} GB",
        "Free Disk Space": f"{shutil.disk_usage('/').free / (1024 ** 3):.2f} GB",
        "Disk Usage": f"{shutil.disk_usage('/').used / shutil.disk_usage('/').total * 100:.2f}%",
        "Network Interfaces": {iface: addr.address for iface, addrs in psutil.net_if_addrs().items() for addr in addrs if addr.family == socket.AF_INET},
        "Last Boot Time": get_boot_time(),
        "System Uptime": get_uptime(),
        "Last Reboot Logs": get_last_reboot_logs(),
    }
    return system_info
