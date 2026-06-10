"""Legacy command scripts for manual red-team experiments.

Prefer importing reusable helpers from ``manual_redteam.core``. These modules
remain script-friendly for direct CLI use.
"""

from __future__ import annotations

import sys

from . import _session_io


# Compatibility for legacy scripts that still say ``from _session_io import``.
# This lets them work under ``python -m manual_redteam.scripts.<script>`` while
# preserving direct execution from the scripts directory.
sys.modules.setdefault("_session_io", _session_io)
