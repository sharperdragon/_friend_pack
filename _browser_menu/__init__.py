# __init__.py - entrypoint for the _browser_menu add-on
# Last updated: 18-30_11-27

from __future__ import annotations

import traceback

from aqt import gui_hooks, mw
from aqt.browser import Browser
from aqt.utils import showText

# =========================
# Compatibility constants
# =========================
BROWSER_MENUS_INIT_HOOK_NAME = "browser_menus_did_init"
BROWSER_MENUS_INIT_GUARD_ATTR = "_friend_pack_browser_menu_hook_registered"


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


def _register_browser_menu_hook() -> bool:
    """
    Register Browser menu hook when available.
    Gracefully skip on older Anki versions where this hook may not exist.
    """
    hook = getattr(gui_hooks, BROWSER_MENUS_INIT_HOOK_NAME, None)
    if hook is None or not hasattr(hook, "append"):
        _dbg(
            f"init: hook '{BROWSER_MENUS_INIT_HOOK_NAME}' not available; "
            "skipping _browser_menu registration"
        )
        return False

    if mw is not None and getattr(mw, BROWSER_MENUS_INIT_GUARD_ATTR, False):
        _dbg("init: browser menu hook already registered")
        return True

    try:
        hook.append(_on_browser_menus_did_init)
        if mw is not None:
            setattr(mw, BROWSER_MENUS_INIT_GUARD_ATTR, True)
        _dbg("init: browser menu hook registered")
        return True
    except Exception:
        _dbg("init: browser menu hook registration failed\n" + traceback.format_exc())
        return False


# * Register hook so the custom menu is created whenever a Browser's menus are initialized.
_register_browser_menu_hook()
