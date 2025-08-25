import os
import sys
import win32com.client


def add_to_autostart(target_path, shortcut_name="UserMonitor"):
    try:
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, f"{shortcut_name}.lnk")

        if os.path.exists(shortcut_path):
            return True

        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path

        # Для EXE не нужны аргументы
        if target_path.endswith('.py'):
            shortcut.Arguments = f'"{target_path}"'

        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()

        return True
    except Exception as e:
        print(f"Ошибка автозагрузки: {e}")
        return False