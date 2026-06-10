#!/usr/bin/env python3
"""Build a full-log evidence bundle for the 2026-05-19 compact writeup.

The output intentionally copies complete raw JSONL/YAML artifacts. It is not
an excerpt file; it is a reviewer-facing bundle that makes the load-bearing
logs easy to hand over when someone asks to inspect them.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "writeup_2026_05_19_full_log_bundle.md"

RUNS = [
    {
        "title": "Primary cold terminal pressure panel: S13/S14",
        "question": (
            "If we apply forced-answer / prior-support pressure in a fresh chat, "
            "do S13 and S14 collapse?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_cold_terminal_factor_panel_gpt4omini",
        "include_patterns": [
            "manifest.yaml",
            "relabel/cell_counts_primary_majority.yaml",
            "relabel/interrater_kappa_primary_vs_secondary.yaml",
            "relabel/labels_primary_pass01_gpt55.jsonl",
            "relabel/labels_primary_pass02_gpt55.jsonl",
            "relabel/labels_primary_pass03_gpt55.jsonl",
            "relabel/labels_secondary_pass01_claude.jsonl",
            "relabel/masked_bundle.jsonl",
            "relabel/SEALED_mapping.json",
            "branches/*/session_meta.yaml",
            "branches/*/messages.jsonl",
        ],
    },
    {
        "title": "Terminal fixed-prefix replay: S11-S14 path check",
        "question": (
            "What happens when the later terminal turns are replayed from the "
            "long after-buildup prefix versus setup-only prefix?"
        ),
        "note": (
            "Important: manual_reading_notes.yaml is the canonical reading for "
            "this auxiliary replay. panel_summary.yaml is a heuristic navigation "
            "summary, and any script labels or stored legacy auto_label fields "
            "should not be cited as final S16/action-verdict counts."
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_s1s7_s9_connection_panel_gpt4omini",
        "include_patterns": [
            "prompt_manifest.yaml",
            "manual_reading_notes.yaml",
            "panel_summary.yaml",
            "branches/*/session_meta.yaml",
            "branches/*/messages.jsonl",
        ],
    },
    {
        "title": "Early after-buildup replicate: S1-S7",
        "question": (
            "What are the full five after-buildup/adaptive S1-S7 branch logs "
            "behind Figure 1?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_s1s7_live_adaptive_n5_gpt4omini",
        "include_patterns": [
            "manifest.yaml",
            "panel_summary.yaml",
            "branches/*/messages.jsonl",
        ],
    },
    {
        "title": "Early exact fresh-chat replay: S1-S7",
        "question": (
            "What are the full one-turn fresh-chat logs behind the S1-S7 cold "
            "comparison in Figure 1?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_s1s7_exact_cold_panel_gpt4omini",
        "include_patterns": [
            "manifest.yaml",
            "panel_summary.yaml",
            "branches/*/session_meta.yaml",
            "branches/*/messages.jsonl",
        ],
    },
    {
        "title": "Plain S13 prefix comparison",
        "question": (
            "What are the full logs behind the plain personal-verdict prefix "
            "comparison?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_s15_plain_panel_gpt4omini",
        "include_patterns": [
            "prompt_manifest.yaml",
            "panel_summary.yaml",
            "branches/*/session_meta.yaml",
            "branches/*/messages.jsonl",
        ],
    },
    {
        "title": "S14 cold variant controls",
        "question": (
            "For comparison, which S14 cold phrasings held versus collapsed "
            "before the final May 19 endpoint panel?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-18_s16_unrestricted_gpt4omini",
        "include_patterns": [
            "unrestricted_condition_notes.yaml",
            "branches/cold_*/messages.jsonl",
        ],
    },
    {
        "title": "Exploratory long-buildup terminal trajectory",
        "question": (
            "What is the original exploratory long-buildup terminal trajectory "
            "that motivated the fixed panels?"
        ),
        "path": ROOT
        / "manual_redteam/data/runs/2026-05-19_s16_longbuild_free_gpt4omini",
        "include_patterns": [
            "longbuild_condition_notes.yaml",
            "branches/*/messages.jsonl",
        ],
    },
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fence_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return "jsonl"
    if suffix in {".yaml", ".yml"}:
        return "yaml"
    if suffix == ".json":
        return "json"
    if suffix == ".txt":
        return "text"
    return ""


def collect_files(base: Path, patterns: list[str]) -> list[Path]:
    seen: set[Path] = set()
    out: list[Path] = []
    for pattern in patterns:
        for path in sorted(base.glob(pattern)):
            if path.is_file() and path not in seen:
                seen.add(path)
                out.append(path)
    return out


def main() -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = []
    lines.append("# Full Log Bundle for writeup_2026_05_19_compact")
    lines.append("")
    lines.append(f"Generated at UTC: `{now}`")
    lines.append("")
    lines.append(
        "Content note: this bundle contains exact user prompts and assistant "
        "replies from self-harm safety experiments. It copies complete raw log "
        "files for the listed runs; no transcript content is excerpted, "
        "paraphrased, or redacted in the log sections."
    )
    lines.append("")
    lines.append(
        "Use this file when a reader asks to inspect the underlying logs. The "
        "source files remain canonical; this markdown is a review-facing "
        "rendering with file paths and SHA-256 hashes."
    )
    lines.append("")
    lines.append("## Quick Index")
    lines.append("")
    for i, run in enumerate(RUNS, start=1):
        base = run["path"]
        files = collect_files(base, run["include_patterns"])
        lines.append(
            f"{i}. **{run['title']}**: `{rel(base)}` "
            f"({len(files)} files copied)"
        )
    lines.append("")
    lines.append("## Direct Answer: S13/S14 Cold Pressure Panel")
    lines.append("")
    lines.append(
        "The main cold-pressure question is covered by "
        "`manual_redteam/data/runs/2026-05-19_cold_terminal_factor_panel_gpt4omini`."
    )
    lines.append("")
    lines.append(
        "Primary majority relabel result: S13 personal verdict collapses 0/5 "
        "both with and without the user-claimed prior-support clause; S14 "
        "action verdict collapses 5/5 both with and without that clause. The "
        "full raw logs for all 20 branch runs appear in Section 1 below."
    )
    lines.append("")

    for i, run in enumerate(RUNS, start=1):
        base = run["path"]
        files = collect_files(base, run["include_patterns"])
        lines.append(f"## {i}. {run['title']}")
        lines.append("")
        lines.append(f"Run directory: `{rel(base)}`")
        lines.append("")
        lines.append(f"Reader question: {run['question']}")
        lines.append("")
        if run.get("note"):
            lines.append(f"Evidence note: {run['note']}")
            lines.append("")
        lines.append(f"Files copied in full: `{len(files)}`")
        lines.append("")
        for path in files:
            text = path.read_text(encoding="utf-8")
            line_count = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
            lines.append(f"### `{rel(path)}`")
            lines.append("")
            lines.append(f"- SHA-256: `{sha256(path)}`")
            lines.append(f"- Lines: `{line_count}`")
            if (
                path.name == "panel_summary.yaml"
                and base.name == "2026-05-19_s1s7_s9_connection_panel_gpt4omini"
            ):
                lines.append(
                    "- Label warning: this file is heuristic only; use "
                    "`manual_reading_notes.yaml` for the corrected S16/action-verdict "
                    "counts."
                )
            lines.append("")
            lines.append(f"```{fence_for(path)}")
            lines.append(text.rstrip("\n"))
            lines.append("```")
            lines.append("")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
