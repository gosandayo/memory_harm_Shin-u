"""Stable paths for the manual red-team package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PACKAGE_ROOT.parent

CONTEXT_PREFIXES_DIR = PACKAGE_ROOT / "context_prefixes"
DOCS_DIR = PACKAGE_ROOT / "docs"
LADDERS_DIR = PACKAGE_ROOT / "ladders"
PORTFOLIO_DIR = PACKAGE_ROOT / "portfolio"
RUNS_DIR = PACKAGE_ROOT / "data" / "runs"
COLD_PROBES_DIR = PACKAGE_ROOT / "data" / "cold_probes"


def resolve_in_package(*parts: str | Path) -> Path:
    """Resolve a path under ``manual_redteam``."""
    return PACKAGE_ROOT.joinpath(*map(Path, parts))


def run_path(run_id: str) -> Path:
    """Return the path for one raw run directory."""
    return RUNS_DIR / run_id


def iter_run_dirs() -> Iterable[Path]:
    """Yield raw run directories in lexical order."""
    if not RUNS_DIR.exists():
        return iter(())
    return (path for path in sorted(RUNS_DIR.iterdir()) if path.is_dir())


def latest_run_dirs(limit: int = 20) -> list[Path]:
    """Return the lexically latest raw run directories."""
    runs = list(iter_run_dirs())
    return runs[-limit:]
