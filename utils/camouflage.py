import os
import ctypes
from utils.logging import log_debug, log_info, log_error

def set_process_name(name):
    log_debug(f"Setting process name to {name}")
    try:
        libc = ctypes.CDLL('libc.so.6')
        libc.prctl(15, name.encode(), 0, 0, 0)
        log_info("Process name set successfully")
    except Exception as e:
        log_error(f"Failed to set process name: {e}")

def hide_file(filepath):
    log_debug(f"Hiding file: {filepath}")
    try:
        os.system(f"chattr +i {filepath}")
        log_info(f"File {filepath} is now hidden")
    except Exception as e:
        log_error(f"Failed to hide file: {e}")
