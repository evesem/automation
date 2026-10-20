FROM python:3.13-slim-bookworm
ENV TZ=Europe/Chisinau PYTHONUNBUFFERED=1
RUN apt-get update \
    && apt-get install -y --no-install-recommends cron tzdata \
    && rm -rf /var/lib/apt/lists/* \
    && ln -snf /usr/share/zoneinfo/Europe/Chisinau /etc/localtime \
    && echo Europe/Chisinau > /etc/timezone
WORKDIR /app/lab03
COPY currency_exchange_rate.py run_scheduled.py ./
COPY cronjob /tmp/cronjob
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod 755 /usr/local/bin/entrypoint.sh && crontab /tmp/cronjob && rm /tmp/cronjob
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
