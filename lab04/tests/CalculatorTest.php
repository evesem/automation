<?php

declare(strict_types=1);

namespace Lab04\Tests;

use InvalidArgumentException;
use Lab04\Calculator;
use PHPUnit\Framework\TestCase;

final class CalculatorTest extends TestCase
{
    private Calculator $calculator;

    protected function setUp(): void
    {
        $this->calculator = new Calculator();
    }

    public function testAddReturnsSum(): void
    {
        self::assertSame(7.0, $this->calculator->add(3, 4));
    }

    public function testSubtractReturnsDifference(): void
    {
        self::assertSame(6.0, $this->calculator->subtract(10, 4));
    }

    public function testMultiplyReturnsProduct(): void
    {
        self::assertSame(21.0, $this->calculator->multiply(3, 7));
    }

    public function testDivideReturnsQuotient(): void
    {
        self::assertSame(2.5, $this->calculator->divide(5, 2));
    }

    public function testDivideByZeroThrowsException(): void
    {
        $this->expectException(InvalidArgumentException::class);
        $this->calculator->divide(5, 0);
    }
}
