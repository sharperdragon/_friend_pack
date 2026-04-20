"""Portable _change_notes_shua addon: missed/custom tags only."""

from aqt import gui_hooks, mw
from aqt.browser import Browser
from aqt.qt import QMenu

from .add_custom_tags import add_custom_tag_menu_items
from . import add_missed_tags as missed_tags_module
from ..utils.menu_styles import (
    build_context_submenu_arrow_stylesheet,
    build_missed_tags_menu_stylesheet,
)


def _apply_stylesheet_block(menu: QMenu, stylesheet_block: str) -> None:
    block = stylesheet_block.strip()
    if not block:
        return

    current_stylesheet = (menu.styleSheet() or "").strip()
    if block in current_stylesheet:
        return

    if current_stylesheet:
        menu.setStyleSheet(f"{current_stylesheet}\n{block}".strip())
    else:
        menu.setStyleSheet(block)


def add_limited_missed_tag_menu_items(browser, menu):
    """Render the limited Missed Tags actions for the export addon."""
    missed_tags_module._reload_runtime_config()

    tag_menu = QMenu(missed_tags_module.MISSED_TAGS_MENU_LABEL, browser)
    _apply_stylesheet_block(tag_menu, build_missed_tags_menu_stylesheet())

    missed_tags_module.add_uworld_tags(browser, tag_menu)
    missed_tags_module.add_nbme_tag(browser, tag_menu)
    missed_tags_module.add_amboss_tag(browser, tag_menu)
    missed_tags_module.add_base_plain_action(browser, tag_menu)
    missed_tags_module.add_multi_tag(browser, tag_menu)
    missed_tags_module.add_correct_guess_action(browser, tag_menu)

    missed_tags_module.add_other_resources_actions(browser, tag_menu)

    if tag_menu.actions():
        menu.addSeparator()
        menu.addMenu(tag_menu)


def on_browser_will_show_context_menu(browser: Browser, menu):
    if not browser.selectedNotes():
        return

    _apply_stylesheet_block(menu, build_context_submenu_arrow_stylesheet())

    add_limited_missed_tag_menu_items(browser, menu)
    add_custom_tag_menu_items(browser, menu)


if not getattr(mw, "_change_notes_shua_menu_injected", False):
    gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)
    mw._change_notes_shua_menu_injected = True
