# JSON Repair Tool

Инструмент для исправления ошибок в JSON файлах.

## Возможности

- Автоматическое обнаружение последнего JSON файла в указанной директории
- Исправление типичных ошибок в JSON:
  - Замена одинарных кавычек на двойные
  - Исправление экранирования
  - Добавление пропущенных кавычек
  - Замена пустых значений на null или 0 (для полей с 'sum' в названии)
- Поддержка различных кодировок (UTF-8, CP1251, Windows-1251)
- Конфигурация через INI файл

## Установка

1. Убедитесь, что у вас установлен Python 3.x
2. Установите необходимые зависимости:
```bash
pip install pyinstaller
```

## Использование

1. Создайте файл `repair.ini` со следующим содержимым:
```ini
[Paths]
source_path = путь_к_папке_с_исходными_файлами
target_dir = путь_к_папке_назначения
target_file = имя_файла_результата.json
```

2. Запустите программу:
```bash
python repair_json.py
```

Или используйте скомпилированную версию:
```bash
repair_json.exe
```

## Сборка

Для создания исполняемого файла выполните:
```bash
pyinstaller --onefile --console repair_json.py
```

Исполняемый файл будет создан в папке `dist`. 