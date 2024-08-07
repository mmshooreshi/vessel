from termcolor import colored

def log_info(message):
    print(colored(f"[INFO] {message}", "green"))

def log_warning(message):
    print(colored(f"[WARNING] {message}", "yellow"))

def log_error(message):
    print(colored(f"[ERROR] {message}", "red"))

def log_debug(message):
    print(colored(f"[DEBUG] {message}", "cyan"))

def log_critical(message):
    print(colored(f"[CRITICAL] {message}", "magenta"))
