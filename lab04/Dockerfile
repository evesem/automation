FROM jenkins/ssh-agent
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends php-cli composer \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
