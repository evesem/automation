<?php

declare(strict_types=1);

namespace Lab04;

use InvalidArgumentException;

final class Calculator
{
    public function add(float $left, float $right): float
    {
        return $left + $right;
    }

    public function subtract(float $left, float $right): float
    {
        return $left - $right;
    }

    public function multiply(float $left, float $right): float
    {
        return $left * $right;
    }

    public function divide(float $left, float $right): float
    {
        if ($right === 0.0) {
            throw new InvalidArgumentException('Делить на ноль нельзя.');
        }

        return $left / $right;
    }
}
