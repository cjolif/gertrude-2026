"""Tests for the agent tools."""

from gertrude.agent import get_current_time, tv_sound


def test_get_current_time() -> None:
    result = get_current_time.invoke({})
    # Should return a date-time string in expected format
    assert len(result) == 19  # "YYYY-MM-DD HH:MM:SS"
    assert "-" in result
    assert ":" in result


def test_tv_sound_invalid_action() -> None:
    result = tv_sound.invoke({"action": "invalid"})
    assert "Error" in result
    assert "Invalid action" in result
