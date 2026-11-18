# SSH-ключи для lab05

В этой папке хранятся **локальные** приватные ключи. Они не должны попадать в Git.

Перед первым запуском выполнится один из сценариев:

```powershell
# Windows (PowerShell), из каталога lab05
.\secrets\generate-keys.ps1
```

```bash
# Linux / macOS, из каталога lab05
bash secrets/generate-keys.sh
```

Сценарий создаст три пары ключей и файл `lab05/.env`:

| Ключ | Назначение |
| --- | --- |
| `id_ed25519_jenkins_php` | Jenkins Controller → ssh-agent (PHP) |
| `id_ed25519_jenkins_ansible` | Jenkins Controller → ansible-agent |
| `id_ed25519_ansible` | ansible-agent → test-server (пользователь `ansible`) |

Приватные ключи монтируются в контейнеры через Docker secrets / переменные окружения,
публичные ключи попадают в `authorized_keys` соответствующих контейнеров.
