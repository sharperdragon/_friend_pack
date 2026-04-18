from __future__ import annotations
from typing import Callable, Optional
from aqt.qt import QAction, QMenu, QMenuBar

# ========== DEBUG IMPORT ==========
try:
    # Reuse the add-on's debug logger from loader.py if available
    from .._browser_menu.loader import _dbg  # type: ignore[attr-defined]
except Exception:
    # Fallback: no-op debug function if loader._dbg is not available yet
    def _dbg(msg: str) -> None:
        return


def _find_menu_by_title(menu_bar: QMenuBar, title: str) -> Optional[QMenu]:
    """Return an existing QMenu from the menubar whose title matches `title`."""
    _dbg(f"menu_utils: _find_menu_by_title search for {title!r}")
    for action in menu_bar.actions():
        menu = action.menu()
        if menu is not None:
            _dbg(f"menu_utils: _find_menu_by_title found candidate {menu.title()!r}")
            if menu.title() == title:
                _dbg(f"menu_utils: _find_menu_by_title matched {title!r}")
                return menu
    _dbg(f"menu_utils: _find_menu_by_title no match for {title!r}")
    return None


def get_or_create_top_menu(menu_bar: QMenuBar, title: str) -> QMenu:
    existing = _find_menu_by_title(menu_bar, title)
    if existing is not None:
        _dbg(f"menu_utils: get_or_create_top_menu reusing existing {title!r}")
        return existing
    _dbg(f"menu_utils: get_or_create_top_menu creating new {title!r}")
    menu = QMenu(title, menu_bar)
    menu_bar.addMenu(menu)
    return menu


def get_or_create_submenu(parent_menu: QMenu, title: str) -> QMenu:
    for action in parent_menu.actions():
        submenu = action.menu()
        if submenu is not None:
            _dbg(
                f"menu_utils: get_or_create_submenu candidate under {parent_menu.title()!r}: "
                f"{submenu.title()!r}"
            )
            if submenu.title() == title:
                _dbg(
                    f"menu_utils: get_or_create_submenu reusing existing submenu {title!r} "
                    f"under {parent_menu.title()!r}"
                )
                return submenu
    _dbg(
        f"menu_utils: get_or_create_submenu creating new submenu {title!r} "
        f"under {parent_menu.title()!r}"
    )
    submenu = QMenu(title, parent_menu)
    parent_menu.addMenu(submenu)
    return submenu


def ensure_menu_path(
    menu_bar: QMenuBar,
    top_menu_title: str,
    submenu_title: Optional[str] = None,
) -> QMenu:
    _dbg(
        f"menu_utils: ensure_menu_path top_menu_title={top_menu_title!r}, "
        f"submenu_title={submenu_title!r}"
    )
    top_menu = get_or_create_top_menu(menu_bar, top_menu_title)

    if submenu_title:
        menu = get_or_create_submenu(top_menu, submenu_title)
        _dbg(
            f"menu_utils: ensure_menu_path returning submenu {menu.title()!r} "
            f"under top {top_menu.title()!r}"
        )
        return menu

    _dbg(f"menu_utils: ensure_menu_path returning top_menu {top_menu.title()!r}")
    return top_menu


def add_action(
    menu: QMenu,
    label: str,
    callback: Callable[[], None],
    *,
    shortcut: Optional[str] = None,
    tooltip: Optional[str] = None,
    checkable: bool = False,
    checked: bool = False,
) -> QAction:
    _dbg(f"menu_utils: add_action label={label!r} to menu={menu.title()!r}")
    action = QAction(label, menu)
    action.triggered.connect(lambda _checked=False, cb=callback: cb())

    if shortcut:
        action.setShortcut(shortcut)

    if tooltip:
        action.setToolTip(tooltip)

    if checkable:
        action.setCheckable(True)
        action.setChecked(checked)

    menu.addAction(action)
    return action


def add_separator(menu: QMenu) -> None:
    """
    Convenience helper to insert a visual separator into a menu.
    """
    _dbg(f"menu_utils: add_separator in menu={menu.title()!r}")
    menu.addSeparator()