"""Unified addon entrypoint for _friend_pack."""

from __future__ import annotations

try:
    from aqt import mw  # type: ignore
except Exception:
    mw = None  # type: ignore[assignment]

# Register top-level config window menu action (defensive: never block addon init).
try:
    from .utils.config_window import (  # noqa: E402
        open_friend_pack_config_window,
        register_friend_pack_config_menu,
    )

    register_friend_pack_config_menu()

    # Wire Anki's Add-ons -> Config button to this add-on's custom config dialog.
    try:
        if (
            mw is not None
            and hasattr(mw, "addonManager")
            and hasattr(mw.addonManager, "setConfigAction")
        ):
            mw.addonManager.setConfigAction(
                __name__,
                lambda: open_friend_pack_config_window(mw),
            )
    except Exception:
        pass
except Exception:
    pass

# Import both internal addons to register their hooks.
from . import _browser_menu  # noqa: E402,F401
from . import _change_notes  # noqa: E402,F401
