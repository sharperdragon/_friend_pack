"""Portable _change_notes_shua addon: missed/custom tags only."""

from aqt import gui_hooks, mw
from aqt.browser import Browser
from aqt.qt import QMenu

from .add_custom_tags import add_custom_tag_menu_items
from . import add_missed_tags as missed_tags_module

CUSTOM_TAGS_MENU_LABEL = "Custom Tags"
TRUE_LEARN_RESOURCE_LABEL = "True-Learn"


def add_limited_missed_tag_menu_items(browser, menu):
    """Render only the six allowed Missed Tags actions for the export addon."""
    missed_tags_module._reload_runtime_config()

    tag_menu = QMenu(missed_tags_module.MISSED_TAGS_MENU_LABEL, browser)
    tag_menu.setStyleSheet(
        """
        QMenu::item {
            padding-top: 4.5px;
            padding-bottom: 4.5px;
            padding-left: 6px;
            padding-right: 6px;
        }
        QMenu::item:selected {
            background-color: rgba(120, 160, 255, 60);
        }
    """
    )

    missed_tags_module.add_uworld_tags(browser, tag_menu)
    missed_tags_module.add_amboss_tag(browser, tag_menu)
    missed_tags_module.add_base_plain_action(browser, tag_menu)
    missed_tags_module.add_multi_tag(browser, tag_menu)
    missed_tags_module.add_correct_guess_action(browser, tag_menu)

    original_resources = list(missed_tags_module.OTHER_RESOURCES)
    try:
        missed_tags_module.OTHER_RESOURCES = [TRUE_LEARN_RESOURCE_LABEL]
        missed_tags_module.add_other_resources_actions(browser, tag_menu)
    finally:
        missed_tags_module.OTHER_RESOURCES = original_resources

    if tag_menu.actions():
        menu.addSeparator()
        menu.addMenu(tag_menu)


def on_browser_will_show_context_menu(browser: Browser, menu):
    if not browser.selectedNotes():
        return

    add_limited_missed_tag_menu_items(browser, menu)
    add_custom_tag_menu_items(browser, menu, menu_label=CUSTOM_TAGS_MENU_LABEL)


if not getattr(mw, "_change_notes_shua_menu_injected", False):
    gui_hooks.browser_will_show_context_menu.append(on_browser_will_show_context_menu)
    mw._change_notes_shua_menu_injected = True
