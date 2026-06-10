"""Shared package utilities for manual red-team experiments."""

from .paths import (
    PACKAGE_ROOT,
    REPO_ROOT,
    COLD_PROBES_DIR,
    CONTEXT_PREFIXES_DIR,
    DOCS_DIR,
    LADDERS_DIR,
    PORTFOLIO_DIR,
    RUNS_DIR,
    iter_run_dirs,
    latest_run_dirs,
    resolve_in_package,
    run_path,
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
    "iter_run_dirs",
    "latest_run_dirs",
    "resolve_in_package",
    "run_path",
]
