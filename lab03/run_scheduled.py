"""Запуск клиента за вчера или за прошлую календарную неделю."""
import argparse
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import subprocess
import sys


def requested_dates(mode, today):
    if mode == "daily":
        return [today - timedelta(days=1)]
    monday = today - timedelta(days=today.weekday() + 7)
    return [monday + timedelta(days=i) for i in range(7)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("daily", "weekly"))
    parser.add_argument("--today", type=date.fromisoformat,
                        help="Опорная дата для ручной проверки")
    args = parser.parse_args()
    env = os.environ.copy()
    env.update(json.loads(Path("/run/cron-env.json").read_text(encoding="utf-8")))
    env["PYTHONUNBUFFERED"] = "1"
    target = "EUR" if args.mode == "daily" else "USD"
    failed = False
    for day in requested_dates(args.mode, args.today or date.today()):
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Начало MDL/{target}, дата {day}", flush=True)
        result = subprocess.run([sys.executable,
            str(Path(__file__).with_name("currency_exchange_rate.py")),
            "MDL", target, day.isoformat()], env=env, check=False)
        print(f"[{datetime.now().isoformat(timespec='seconds')}] Завершение, код {result.returncode}", flush=True)
        failed |= result.returncode != 0
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
