FROM jenkins/ssh-agent
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends php-cli composer php-xml php-mbstring php-curl \
    && rm -rf /var/lib/apt/lists/*