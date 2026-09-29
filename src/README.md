# Маршрутизатор обращений

Программа для автоматического определения категории и приоритета обращений пользователей в службу поддержки.  
Обрабатывает входные файлы в форматах JSON и CSV, применяет явные правила маршрутизации и сохраняет результат в JSON.

## Требования

- Python 3 (проверено на версии 3.12)
- Стандартная библиотека (модули `json`, `csv`, `argparse`, `os`, `sys`)

## Поддерживаемые форматы

- **Входные файлы**: JSON (массив объектов с полями `id` и `text`) или CSV (с заголовками `id` и `text`).
- **Выходной файл**: JSON (массив объектов с полями `id`, `category`, `priority`).

## Использование

python3 src/main.py --input <путь_к_входному_файлу> --output <путь_к_результату>

## Проверено

python src/main.py --help

python src/main.py --input datasets/requests.json --output src/result.json

python src/main.py --input datasets/requests.csv --output src/result.json