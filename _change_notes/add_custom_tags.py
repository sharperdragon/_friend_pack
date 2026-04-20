# pyright: reportMissingImports=false
from __future__ import annotations

from typing import Any, TypedDict

from aqt.qt import QAction, QMenu
from aqt.utils import showInfo, tooltip

from ..menu_styles import build_custom_tags_menu_stylesheet
from ..utils.config_manager import ConfigManager

# ! ----------------------------- CONFIG SECTION -----------------------------
CONFIG_SECTION = "add_custom_tags"
# ! ------------------------------------------------------------------------

# ! --------------------------- USER-TUNABLE DEFAULTS ---------------------------
DEFAULT_SUBMENU_LABEL = "Custom Tags"
DEFAULT_MSG_NO_NOTES_SELECTED = "No notes selected."
DEFAULT_MSG_APPLIED_TEMPLATE = "Applied {tag_count} tag(s) to {note_count} notes."
# ! -----------------------------------------------------------------------------

# ! --------------------------- OPTIONAL CONFIG KEYS ---------------------------
CONFIG_KEY_SUBMENU_LABEL = "submenu_label"
CONFIG_KEY_PRESETS = "presets"
# ! -----------------------------------------------------------------------------


class TagPreset(TypedDict):
    menu_label: str
    tags: list[str]


def _to_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []

    if isinstance(value, list):
        out = [str(v).strip() for v in value if str(v).strip()]
        return out

    return []


def _normalize_presets(raw: Any) -> list[TagPreset]:
    if not isinstance(raw, list):
        return []

    normalized: list[TagPreset] = []
    for preset in raw:
        if not isinstance(preset, dict):
            continue

        menu_label = str(preset.get("menu_label", preset.get("label", ""))).strip()
        tags = _to_string_list(preset.get("tags", []))
        if not menu_label or not tags:
            continue

        normalized.append({"menu_label": menu_label, "tags": tags})

    return normalized


def _load_runtime_config(
    menu_label_override: str | None = None,
) -> tuple[str, list[TagPreset], str, str]:
    section_cfg = ConfigManager.get_section(CONFIG_SECTION, default={})
    if not isinstance(section_cfg, dict):
        section_cfg = {}

    configured_submenu_label = str(section_cfg.get(CONFIG_KEY_SUBMENU_LABEL, "")).strip()
    if isinstance(menu_label_override, str) and menu_label_override.strip():
        submenu_label = menu_label_override.strip()
    elif configured_submenu_label:
        submenu_label = configured_submenu_label
    else:
        submenu_label = DEFAULT_SUBMENU_LABEL

    # Hardcoded by request: do not read these from config.
    msg_no_notes_selected = DEFAULT_MSG_NO_NOTES_SELECTED
    msg_applied_template = DEFAULT_MSG_APPLIED_TEMPLATE

    # Presets come from config only; no hardcoded fallback presets.
    presets = _normalize_presets(section_cfg.get(CONFIG_KEY_PRESETS, []))

    return submenu_label, presets, msg_no_notes_selected, msg_applied_template


def _add_tag_safe(note, tag: str):
    if hasattr(note, "add_tag"):
        note.add_tag(tag)
    else:
        note.addTag(tag)


def _save_note_safe(col, note):
    try:
        col.update_note(note)
    except Exception:
        note.flush()


def _apply_tags_to_selected_notes(
    browser,
    tags: list[str],
    *,
    msg_no_notes_selected: str,
    msg_applied_template: str,
):
    nids = browser.selectedNotes()
    if not nids:
        showInfo(msg_no_notes_selected)
        return

    # Deduplicate while preserving order
    final_tags: list[str] = []
    seen = set()
    for tag in tags:
        if tag and tag not in seen:
            seen.add(tag)
            final_tags.append(tag)

    if not final_tags:
        return

    col = browser.mw.col
    for nid in nids:
        note = col.get_note(nid)
        current_tags = set(note.tags)
        for tag in final_tags:
            if tag not in current_tags:
                _add_tag_safe(note, tag)
        _save_note_safe(col, note)

    browser.model.reset()
    tooltip(msg_applied_template.format(tag_count=len(final_tags), note_count=len(nids)))


def add_custom_tag_menu_items(
    browser,
    parent_menu,
    *,
    menu_label: str | None = None,
):
    submenu_label, presets, msg_no_notes_selected, msg_applied_template = _load_runtime_config(
        menu_label_override=menu_label
    )
    if not presets:
        return

    custom_menu = QMenu(submenu_label, browser)
    custom_menu_stylesheet = build_custom_tags_menu_stylesheet()
    if custom_menu_stylesheet:
        custom_menu.setStyleSheet(custom_menu_stylesheet)

    for preset in presets:
        menu_label = preset["menu_label"]
        tags = list(preset["tags"])

        action = QAction(menu_label, browser)
        action.triggered.connect(
            lambda _=None, preset_tags=tags: _apply_tags_to_selected_notes(
                browser,
                preset_tags,
                msg_no_notes_selected=msg_no_notes_selected,
                msg_applied_template=msg_applied_template,
            )
        )
        custom_menu.addAction(action)

    if custom_menu.actions():
        parent_menu.addSeparator()
        parent_menu.addMenu(custom_menu)
