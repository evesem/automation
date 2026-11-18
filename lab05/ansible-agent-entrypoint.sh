#!/bin/bash
set -euo pipefail

if [ -z "${JENKINS_ANSIBLE_AGENT_SSH_PUBKEY:-}" ]; then
    echo "ERROR: JENKINS_ANSIBLE_AGENT_SSH_PUBKEY is not set" >&2
    exit 1
fi

# Публичный ключ Jenkins Controller -> ansible-agent
echo "${JENKINS_ANSIBLE_AGENT_SSH_PUBKEY}" > /home/jenkins/.ssh/authorized_keys
chown jenkins:jenkins /home/jenkins/.ssh/authorized_keys
chmod 600 /home/jenkins/.ssh/authorized_keys

# Приватный ключ ansible-agent -> test-server (пользователь ansible)
if [ ! -f /run/secrets/ansible_private_key ]; then
    echo "ERROR: /run/secrets/ansible_private_key is not mounted" >&2
    exit 1
fi
install -m 600 -o jenkins -g jenkins /run/secrets/ansible_private_key /home/jenkins/.ssh/id_ed25519

exec /usr/sbin/sshd -D -e
