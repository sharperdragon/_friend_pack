# loader.py - reads root config and attaches Browser menu actions
# Last updated: 18-30_11-28

from __future__ import annotations

import importlib
import traceback
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Optional

from aqt.browser import Browser
from aqt.qt import QMenu

from .module_configs import open_find_qids_config
from .menu_utils import add_action

try:
    from ..config_manager import ConfigManager as RootConfigManager
except Exception:
    RootConfigManager = None  # type: ignore[assignment]


# Runtime config keys in root config.json
BROWSER_MENU_SECTION = "browser_menu"
BROWSER_MENU_TOP_MENU_KEY = "top_menu_title"

# Fallback defaults (used if section/keys are absent)
DEFAULT_TOP_MENU_TITLE = "Custom"
LEGACY_FIND_QIDS_SUBMENU_TITLE = "Find QIDs"

ACTION_LABEL_SEARCH_ALL = "Search all"
ACTION_LABEL_SEARCH_ONE_BY_ONE = "Search 1-by-1"
ACTION_LABEL_QID_SEARCH_CONFIG = "QID search settings"

# Debug logging (keep disabled for release builds)
ENABLE_DEBUG_LOGGING = False
DEBUG_LOG_FILENAME = "_browser_menu_debug.log"
DEBUG_TIMESTAMP_FORMAT = "%H-%M_%m-%d"

LEGACY_FIND_QIDS_ACTION_LABELS = frozenset(
    {
        ACTION_LABEL_SEARCH_ALL,
        ACTION_LABEL_SEARCH_ONE_BY_ONE,
        ACTION_LABEL_QID_SEARCH_CONFIG,
    }
)


@dataclass(frozen=True)
class ActionConfig:
    name: str
    module: str
    function: str
    submenu: Optional[str]


# Browser actions are intentionally hardcoded and not loaded from config.
HARDCODED_ACTIONS: tuple[ActionConfig, ...] = (
    ActionConfig(
        name=ACTION_LABEL_SEARCH_ALL,
        submenu=None,
        module="Find_QIDs",
        function="run_search_all_from_browser",
    ),
    ActionConfig(
        name=ACTION_LABEL_SEARCH_ONE_BY_ONE,
        submenu=None,
        module="Find_QIDs",
        function="run_search_one_by_one_from_browser",
    ),
)


def _dbg(msg: str) -> None:
    """
    Append a timestamped debug line to disk when debug logging is enabled.
    """
    if not ENABLE_DEBUG_LOGGING:
        return

    try:
        ts = datetime.now().strftime(DEBUG_TIMESTAMP_FORMAT)
        addon_root = Path(__file__).parent
        log_path = addon_root / DEBUG_LOG_FILENAME
        with log_path.open("a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        # Never let debug logging break menu creation.
        pass


# Helper to load root browser_menu section.
def _load_browser_menu_section() -> dict[str, Any]:
    if RootConfigManager is None:
        return {}
    try:
        section = RootConfigManager.get_section(BROWSER_MENU_SECTION, default={})
    except Exception:
        return {}
    return section if isinstance(section, dict) else {}


# Helper to load the top menu title from root config.json, with fallback.
def _load_top_menu_title() -> str:
    """Load top menu title from root config.json, falling back to default."""
    section = _load_browser_menu_section()
    title = section.get(BROWSER_MENU_TOP_MENU_KEY, DEFAULT_TOP_MENU_TITLE)
    if isinstance(title, str) and title.strip():
        return title.strip()
    return DEFAULT_TOP_MENU_TITLE


def _resolve_addon_package() -> str:
    """
    Resolve the package path for this addon in both layouts:
    - top-level: "_browser_menu"
    - nested: "_friend_pack._browser_menu"
    """
    if __package__:
        return __package__
    return __name__.rsplit(".", 1)[0]


ADDON_PACKAGE = _resolve_addon_package()


def _resolve_callable(browser: Browser, cfg: ActionConfig) -> Optional[Callable[[], None]]:
    """Import the target function and wrap it so it receives the Browser instance."""
    if not cfg.function:
        _dbg(f"_resolve_callable: action '{cfg.name}' has empty function name; skipping")
        return None

    # Determine import path: allow fully-qualified modules or short names.
    # For short names, resolve only within the add-on root package.
    if "." in cfg.module:
        # Treat as a fully-qualified import path, e.g. "_browser_menu.module_configs"
        import_path = cfg.module
    else:
        addon_root = Path(__file__).parent
        root_file = addon_root / f"{cfg.module}.py"
        root_pkg = addon_root / cfg.module / "__init__.py"

        if root_file.exists() or root_pkg.exists():
            import_path = f"{ADDON_PACKAGE}.{cfg.module}"
        else:
            # Keep root-package fallback for compatibility with dynamic module names.
            import_path = f"{ADDON_PACKAGE}.{cfg.module}"
            _dbg(
                f"_resolve_callable: no module file/package found for short module "
                f"'{cfg.module}' under add-on root; trying import '{import_path}'"
            )

    try:
        mod = importlib.import_module(import_path)
    except Exception as e:
        _dbg(
            f"_resolve_callable: import failed for action '{cfg.name}' "
            f"(module={import_path}): {e}\n{traceback.format_exc()}"
        )
        return None

    try:
        target = getattr(mod, cfg.function)
    except AttributeError:
        _dbg(
            f"_resolve_callable: action '{cfg.name}' missing function "
            f"'{cfg.function}' in module '{import_path}'; skipping"
        )
        return None

    # Wrap to ignore the QAction's `checked` argument and inject the Browser.
    def callback(_checked: bool = False, cb=target, b=browser) -> None:
        cb(b)

    return callback


def _menu_action_labels(menu: QMenu) -> set[str]:
    return {a.text() for a in menu.actions()}


def _remove_legacy_find_qids_submenu(top_menu: QMenu) -> None:
    """
    Remove the old "Find QIDs" submenu if it is the legacy container for these actions.
    """
    for act in list(top_menu.actions()):
        submenu = act.menu()
        if submenu is None:
            continue
        if submenu.title() != LEGACY_FIND_QIDS_SUBMENU_TITLE:
            continue
        labels = _menu_action_labels(submenu)
        if labels.intersection(LEGACY_FIND_QIDS_ACTION_LABELS):
            _dbg(
                "load_browser_menu: removing legacy 'Find QIDs' submenu now that "
                "actions are added directly under Custom"
            )
            top_menu.removeAction(act)
            return


def load_browser_menu(browser: Browser) -> None:
    """
    Build Browser custom menu from root config and attach module configs.
    """
    _dbg("load_browser_menu: START")
    actions = list(HARDCODED_ACTIONS)
    top_menu_title = _load_top_menu_title()
    _dbg(f"load_browser_menu: hardcoded actions count = {len(actions)}")

    menu_bar = browser.form.menubar

    # 1) Get or create the top-level "Custom" menu and ALWAYS bind it to browser.form.menu_Custom.
    top_menu = getattr(browser.form, "menu_Custom", None)

    if top_menu is None:
        # No Custom menu registered yet: create one on the menubar.
        top_menu = menu_bar.addMenu(top_menu_title)
        browser.form.menu_Custom = top_menu  # bind for reuse
        _dbg(
            f"load_browser_menu: created browser.form.menu_Custom "
            f"with title = {top_menu.title()}"
        )
    else:
        if top_menu.title() != top_menu_title:
            top_menu.setTitle(top_menu_title)
        # Reuse the existing Custom menu that Anki/another add-on is already using.
        _dbg(
            f"load_browser_menu: reusing browser.form.menu_Custom "
            f"with title = {top_menu.title()}"
        )

    _remove_legacy_find_qids_submenu(top_menu)

    # Helper: get or create a submenu under Custom
    def get_submenu(title: Optional[str]) -> QMenu:
        if not title:
            return top_menu
        for act in top_menu.actions():
            m = act.menu()
            if m is not None and m.title() == title:
                return m
        _dbg(f"load_browser_menu: creating submenu '{title}' under Custom")
        return top_menu.addMenu(title)

    # 2) Build hardcoded actions.
    if actions:
        _dbg("load_browser_menu: entering actions loop")
        for cfg in actions:
            _dbg(
                f"  action: name='{cfg.name}', module='{cfg.module}', "
                f"function='{cfg.function}', submenu='{cfg.submenu}'"
            )

            cb = _resolve_callable(browser, cfg)
            if cb is None:
                _dbg(f"  skipping '{cfg.name}' because callback could not be resolved")
                continue

            parent_menu = get_submenu(cfg.submenu)
            existing_labels = _menu_action_labels(parent_menu)
            if cfg.name in existing_labels:
                _dbg(
                    f"  skipping '{cfg.name}' because it already exists under "
                    f"'{parent_menu.title()}'"
                )
                continue
            add_action(parent_menu, cfg.name, cb)
            _dbg(
                f"  added action '{cfg.name}' under menu '{parent_menu.title()}'"
            )
    else:
        _dbg("load_browser_menu: no actions to process")

    # 3) Attach module config actions that are currently supported.
    existing_labels_top = _menu_action_labels(top_menu)
    if ACTION_LABEL_QID_SEARCH_CONFIG not in existing_labels_top:
        _dbg(
            "load_browser_menu: adding 'QID search settings' directly under "
            "top-level Custom menu"
        )
        add_action(
            top_menu,
            ACTION_LABEL_QID_SEARCH_CONFIG,
            callback=lambda _checked=False, b=browser: open_find_qids_config(b),
        )

    _dbg("load_browser_menu: END")
