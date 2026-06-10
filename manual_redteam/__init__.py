"""Manual red-team experiment package.

The package exposes stable path helpers and shared I/O utilities while the
legacy scripts remain available under ``manual_redteam/scripts``.
"""

from .core.paths import (
    PACKAGE_ROOT,
    REPO_ROOT,
    COLD_PROBES_DIR,
    CONTEXT_PREFIXES_DIR,
    DOCS_DIR,
    LADDERS_DIR,
    PORTFOLIO_DIR,
    RUNS_DIR,
)

__all__ = [
    "PACKAGE_ROOT",
    "REPO_ROOT",
    "COLD_PROBES_DIR",
    "CONTEXT_PREFIXES_DIR",
    "DOCS_DIR",
    "LADDERS_DIR",
    "PORTFOLIO_DIR",
    "RUNS_DIR",
]
