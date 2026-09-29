#!/usr/bin/env python3
"""
Маршрутизатор обращений для команды поддержки.
Читает обращения из JSON или CSV, определяет категорию и приоритет по правилам,
сохраняет результат в JSON.
"""

import sys
import os
import json
import csv
import argparse
from typing import List, Dict


# ---------- Нормализация ----------
def normalize(text: str) -> str:
    """Приводит текст к нижнему регистру и заменяет 'ё' на 'е'."""
    text = text.lower()
    text = text.replace("ё", "е")
    return text


# ---------- Правила маршрутизации ----------
# Порядок категорий важен – первое совпадение
CATEGORY_RULES = {
    "access": ["войти", "пароль", "нет доступа"],
    "billing": ["оплата", "счет", "тариф", "спис"],
    "bug": ["ошибка", "не работает", "падает", "недоступен"],
}
# Признаки высокого приоритета
HIGH_KEYWORDS = ["срочно", "критично", "недоступен всем"]


def determine_category(text: str) -> str:
    """
    Определяет категорию по первому совпадению ключевых слов.
    Если совпадений нет, то возвращает 'other'.
    """
    norm = normalize(text)
    for category, keywords in CATEGORY_RULES.items():
        for word in keywords:
            if word in norm:
                return category
    return "other"


def determine_priority(text: str, category: str) -> str:
    norm = normalize(text)
    for word in HIGH_KEYWORDS:
        if word in norm:
            return "high"
    if category in ("access", "bug"):
        return "medium"
    return "low"


def route_record(record: Dict[str, str]) -> Dict[str, str]:
    """Применяет маршрутизацию к одной записи."""
    text = record["text"]
    category = determine_category(text)
    priority = determine_priority(text, category)
    return {"id": record["id"], "category": category, "priority": priority}


# ---------- Чтение данных ----------
def read_json(filepath: str) -> List[Dict[str, str]]:
    """Читает JSON-файл с массивом записей."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Корневой элемент JSON должен быть массивом")
    return _normalize_records(data)


def read_csv(filepath: str) -> List[Dict[str, str]]:
    """Читает CSV-файл с заголовками."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    return _normalize_records(records)


def _normalize_records(records: List[Dict]) -> List[Dict[str, str]]:
    """
    Приводит каждую запись к словарю с полями id и text,
    удаляет пробелы, проверяет наличие и непустоту.
    """
    normalized = []
    for idx, rec in enumerate(records):
        record_id = str(rec.get("id", "")).strip()
        record_text = str(rec.get("text", "")).strip()
        if not record_id or not record_text:
            raise ValueError(f"в записи #{idx} отсутствует или пусто поле 'id' или 'text'")
        normalized.append({"id": record_id, "text": record_text})
    # print(*normalized, sep="\n")
    return normalized


def read_file(filepath: str) -> List[Dict[str, str]]:
    """Выбирает способ чтения в зависимости от расширения файла."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        return read_json(filepath)
    elif ext == ".csv":
        return read_csv(filepath)
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}. Ожидается .json или .csv")


# ---------- Основной сценарий ----------
def main() -> None:
    parser = argparse.ArgumentParser(description="Маршрутизатор обращений для команды поддержки.")
    parser.add_argument("--input", required=True, help="Путь к входному файлу (JSON или CSV)")
    parser.add_argument("--output", required=True, help="Путь для сохранения результата (JSON)")
    args = parser.parse_args()

    try:
        if not os.path.exists(args.input):
            raise FileNotFoundError(f"Входной файл не найден: {args.input}")
        records = read_file(args.input)
        results = [route_record(rec) for rec in records]
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"{e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Синтаксическая ошибка в JSON-файле", file=sys.stderr)
        sys.exit(2)
    except ValueError as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(3)
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
