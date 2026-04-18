"""Unified addon entrypoint for _friend_pack."""

from __future__ import annotations

# Register top-level config window menu action (defensive: never block addon init).
try:
    from .utils.config_window import register_friend_pack_config_menu  # noqa: E402

    register_friend_pack_config_menu()
except Exception:
    pass

# Import both internal addons to register their hooks.
from . import _browser_menu  # noqa: E402,F401
from . import _change_notes  # noqa: E402,F401
