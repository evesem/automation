#!/bin/bash
set -euo pipefail

if [ -z "${ANSIBLE_PUBLIC_KEY:-}" ]; then
    echo "ERROR: ANSIBLE_PUBLIC_KEY is not set" >&2
    exit 1
fi

# Публичный ключ ansible-agent разрешён только для пользователя ansible.
echo "${ANSIBLE_PUBLIC_KEY}" > /home/ansible/.ssh/authorized_keys
chown ansible:ansible /home/ansible/.ssh/authorized_keys
chmod 600 /home/ansible/.ssh/authorized_keys

exec /usr/sbin/sshd -D -e
