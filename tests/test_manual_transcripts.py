"""Tests for manual transcript rendering and persistence."""

import json

from src.manual_transcripts import render_transcript, save_bundle


def _sample_bundle() -> dict:
    return {
        "candidate": {
            "id": "sample_manual_case",
            "scenario": "therapy",
            "title": "Sample case",
        },
        "config": {
            "prompt_version": "test_prompt",
            "assistant_model": "gpt-4o-mini",
            "assistant_temperature": 0.7,
        },
        "turns": [
            {
                "turn": 0,
                "user_msg": "I feel stuck.",
                "assistant_text": "That sounds hard.",
            }
        ],
        "judgment": {
            "lead_to_safety_problem": None,
            "first_unsafe_turn": None,
            "failure_mode": "",
            "notes": "",
        },
    }


def test_render_transcript_uses_role_icons():
    """Rendered transcript should visibly separate user and assistant turns."""
    rendered = render_transcript(_sample_bundle())

    assert "🧑 User" in rendered
    assert "I feel stuck." in rendered
    assert "🤖 Assistant" in rendered
    assert "That sounds hard." in rendered


def test_save_bundle_writes_json_and_text_transcript(tmp_path):
    """Saving should create both machine-readable JSON and readable text output."""
    bundle = _sample_bundle()

    json_path = save_bundle(bundle, tmp_path)
    text_path = json_path.with_suffix(".txt")

    saved_bundle = json.loads(json_path.read_text(encoding="utf-8"))
    saved_text = text_path.read_text(encoding="utf-8")

    assert saved_bundle["candidate"]["id"] == "sample_manual_case"
    assert "🧑 User" in saved_text
    assert "🤖 Assistant" in saved_text
