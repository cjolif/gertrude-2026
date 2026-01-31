"""Tests for the agent tools."""

from gertrude.agent import calculate, get_current_time


def test_get_current_time() -> None:
    result = get_current_time.invoke({})
    # Should return a date-time string in expected format
    assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"
    assert "-" in result
    assert ":" in result


def test_calculate_simple() -> None:
    assert calculate.invoke({"expression": "2 + 2"}) == "4"
    assert calculate.invoke({"expression": "10 * 5"}) == "50"
    assert calculate.invoke({"expression": "2 ** 8"}) == "256"


def test_calculate_with_functions() -> None:
    assert calculate.invoke({"expression": "abs(-5)"}) == "5"
    assert calculate.invoke({"expression": "max(1, 2, 3)"}) == "3"


def test_calculate_invalid() -> None:
    result = calculate.invoke({"expression": "invalid"})
    assert "Error" in result
