# whitelist_editor.py
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Querybox
import winreg


class WhitelistEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Редактор белого списка")
        self.root.geometry("650x400")

        # Стиль (используем тему 'minty' из ttkbootstrap)
        self.style = ttk.Style(theme='minty')

        self.create_widgets()
        self.load_whitelist()

    def create_widgets(self):
        """Создаем элементы интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Список
        self.listbox = tk.Listbox(
            main_frame,
            selectmode=tk.SINGLE,
            font=('Segoe UI', 10),
            height=10
        )
        self.listbox.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.listbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(
            btn_frame,
            text="Добавить",
            command=self.add_path,
            bootstyle="success"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Удалить",
            command=self.remove_path,
            bootstyle="danger"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Применить",
            command=self.apply_changes,
            bootstyle="primary"
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_frame,
            text="Экспорт",
            command=self.export_whitelist,
            bootstyle="info"
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            btn_frame,
            text="Импорт",
            command=self.import_whitelist,
            bootstyle="info"
        ).pack(side=tk.RIGHT, padx=5)

    def load_whitelist(self):
        """Загружаем белый список из реестра"""
        self.listbox.delete(0, tk.END)
        whitelist = self.get_whitelist()
        for item in whitelist:
            self.listbox.insert(tk.END, item["Path"])

    def get_whitelist(self):
        """Получаем список из реестра Windows"""
        base_key = r"SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\Paths"
        whitelist = []

        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, base_key) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            path = winreg.QueryValueEx(subkey, "ItemData")[0]
                            whitelist.append({"Path": path})
                        i += 1
                    except OSError:
                        break
        except WindowsError:
            pass

        return whitelist

    def save_whitelist(self, paths):
        """Сохраняем изменения в реестр"""
        base_key = r"SOFTWARE\Policies\Microsoft\Windows\Safer\CodeIdentifiers\Paths"

        try:
            winreg.DeleteKeyEx(winreg.HKEY_LOCAL_MACHINE, base_key)
        except WindowsError:
            pass

        winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, base_key)

        for i, entry in enumerate(paths):
            subkey = f"{base_key}\\{0x1000 + i}"
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, subkey)
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, subkey, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ItemData", 0, winreg.REG_SZ, entry["Path"])
                winreg.SetValueEx(key, "SaferFlags", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "Description", 0, winreg.REG_SZ, "Разрешённый путь")

    def add_path(self):
        """Добавляем новый путь"""
        path = Querybox.get_string(
            title="Добавить путь",
            prompt="Введите путь к разрешённой папке:",
            parent=self.root
        )

        if path and path not in self.listbox.get(0, tk.END):
            self.listbox.insert(tk.END, path)

    def remove_path(self):
        """Удаляем выбранный путь"""
        selection = self.listbox.curselection()
        if selection:
            self.listbox.delete(selection)

    def apply_changes(self):
        """Применяем изменения"""
        paths = [{"Path": self.listbox.get(i)} for i in range(self.listbox.size())]
        self.save_whitelist(paths)
        messagebox.showinfo("Готово", "Изменения применены")

    def export_whitelist(self):
        """Экспортируем список в JSON"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            title="Сохранить белый список"
        )

        if file_path:
            try:
                data = [self.listbox.get(i) for i in range(self.listbox.size())]
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                messagebox.showinfo("Экспорт", "Список сохранён")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def import_whitelist(self):
        """Импортируем список из JSON"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            title="Открыть белый список"
        )

        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self.listbox.delete(0, tk.END)
                for item in data:
                    self.listbox.insert(tk.END, item)
                messagebox.showinfo(
                    "Импорт",
                    "Список загружен. Не забудьте нажать 'Применить'"
                )
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить: {str(e)}")


def run_editor():
    """Запуск приложения"""
    root = ttk.Window()
    app = WhitelistEditor(root)
    root.mainloop()


if __name__ == "__main__":
    run_editor()