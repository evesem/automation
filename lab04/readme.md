# IW04: Jenkins и PHP CI

## Описание проекта

Небольшой PHP-проект «Калькулятор» с модульными тестами PHPUnit. Jenkins запускает Composer и тесты на SSH-агенте с PHP CLI и Composer.

## Состав

- `src/Calculator.php` — операции сложения, вычитания, умножения и деления.
- `tests/CalculatorTest.php` — пять PHPUnit-тестов, включая проверку деления на ноль.
- `composer.json`, `phpunit.xml` — зависимости и конфигурация тестирования.
- `Jenkinsfile` — CI-конвейер.
- `docker-compose.yml`, `Dockerfile` — Jenkins Controller и PHP SSH-агент.

## Запуск PHP-проекта локально

Нужны PHP 8.1+ и Composer. Из каталога `lab04` выполнить:

```sh
composer install
composer test
```

## Подключение Jenkins

Создать Pipeline job типа **Pipeline script from SCM**, подключить репозиторий `https://github.com/evesem/automation.git`, ветку `main`, Script Path `lab04/Jenkinsfile`. На настроенном SSH-агенте должна быть метка `php-agent`. Pipeline устанавливает зависимости в `lab04` и запускает PHPUnit.

Порядок запуска Controller и SSH-агента описан в `docker-compose.yml`, `Dockerfile` и `.env.example`. Перед запуском скопировать `.env.example` в `.env` и подставить публичный SSH-ключ. Закрытый SSH-ключ и настоящий `.env` в репозиторий не загружать.
