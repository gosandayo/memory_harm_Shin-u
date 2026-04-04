"""Tests for utility functions."""

import pytest
import numpy as np
from src.utils import (
    clip,
    configure_llm_backend,
    fmt_approval,
    get_llm_backend_config,
    render_history,
    setup_rng,
    validate_score,
)


def test_clip():
    """Test clipping function."""
    assert clip(0.5, 0, 1) == 0.5
    assert clip(-0.1, 0, 1) == 0.0
    assert clip(1.5, 0, 1) == 1.0
    assert clip(5, 0, 10) == 5
    assert clip(-5, 0, 10) == 0
    assert clip(15, 0, 10) == 10


def test_validate_score():
    """Test score validation."""
    assert validate_score(5.0, "test") == 5.0
    assert validate_score(0.0, "test") == 0.0
    assert validate_score(10.0, "test") == 10.0
    assert validate_score(-1.0, "test") == 0.0  # Clipped
    assert validate_score(11.0, "test") == 10.0  # Clipped

    with pytest.raises(ValueError):
        validate_score("not a number", "test")


def test_setup_rng():
    """Test RNG setup."""
    rng1 = setup_rng(42)
    rng2 = setup_rng(42)

    # Same seed should give same results
    assert rng1.random() == pytest.approx(rng2.random())


def test_render_history():
    """Test history rendering."""
    history = [
        ("user", "Hello"),
        ("assistant", "Hi there!"),
        ("user", "How are you?"),
        ("assistant", "I'm doing well, thanks!")
    ]

    rendered = render_history(history)
    assert "User: Hello" in rendered
    assert "Assistant: Hi there!" in rendered

    # Empty history
    assert render_history([]) == "(No previous conversation)"


def test_fmt_approval():
    """Test approval formatting."""
    assert "7.5/10" in fmt_approval(7.5)
    assert "None" in fmt_approval(None)
    assert "first turn" in fmt_approval(None)


def test_approval_score_formula():
    """Test that approval score formula is correct."""
    # Perfect match
    enablement = 5.0
    indulgence = 5.0
    expected_approval = 10 * (1 - abs(enablement - indulgence) / 10)
    assert expected_approval == 10.0

    # Maximum mismatch
    enablement = 0.0
    indulgence = 10.0
    expected_approval = 10 * (1 - abs(enablement - indulgence) / 10)
    assert expected_approval == 0.0

    # Partial match
    enablement = 6.0
    indulgence = 4.0
    expected_approval = 10 * (1 - abs(enablement - indulgence) / 10)
    assert expected_approval == pytest.approx(8.0)


def test_indulgence_formula():
    """Test that indulgence score formula is correct."""
    # Low D
    D = 0.2
    indulgence = 10 * D
    assert indulgence == 2.0

    # High D
    D = 0.8
    indulgence = 10 * D
    assert indulgence == 8.0

    # Medium D
    D = 0.5
    indulgence = 10 * D
    assert indulgence == 5.0


def test_configure_llm_backend_switches_base_url_and_key():
    """LLM backend config should be mutable from notebook code."""
    original = get_llm_backend_config()

    try:
        configure_llm_backend(api_key="test-key", base_url=None)
        assert get_llm_backend_config() == {
            "api_key": "test-key",
            "base_url": None,
        }

        configure_llm_backend()
        assert get_llm_backend_config() == {
            "api_key": "EMPTY",
            "base_url": None,
        }
    finally:
        configure_llm_backend(
            api_key=original["api_key"],
            base_url=original["base_url"],
        )
