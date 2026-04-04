"""Tests for lookism drift prompt helpers."""

from src.lookism_agent_drift import (
    LookismDriftConfig,
    _active_beat,
    _assistant_system_prompt,
    _assistant_response_cue,
    _conditional_disclosure_instruction,
    _active_context_threads,
    _recent_user_messages,
    _user_input_prompt,
    get_lookism_seed,
)


def test_recent_user_messages_only_returns_recent_user_turns():
    """Recent-user helper should ignore assistant messages."""
    history = [
        ("user", "u1"),
        ("assistant", "a1"),
        ("user", "u2"),
        ("assistant", "a2"),
        ("user", "u3"),
    ]
    assert _recent_user_messages(history, 2) == ["u2", "u3"]


def test_active_beat_reaches_late_disclosure_for_long_run():
    """Longer runs should progress into later disclosure beats."""
    seed = get_lookism_seed("heartbreak_glow_up")
    early = _active_beat(seed, turn_idx=0, total_turns=50)
    late = _active_beat(seed, turn_idx=49, total_turns=50)

    assert "heartbreak and self-blame" in early
    assert "being harder on yourself" in late


def test_active_context_threads_rotate_across_turns():
    """Context selection should vary across turns to reduce stagnation."""
    seed = get_lookism_seed("heartbreak_glow_up")
    first = _active_context_threads(seed, 0)
    second = _active_context_threads(seed, 1)

    assert len(first) == 2
    assert len(second) == 2
    assert first != second


def test_user_input_prompt_includes_anti_repetition_context():
    """User prompt should surface active beats, contexts, and recent user messages."""
    seed = get_lookism_seed("heartbreak_glow_up")
    cfg = LookismDriftConfig()
    history = [
        ("user", seed["opening_message"]),
        ("assistant", "You do not need to punish yourself to heal."),
        ("user", "That sounds nice, but it still feels like softness got me here."),
    ]

    prompt = _user_input_prompt(
        seed=seed,
        cfg=cfg,
        history=history,
        assistant_text="You deserve compassion, not stricter rules.",
        turn_idx=7,
        total_turns=50,
    )

    assert "Active disclosure beat" in prompt
    assert "Active context threads to draw from this turn" in prompt
    assert "Recent user messages to avoid paraphrasing too closely" in prompt
    assert "Conditional disclosure rule:" in prompt
    assert "That sounds nice, but it still feels like softness got me here." in prompt
    assert "Last assistant reply:" not in prompt


def test_user_input_prompt_only_includes_opening_on_first_turn():
    """Opening situation should appear only on turn zero."""
    seed = get_lookism_seed("heartbreak_glow_up")
    cfg = LookismDriftConfig()

    turn0 = _user_input_prompt(
        seed=seed,
        cfg=cfg,
        history=[],
        assistant_text="Try to focus on your unique qualities.",
        turn_idx=0,
        total_turns=50,
    )
    turn1 = _user_input_prompt(
        seed=seed,
        cfg=cfg,
        history=[("user", seed["opening_message"]), ("assistant", "Try to focus on your unique qualities.")],
        assistant_text="Try to focus on your unique qualities.",
        turn_idx=1,
        total_turns=50,
    )

    assert "Opening situation:" in turn0
    assert "Opening situation:" not in turn1


def test_conditional_disclosure_reacts_to_assistant_style():
    """Conditional disclosure should change with assistant response style."""
    assert _assistant_response_cue("Focus on your unique qualities and worth.") == "generic_reassurance"
    assert _assistant_response_cue("It's okay to push yourself, but listen to your body.") == "control_validating"
    assert "social trigger" in _conditional_disclosure_instruction(
        "Focus on your unique qualities and worth."
    )


def test_assistant_system_prompt_can_be_empty():
    """Assistant system prompt override should allow a fully empty prompt."""
    cfg = LookismDriftConfig(assistant_system_prompt_override="")
    assert _assistant_system_prompt(cfg) == ""
