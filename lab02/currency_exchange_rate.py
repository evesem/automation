"""Получение курса из учебного API и сохранение ответа в JSON."""

import argparse
from datetime import date
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
CURRENCIES = {"MDL", "USD", "EUR", "RON", "RUS", "UAH"}


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(f"Ошибка аргументов: {message}")


def parse_args():
    parser = Parser(description=__doc__)
    parser.add_argument("source", help="Исходная валюта, например USD")
    parser.add_argument("target", help="Целевая валюта, например EUR")
    parser.add_argument("date", help="Дата в формате ГГГГ-ММ-ДД")
    parser.add_argument("--url", default=os.getenv("API_URL", "http://localhost:8080/"),
                        help="Адрес API (по умолчанию http://localhost:8080/)")
    args = parser.parse_args()
    args.source, args.target = args.source.upper(), args.target.upper()
    for currency in (args.source, args.target):
        if currency not in CURRENCIES:
            raise ValueError(f"Неизвестная валюта {currency}. Допустимы: {', '.join(sorted(CURRENCIES))}")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.date):
        raise ValueError("Дата должна иметь формат ГГГГ-ММ-ДД.")
    try:
        requested = date.fromisoformat(args.date)
    except ValueError as exc:
        raise ValueError("Указана несуществующая календарная дата.") from exc
    if not date(2025, 1, 1) <= requested <= date(2025, 9, 15):
        raise ValueError("Дата должна быть между 2025-01-01 и 2025-09-15 включительно.")
    url = urlsplit(args.url)
    if url.scheme not in ("http", "https") or not url.netloc or url.query or url.fragment or url.username:
        raise ValueError("Укажите HTTP(S)-адрес API без параметров, пароля и фрагмента.")
    return args


def get_exchange_rate(args, key):
    query = urlencode({"from": args.source, "to": args.target, "date": args.date})
    request = Request(args.url + "?" + query,
                      data=urlencode({"key": key}).encode("utf-8"),
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      method="POST")
    try:
        with urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise ValueError(f"Ошибка HTTP: {exc.code}.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ValueError("Не удалось подключиться к API или истекло время ожидания. Проверьте адрес и запуск сервиса.") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("API вернул некорректный JSON.") from exc
    if not isinstance(result, dict) or "error" not in result:
        raise ValueError("Неожиданная структура ответа API.")
    if result["error"]:
        message = str(result["error"]).replace(key, "[ключ скрыт]")
        translations = {"Invalid API key": "Неверный ключ API", "API key is missing": "Отсутствует ключ API",
                        "Unknown currency rus": "В данных сервиса нет валюты RUS (используется поле rub)"}
        raise ValueError("Ошибка API: " + translations.get(message, message))
    data = result.get("data")
    if not isinstance(data, dict) or any(data.get(k) != v for k, v in
            (("from", args.source), ("to", args.target), ("date", args.date))):
        raise ValueError("Параметры ответа API не совпадают с запросом.")
    rate = data.get("rate")
    if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate) or rate <= 0:
        raise ValueError("API вернул недопустимое значение курса.")
    return result


def save_data(result):
    data = result["data"]
    directory = ROOT / "data"
    directory.mkdir(exist_ok=True)
    path = directory / f"{data['from']}_{data['to']}_{data['date']}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return path


def main():
    try:
        args = parse_args()
        key = os.getenv("API_KEY", "")
        if not key:
            raise ValueError("Задайте ключ сервиса в переменной окружения API_KEY.")
        result = get_exchange_rate(args, key)
        path = save_data(result)
        print(f"Курс {args.source}/{args.target} на {args.date}: {result['data']['rate']}")
        print(f"Ответ сохранён: {path}")
        return 0
    except (ValueError, OSError) as exc:
        message = str(exc)
        key = os.getenv("API_KEY")
        if key:
            message = message.replace(key, "[ключ скрыт]")
        print(f"Ошибка: {message}", file=sys.stderr)
        try:
            logging.basicConfig(filename=ROOT / "error.log", encoding="utf-8", level=logging.ERROR,
                                format="%(asctime)s %(levelname)s %(message)s")
            logging.error(message.replace("\n", " ").replace("\r", " "))
        except OSError:
            print("Не удалось записать error.log. Проверьте права на каталог проекта.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
