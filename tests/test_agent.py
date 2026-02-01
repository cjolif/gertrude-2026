"""Tests for the agent tools."""

from gertrude.agent import change_tv_volume, get_current_time


def test_get_current_time() -> None:
    result = get_current_time.invoke({})
    # Should return a date-time string in expected format
    assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"
    assert "-" in result
    assert ":" in result


def test_change_tv_volume_invalid_action() -> None:
    result = change_tv_volume.invoke({"action": "invalid"})
    assert "Error" in result
    assert "Invalid action" in result
