# from termcolor import colored

# def log_info(message):
#     print(colored(f"[INFO] {message}", "green"))

# def log_warning(message):
#     print(colored(f"[WARNING] {message}", "yellow"))

# def log_error(message):
#     print(colored(f"[ERROR] {message}", "red"))

# def log_debug(message):
#     print(colored(f"[DEBUG] {message}", "cyan"))

# def log_critical(message):
#     print(colored(f"[CRITICAL] {message}", "magenta"))



import logging
import coloredlogs

def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.DEBUG
    )
    coloredlogs.install(level='DEBUG', logger=logging.getLogger())

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.INFO)
    logging.getLogger("telegram.ext").setLevel(logging.INFO)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
