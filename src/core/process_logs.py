import os
import re

# Путь к директории с логами относительно текущего файла
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")


def process_line(line: str) -> str:
    """
    Обрабатывает одну строку лога, удаляя символы Backspace и нормализуя специальные клавиши.

    Args:
        line (str): Строка лога для обработки

    Returns:
        str: Обработанная строка с примененными Backspace и нормализованными специальными клавишами
    """
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
    Обрабатывает все текстовые файлы логов в директории LOG_DIR.
    Выводит прогресс обработки для каждого файла.
    """
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".txt"):  # Обрабатываем только текстовые файлы
            path = os.path.join(LOG_DIR, filename)
            print(f"Обработка файла: {filename}")
            process_file(path)  # Обрабатываем каждый файл


if __name__ == "__main__":
    process_all_logs()