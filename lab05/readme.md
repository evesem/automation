# IW05: Ansible playbook для конфигурации сервера

## 1. Описание проекта

Лабораторная работа развивает окружение IW04. В `compose.yaml` описаны четыре сервиса:

| Сервис | Образ | Назначение | Порты на хосте |
| --- | --- | --- | --- |
| `jenkins-controller` | `jenkins/jenkins:lts-jdk17` | Оркестрация всех этапов | 8080 (UI), 50000 (агенты) |
| `ssh-agent` | `Dockerfile.ssh_agent` | Сборка PHP-проекта и PHPUnit (метка `php-agent`) | — |
| `ansible-agent` | `Dockerfile.ansible_agent` | Выполнение Ansible playbook (метка `ansible-agent`) | — |
| `test-server` | `Dockerfile.test_server` | Целевой сервер с Apache, PHP и пользователем `ansible` | 2222 → 22 (SSH), 8081 → 80 (HTTP) |

PHP-проект «Калькулятор» скопирован из `lab04`: класс `src/Calculator.php`, пять модульных
тестов `tests/CalculatorTest.php`, `composer.json` и `phpunit.xml`. Добавлен `index.php`,
чтобы результат размещения можно было открыть в браузере.

Все приватные SSH-ключи создаются локально и не хранятся в Git. Публичные ключи передаются
в контейнеры через переменные окружения, приватный ключ Ansible монтируется как Docker secret.

## 2. Подготовка и быстрый старт

Из каталога `lab05`:

```powershell
# 1. Создать три пары ключей и файл .env (Windows)
.\secrets\generate-keys.ps1

# 2. Поднять окружение
docker compose up -d --build

# 3. Проверить состояние
docker compose ps
```

Для Linux/macOS используется `bash secrets/generate-keys.sh`.
Шаблон переменных — `.env.example`. Итоговый `.env` и каталог `secrets/` с приватными
ключами исключены из Git.

Созданные пары ключей:

| Файл | Использование |
| --- | --- |
| `secrets/id_ed25519_jenkins_php` | Jenkins Controller → `ssh-agent` |
| `secrets/id_ed25519_jenkins_ansible` | Jenkins Controller → `ansible-agent` |
| `secrets/id_ed25519_ansible` | `ansible-agent` → `test-server` (пользователь `ansible`) |

## 3. Настройка Jenkins Controller

1. Убедиться, что запущены Docker Engine и Docker Compose.
2. Выполнить `docker compose up -d --build` в каталоге `lab05`.
3. Открыть `http://localhost:8080` и получить стартовый пароль:

   ```bash
   docker compose exec jenkins-controller cat /var/jenkins_home/secrets/initialAdminPassword
   ```

4. Завершить мастер настройки: установить рекомендуемые плагины, создать администратора,
   подтвердить URL Jenkins.
5. В **Manage Jenkins → Plugins → Available plugins** дополнительно установить:
   **Docker**, **Docker Pipeline**, **GitHub Integration**, **SSH Agent**
   (и **SSH Build Agents**, если он не вошёл в рекомендуемый набор). Перезапустить Jenkins.

## 4. Настройка SSH-агента (повторение IW04)

1. Публичный ключ из `secrets/id_ed25519_jenkins_php.pub` записан в `.env` как
   `JENKINS_AGENT_SSH_PUBKEY`. Entrypoint образа `jenkins/ssh-agent` добавляет его в
   `authorized_keys` пользователя `jenkins`.
2. В Jenkins создать Credentials **SSH Username with private key**:
   - ID: `jenkins-php-agent-key`;
   - Username: `jenkins`;
   - Private Key: содержимое `secrets/id_ed25519_jenkins_php`.
3. Создать постоянный узел `ssh-agent1`:
   - Remote root directory: `/home/jenkins/agent`;
   - Labels: `php-agent`;
   - Launch method: **Launch agents via SSH**;
   - Host: `ssh-agent`, Port: `22`, Credentials: `jenkins-php-agent-key`;
   - Host Key Verification Strategy: **Manually trusted key** (подтвердить при первом подключении).
4. Убедиться, что узел в статусе **Online**. На агенте установлены PHP CLI, Composer,
   расширения `php-xml`, `php-mbstring`, `php-curl`, `php-zip`, Git и unzip.

## 5. Создание и настройка агента Ansible

1. `Dockerfile.ansible_agent` основан на `ubuntu:24.04`. Установлены `ansible`,
   `openssh-client`, `openssh-server`, `openjdk-17-jre-headless` (для remoting-агента Jenkins),
   `python3`, `git`, `curl`, `sudo`.
2. Публичный ключ `secrets/id_ed25519_jenkins_ansible.pub` передаётся переменной
   `JENKINS_ANSIBLE_AGENT_SSH_PUBKEY` и записывается в `authorized_keys` пользователя `jenkins`.
3. Приватный ключ `secrets/id_ed25519_ansible` монтируется Docker secret в
   `/run/secrets/ansible_private_key`; entrypoint копирует его в
   `/home/jenkins/.ssh/id_ed25519` с правами `600`. Этого достаточно, чтобы Ansible
   подключался к тестовому серверу от имени `ansible`.
4. В Jenkins создать вторые Credentials **SSH Username with private key**:
   - ID: `jenkins-ansible-agent-key`;
   - Username: `jenkins`;
   - Private Key: содержимое `secrets/id_ed25519_jenkins_ansible`.
5. Создать узел `ansible-agent1`: Remote root directory `/home/jenkins/agent`,
   метка `ansible-agent`, Launch agents via SSH, Host `ansible-agent`, Port `22`,
   указанные Credentials. Проверить статус **Online**.

## 6. Создание тестового сервера

1. `Dockerfile.test_server` также основан на `ubuntu:24.04`: установлены `openssh-server`,
   `python3`, `sudo`, `ca-certificates`; сгенерированы host keys sshd.
2. Создан пользователь `ansible` с домашним каталогом и `NOPASSWD:ALL` в sudoers —
   это необходимо tasks с `become: true`.
3. Публичный ключ из `.env` (`ANSIBLE_PUBLIC_KEY`, он же `secrets/id_ed25519_ansible.pub`)
   entrypoint записывает в `/home/ansible/.ssh/authorized_keys`. Парольный вход и вход root
   запрещены в `/etc/ssh/sshd_config.d/10-ansible.conf`.
4. Проверка подключения с ansible-агента:

   ```bash
   docker compose exec -u jenkins ansible-agent \
     ssh -i /home/jenkins/.ssh/id_ed25519 -o StrictHostKeyChecking=no ansible@test-server 'whoami'
   # ansible
   ```

## 7. Ansible playbook и его задачи

### Инвентарь

`ansible/hosts.ini` описывает группу `test_servers` с хостом `test-server`, пользователем
`ansible`, ключом `/home/jenkins/.ssh/id_ed25519` и интерпретатором Python.
`ansible.cfg` в каталоге `lab05` задаёт те же параметры по умолчанию и отключает проверку
host keys (допустимо только для лабораторного контура).

### `ansible/setup_test_server.yml`

1. `apt` устанавливает Apache2, `libapache2-mod-php`, PHP CLI и расширения
   (`mbstring`, `xml`, `curl`, `zip`), `unzip`, `git`.
2. Модуль `ansible.builtin.sysvinit` запускает Apache и включает его в автозагрузку.
   Использован sysvinit, потому что внутри контейнера нет systemd.
3. Создаётся каталог `/var/www/php-app` с владельцем `www-data`.
4. Из шаблона `templates/php-app.conf.j2` создаётся виртуальный хост `php-app.conf`
   с `DocumentRoot /var/www/php-app`; включается `rewrite`, включается новый сайт
   и отключается `000-default`. Изменения запускают handler **Restart Apache**.
5. Добавляется временная страница-заглушка (`force: false`), чтобы до запуска deploy
   pipeline сервер уже отвечал осмысленным сообщением.

### `ansible/deploy_php_project.yml`

1. Гарантирует наличие `/var/www/php-app`.
2. Копирует каталоги `src/` и `tests/`, а также файлы `index.php`, `composer.json`,
   `phpunit.xml` из клонированного репозитория на сервер; владелец — `www-data`.
3. Проверяет через `stat`, что `index.php` действительно развёрнут.

## 8. Конвейеры Jenkins

Все три задания создаются как **Pipeline → Pipeline script from SCM**:
репозиторий `https://github.com/evesem/automation.git`, ветка `*/main`.

| Задание | Script Path | Агент |
| --- | --- | --- |
| `php-build-and-test` | `lab05/pipelines/php_build_and_test_pipeline.groovy` | `php-agent` |
| `ansible-setup` | `lab05/pipelines/ansible_setup_pipeline.groovy` | `ansible-agent` |
| `php-deploy` | `lab05/pipelines/php_deploy_pipeline.groovy` | `ansible-agent` |

### 8.1. Сборка и тестирование PHP (повторение IW04)

Этапы: `Clone PHP repository` → `Install Composer dependencies` →
`Run PHPUnit tests` (с выводом JUnit-отчёта) → `Test report` (архивация отчёта).
Проверка: `composer install` и `vendor/bin/phpunit --configuration phpunit.xml`.

### 8.2. Настройка сервера через Ansible

Этапы: `Clone Ansible playbook repository` → `Run Ansible playbook`
(`ansible-playbook -i ansible/hosts.ini ansible/setup_test_server.yml`).

### 8.3. Размещение PHP-проекта

Этапы: `Clone PHP repository` →
`Copy project files to test server` (`ansible/deploy_php_project.yml`) →
`Verify deployed application` (`curl http://test-server/` и поиск строки `Calculator`).

### 8.4. Проверка в браузере

После успешного `php-deploy` открыть `http://localhost:8081/`. Должна отобразиться страница
с заголовком «IW05: PHP-проект развёрнут через Ansible», версией PHP и формой калькулятора.
Например, ссылка `/?a=3&b=4&op=add` должна вывести `Результат: 7`.

## 9. Проверка конфигурации

Команда `docker compose -f lab05/compose.yaml config --quiet` завершается без ошибок:
YAML корректен, все обязательные переменные окружения определены в `lab05/.env`.
Полный прогон контейнеров на машине выполнения был ограничен нехваткой свободного места
на диске `C:` (менее 3 МБ), поэтому скриншоты работающих конвейеров добавляются после
запуска на машине с доступным местом. Порядок получения скриншотов:

1. `docker compose ps` — все четыре сервиса в статусе `Up`.
2. Jenkins → узлы `ssh-agent1` и `ansible-agent1` в статусе **Online**.
3. Успешные сборки трёх pipeline.
4. `http://localhost:8081/` с работающей формой калькулятора.

## 10. Ответы на вопросы

### Какие преимущества использования Ansible для настройки серверов?

- **Идемпотентность**: повторный запуск playbook не меняет уже настроенное состояние,
  что безопасно для повторного применения.
- **Декларативность**: описывается желаемое состояние (пакеты, файлы, сервисы), а не
  последовательность команд; это проще читать и поддерживать.
- **Отсутствие агентов**: достаточно SSH и Python на целевом сервере, не нужно ставить
  дополнительный демон (в отличие от Puppet/Chef).
- **Масштабируемость**: один playbook применяется к группе хостов из инвентаря; переменные
  и роли позволяют переиспользовать код.
- **Интеграция с CI/CD**: playbook хранится в Git и запускается Jenkins, обеспечивая
  воспроизводимость инфраструктуры и аудит изменений.
- **Богатые модули и шаблоны**: `apt`, `template`, `copy`, `service`/`sysvinit`, `file`,
  `stat` и др. закрывают типовые задачи администрирования.

### Какие ещё бывают модули Ansible для управления конфигурацией?

Помимо использованных `apt`, `template`, `copy`, `file`, `stat`, `command` и `sysvinit`,
существуют:

- `ansible.builtin.yum` / `dnf` / `pacman` / `apk` — менеджеры пакетов других дистрибутивов;
- `ansible.builtin.systemd` / `sysvinit` / `service` — управление сервисами;
- `ansible.builtin.user` / `group` — управление учётными записями;
- `ansible.builtin.lineinfile` / `blockinfile` / `ini_file` — точечная правка конфигов;
- `ansible.posix.authorized_key` — управление SSH-ключами;
- `ansible.builtin.git` / `get_url` / `unarchive` — получение артефактов;
- `ansible.builtin.cron` — задания cron;
- `ansible.builtin.firewalld` / `iptables` — сетевые правила;
- `community.docker.docker_container`, `kubernetes.core.k8s` — контейнеры и Kubernetes;
- `ansible.builtin.debug`, `assert`, `fail`, `wait_for`, `uri` — отладка и проверки.

### С какими проблемами я столкнулся при создании playbook и как их решил?

1. **Нет systemd внутри контейнера.** Модуль `service` с автоопределением пытался
   обратиться к `systemctl`, которого в Ubuntu-контейнере нет. Решение — явно использовать
   `ansible.builtin.sysvinit` для Apache (`/etc/init.d/apache2` присутствует).
2. **Распространение SSH-ключей.** Ключ Jenkins → ansible-agent и ключ Ansible → test-server
   разные. Решение — три отдельные пары ключей; публичные передаются через переменные
   окружения, приватный ключ Ansible монтируется Docker secret и копируется entrypoint'ом
   в `.ssh` с правами `600`.
3. **Проверка host keys при первом подключении.** Решение — в лабораторном контуре
   `host_key_checking = False` в `ansible.cfg` и явные опции SSH; для продакшена следовало
   бы использовать `ssh-keyscan`/policy `accept-new` и доверие через known_hosts.
4. **Идемпотентность команд a2enmod/a2ensite/a2dissite.** Решение — регистрировать вывод
   команд и задавать `changed_when` по содержимому stdout, чтобы handler срабатывал только
   при реальном изменении конфигурации.
5. **Права на каталог приложения.** Решение — владелец `www-data:www-data` и режимы
   `0755` для каталогов, `0644` для файлов; временная страница создаётся с `force: false`,
   чтобы не затирать уже развёрнутое приложение.
