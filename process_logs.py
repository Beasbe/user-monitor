import os
import re

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")

def process_line(line: str) -> str:
    # Отделяем префикс (время + процесс + окно)
    match = re.match(r"^(.*? - \[.*?\] - \".*?\" - )(.*)$", line)
    if not match:
        return line.strip()

    prefix, content = match.groups()
    result = []

    i = 0
    while i < len(content):
        if content.startswith("[Backspace]", i):
            if result:
                result.pop()
            i += len("[Backspace]")
        elif content[i] == "[":
            # спецсимвол типа [Tab]
            end = content.find("]", i)
            if end != -1:
                result.append(content[i:end+1])
                i = end + 1
            else:
                result.append(content[i])
                i += 1
        else:
            result.append(content[i])
            i += 1

    return prefix + "".join(result).strip()

def process_file(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    processed = [process_line(line) for line in lines]

    with open(path, "w", encoding="utf-8") as f:
        for line in processed:
            f.write(line + "\n")

def process_all_logs():
    for filename in os.listdir(LOG_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(LOG_DIR, filename)
            print(f"Обработка файла: {filename}")
            process_file(path)

if __name__ == "__main__":
    process_all_logs()
