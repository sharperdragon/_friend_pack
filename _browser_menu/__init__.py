# __init__.py - entrypoint for the _browser_menu add-on
# Last updated: 18-30_11-27

from __future__ import annotations

import traceback

from aqt import gui_hooks
from aqt.browser import Browser
from aqt.utils import showText

# ! Try to import the debug helper _dbg from loader; fall back to a no-op if missing.
try:
    from .loader import load_browser_menu, _dbg
except Exception:
    from .loader import load_browser_menu

    def _dbg(msg: str) -> None:
        # ? Fallback debug function: do nothing if _dbg is not defined in loader.
        return


def _on_browser_menus_did_init(browser: Browser) -> None:
    """Build the Browser's custom menu from root config for this Browser instance."""
    _dbg("init: _on_browser_menus_did_init START")
    try:
        load_browser_menu(browser)
        _dbg("init: _on_browser_menus_did_init END (success)")
    except Exception:
        _dbg("init: _on_browser_menus_did_init ERROR\n" + traceback.format_exc())
        showText(
            "[_browser_menu] Failed to initialize Browser menu:\n\n"
            + traceback.format_exc(),
            type="text",
        )


# * Register hook so the custom menu is created whenever a Browser's menus are initialized.
gui_hooks.browser_menus_did_init.append(_on_browser_menus_did_init)
