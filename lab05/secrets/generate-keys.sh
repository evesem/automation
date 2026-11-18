#!/usr/bin/env bash
set -euo pipefail

lab_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
secrets_dir="$lab_dir/secrets"
mkdir -p "$secrets_dir"

new_key_pair() {
    local file_name="$1" comment="$2" private_path="$secrets_dir/$1"
    if [ -f "$private_path" ]; then
        echo "$file_name already exists, reusing it."
    else
        ssh-keygen -q -t ed25519 -N '' -C "$comment" -f "$private_path"
    fi
    cat "$private_path.pub"
}

php_key="$(new_key_pair id_ed25519_jenkins_php jenkins-php)"
ansible_agent_key="$(new_key_pair id_ed25519_jenkins_ansible jenkins-ansible)"
ansible_to_server_key="$(new_key_pair id_ed25519_ansible ansible-to-test-server)"

cat > "$lab_dir/.env" <<EOF
JENKINS_AGENT_SSH_PUBKEY=$php_key
JENKINS_ANSIBLE_AGENT_SSH_PUBKEY=$ansible_agent_key
ANSIBLE_PUBLIC_KEY=$ansible_to_server_key
ANSIBLE_PRIVATE_KEY_PATH=./secrets/id_ed25519_ansible
EOF

echo "Created $lab_dir/.env and SSH keys in $secrets_dir"
echo 'Private keys are ignored by Git. Never commit them.'
