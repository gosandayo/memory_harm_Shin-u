# Manual Red-Team Research Workspace

This directory contains the manual red-team ladder experiments used to study
context-dependent safety failures, confirmation effects, and robustness across
models.

The directory is now split into three surfaces:

- `core/`: importable Python package helpers shared by scripts.
- `scripts/`: legacy command-line runners and analysis utilities.
- `ladders/` and `context_prefixes/`: experiment definitions and reusable prompt
  context.
- `docs/`: research notes, protocol writeups, and result reports.
- `portfolio/`: curated, external-facing entry point.
- `data/runs/`: raw run vault. This is intentionally treated as local/raw
  experiment output, not the public face of the project.

## Package Imports

Use package imports for new reusable code:

```python
from manual_redteam.core.paths import RUNS_DIR, latest_run_dirs
from manual_redteam.core.session_io import load_jsonl, dump_yaml
```

Existing scripts still work as direct files, for example:

```bash
python manual_redteam/scripts/render_session.py --help
```

Over time, script-local helpers should move into `manual_redteam.core`.

## Portfolio Rule

Raw transcripts and agent logs are useful for auditability, but they make the
repository hard to read and can include sensitive red-team content. The rule is:

1. Raw run artifacts stay under `data/runs/<run_id>/`.
2. Each important run gets a short, sanitized summary in `portfolio/RUNS.md`.
3. Public-facing narrative lives in `portfolio/README.md`.
4. Only promote raw artifacts into Git deliberately, with a clear reason.

This keeps the research reproducible without making the raw vault the first
thing a reader has to understand.
