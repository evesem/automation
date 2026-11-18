<?php

declare(strict_types=1);

require_once __DIR__ . '/src/Calculator.php';

use Lab04\Calculator;

$calculator = new Calculator();
$a = isset($_GET['a']) && is_numeric($_GET['a']) ? (float) $_GET['a'] : null;
$b = isset($_GET['b']) && is_numeric($_GET['b']) ? (float) $_GET['b'] : null;
$operation = isset($_GET['op']) ? (string) $_GET['op'] : 'add';
$result = null;
$error = null;

if ($a !== null && $b !== null) {
    try {
        $result = match ($operation) {
            'add' => $calculator->add($a, $b),
            'subtract' => $calculator->subtract($a, $b),
            'multiply' => $calculator->multiply($a, $b),
            'divide' => $calculator->divide($a, $b),
            default => throw new InvalidArgumentException('Unknown operation.'),
        };
    } catch (Throwable $exception) {
        $error = $exception->getMessage();
    }
}
?>
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
    <title>IW05 — PHP приложение на тестовом сервере</title>
    <style>
        body { font-family: sans-serif; margin: 2rem; }
        code { background: #f2f2f2; padding: 0.1rem 0.3rem; }
        .result { font-weight: bold; color: #1a7f37; }
        .error { font-weight: bold; color: #b42318; }
    </style>
</head>
<body>
    <h1>IW05: PHP-проект развёрнут через Ansible</h1>
    <p>PHP версия: <code><?= htmlspecialchars(PHP_VERSION, ENT_QUOTES, 'UTF-8') ?></code></p>

    <h2>Калькулятор</h2>
    <form method="get">
        <input type="number" step="any" name="a" value="<?= $a ?? 3 ?>" required>
        <select name="op">
            <option value="add" <?= $operation === 'add' ? 'selected' : '' ?>>+</option>
            <option value="subtract" <?= $operation === 'subtract' ? 'selected' : '' ?>>−</option>
            <option value="multiply" <?= $operation === 'multiply' ? 'selected' : '' ?>>×</option>
            <option value="divide" <?= $operation === 'divide' ? 'selected' : '' ?>>÷</option>
        </select>
        <input type="number" step="any" name="b" value="<?= $b ?? 4 ?>" required>
        <button type="submit">Вычислить</button>
    </form>

    <?php if ($error !== null): ?>
        <p class="error">Ошибка: <?= htmlspecialchars($error, ENT_QUOTES, 'UTF-8') ?></p>
    <?php elseif ($result !== null): ?>
        <p class="result">Результат: <?= htmlspecialchars((string) $result, ENT_QUOTES, 'UTF-8') ?></p>
    <?php else: ?>
        <p>Отправьте форму, чтобы выполнить вычисление. Например:
            <a href="/?a=3&amp;b=4&amp;op=add">3 + 4</a></p>
    <?php endif; ?>
</body>
</html>
