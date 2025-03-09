import os
import json
import re
import configparser
from pathlib import Path
from datetime import datetime

def fix_empty_value(match):
    """
    Заменяет пустые значения на null или 0 в зависимости от ключа
    """
    full_match = match.group(0)  # Получаем весь найденный текст
    # Ищем ключ в кавычках перед :
    key_match = re.search(r'"([^"]+)"(?=\s*:)', full_match)
    if key_match:
        key = key_match.group(1)
        # Если ключ содержит 'sum' (регистронезависимо), возвращаем 0
        if 'sum' in key.lower():
            return full_match.replace(':', ':0')
    # В остальных случаях возвращаем null
    return full_match.replace(':', ':null')

def fix_json_errors(json_str: str) -> str:
    """
    Исправляет типичные ошибки в JSON строке
    """
    # Удаляем BOM маркер, если он есть
    json_str = json_str.strip('\ufeff')
    
    # Удаляем возможные пробельные символы в начале и конце
    json_str = json_str.strip()
    
    # Заменяем неправильные кавычки на правильные
    json_str = json_str.replace("'", '"')
    json_str = json_str.replace("«", '"').replace("»", '"')
    
    # Удаляем лишние запятые перед закрывающими скобками
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    # Исправляем экранирование кавычек
    json_str = re.sub(r'(?<!\\)\\"', '"', json_str)
    
    # Исправляем неправильное экранирование
    json_str = json_str.replace('\\\\', '\\')
    
    # Исправляем пропущенные кавычки вокруг ключей
    json_str = re.sub(r'([{,]\s*)([a-zA-Zа-яА-Я_]\w*)\s*:', r'\1"\2":', json_str)
    
    # Исправляем пустые значения на null или 0 (в зависимости от ключа)
    # Ищем паттерны вида "ключ": , или "ключ":,
    json_str = re.sub(r'"[^"]+"\s*:\s*(?=,|]|})', fix_empty_value, json_str)
    
    # Исправляем пропущенные кавычки вокруг строковых значений
    json_str = re.sub(r':\s*([a-zA-Zа-яА-Я_][^,}\]]*?)([,}\]])', r':"\1"\2', json_str)
    
    return json_str

def read_file_with_encoding(file_path):
    """
    Пытается прочитать файл с разными кодировками
    """
    encodings = ['utf-8', 'cp1251', 'windows-1251', 'ascii']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Не удалось прочитать файл ни с одной из кодировок: {encodings}")

def read_config():
    """
    Читает конфигурацию из файла repair.ini
    """
    config = configparser.ConfigParser()
    
    # Определяем путь к ini файлу относительно текущего скрипта
    ini_path = Path(__file__).parent / 'repair.ini'
    
    if not ini_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {ini_path}")
    
    config.read(ini_path, encoding='utf-8')
    
    if 'Paths' not in config:
        raise ValueError("Секция 'Paths' не найдена в файле конфигурации")
    
    required_params = ['source_path', 'target_dir', 'target_file']
    for param in required_params:
        if param not in config['Paths']:
            raise ValueError(f"Параметр '{param}' не найден в файле конфигурации")
    
    return {
        'source_path': config['Paths']['source_path'],
        'target_path': str(Path(config['Paths']['target_dir']) / config['Paths']['target_file'])
    }

def main():
    try:
        # Читаем конфигурацию
        config = read_config()
        source_path = config['source_path']
        target_path = config['target_path']
        
        # Получаем список всех JSON файлов в директории
        json_files = list(Path(source_path).glob('*.json'))
        
        if not json_files:
            print("JSON файлы не найдены в указанной директории")
            return
        
        # Находим самый последний файл по времени изменения
        last_file = max(json_files, key=lambda x: x.stat().st_mtime)
        print(f"Обрабатывается файл: {last_file}")
        
        # Читаем содержимое файла с автоопределением кодировки
        json_content = read_file_with_encoding(last_file)
        
        # Исправляем ошибки в JSON
        json_content = fix_json_errors(json_content)
        
        # Проверяем валидность JSON
        try:
            # Попытка разобрать JSON для проверки
            parsed_json = json.loads(json_content)
            # Преобразуем обратно в строку с правильным форматированием
            json_content = json.dumps(parsed_json, ensure_ascii=False, indent=2)
        except json.JSONDecodeError as ex:
            print(f"Ошибка в структуре JSON: {str(ex)}")
            print("Проблемный участок:")
            lines = json_content.split('\n')
            line_num = ex.lineno - 1
            start = max(0, line_num - 2)
            end = min(len(lines), line_num + 3)
            for i in range(start, end):
                prefix = ">>> " if i == line_num else "    "
                print(f"{prefix}Строка {i+1}: {lines[i]}")
            return
            
        # Создаем директорию назначения, если она не существует
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        # Записываем исправленный JSON в новый файл
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
            
        print("Файл успешно обработан и сохранен")
        
    except Exception as ex:
        print(f"Произошла ошибка: {str(ex)}")
        input("Нажмите Enter для завершения...")  # Пауза перед закрытием

if __name__ == '__main__':
    main() 