#!/usr/bin/env python3
"""Build a focused bundle for S14 fresh-chat/cold collapse logs."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "manual_redteam/data/runs/2026-05-19_cold_terminal_factor_panel_gpt4omini"
OUT = ROOT / "docs/writeup_2026_05_19_s14_fresh_collapse_logs.md"


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> None:
    files = sorted((BASE / "branches").glob("S14_cold_forced_only_run*/messages.jsonl"))
    files += sorted((BASE / "branches").glob("S14_cold_forced_ctxclaim_run*/messages.jsonl"))

    lines: list[str] = [
        "# S14 Fresh-Chat Collapse Logs",
        "",
        f"Generated at UTC: `{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}`",
        "",
        "Content note: exact self-harm-related user prompts and assistant replies are included below as raw logs.",
        "",
        f"Source run: `{rel(BASE)}`",
        "",
        "Scope: only S14 fresh-chat/cold endpoint runs where the action-verdict endpoint collapsed from a new chat.",
        "",
        "Relabel summary from `relabel/cell_counts_primary_majority.yaml`:",
        "",
        "```yaml",
        "S14_cold_forced_only:",
        "  N: 5",
        "  collapse_count: 5",
        "  collapse_rate: 5/5",
        "  label_dist:",
        "    CLEAN_COLLAPSE: 5",
        "S14_cold_forced_ctxclaim:",
        "  N: 5",
        "  collapse_count: 5",
        "  collapse_rate: 5/5",
        "  label_dist:",
        "    CLEAN_COLLAPSE: 5",
        "```",
        "",
    ]

    for path in files:
        text = path.read_text(encoding="utf-8")
        lines.extend(
            [
                f"## `{rel(path)}`",
                "",
                f"- SHA-256: `{sha256_text(text)}`",
                "- Full raw `messages.jsonl` follows.",
                "",
                "```jsonl",
                text.rstrip("\n"),
                "```",
                "",
            ]
        )

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
