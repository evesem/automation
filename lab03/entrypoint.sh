#!/bin/sh
set -eu
umask 077
python -c 'import json, os; from pathlib import Path; Path("/run/cron-env.json").write_text(json.dumps({k: os.environ[k] for k in ("API_KEY", "API_URL") if k in os.environ}), encoding="utf-8")'
touch /var/log/cron.log
chmod 644 /var/log/cron.log
cron
tail -n 0 -F /var/log/cron.log &
tail_pid=$!
cleanup() {
    kill "$(cat /run/crond.pid)" "$tail_pid" 2>/dev/null || true
}
trap 'exit 0' TERM INT
trap cleanup EXIT
echo "Планировщик запущен. Часовой пояс: $(cat /etc/timezone)"
while kill -0 "$(cat /run/crond.pid)" 2>/dev/null && kill -0 "$tail_pid" 2>/dev/null; do
    sleep 1 &
    wait $! || true
done
echo "Планировщик или просмотр журнала остановлен" >&2
exit 1
