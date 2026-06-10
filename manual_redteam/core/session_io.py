"""Package import path for session I/O helpers.

This is a compatibility facade over the original script-local helper module.
New code should import from ``manual_redteam.core.session_io``. Existing scripts
that run directly can continue importing ``_session_io`` until they are migrated.
"""

from manual_redteam.scripts._session_io import *  # noqa: F401,F403
