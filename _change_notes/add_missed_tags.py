# pyright: reportMissingImports=false
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from aqt.qt import QAction, QInputDialog, QMenu
from aqt.utils import showInfo, tooltip

from .config_manager import ConfigManager

# ! ----------------------------- CONFIG SECTIONS -----------------------------
CONFIG_SECTION = "add_missed_tags"
LEGACY_CONFIG_SECTION = "tag_selected_notes_config"
LEGACY_MODULE_CONFIG_SECTION = "add_tags"
LEGACY_CONFIG_SECTIONS = [
    LEGACY_CONFIG_SECTION,
    LEGACY_MODULE_CONFIG_SECTION,
]
# ! -------------------------------------------------------------------------

# ! ----------------------------- USER-TUNABLE CONSTANTS -----------------------------
# ? Base/scaffold defaults
DEFAULT_BASE_MISSED_TAGS = ["##Missed-Qs"]
DEFAULT_Q_BANKS = ["UWORLD", "NBME", "AMBOSS"]
DEFAULT_TEST_TAG_PREFIX = "UW_Tests"
DEFAULT_NBME_TAG_PREFIX = "NBME"
DEFAULT_MULTI_MISS_TAG = "2x"
DEFAULT_OTHER_SUFFIX = "Other"

# ? Action defaults
DEFAULT_UWORLD_LABEL = "🛃UWorld"
DEFAULT_UWORLD_BASE_TAGS = ["##Missed-Qs::UW_Tests"]
DEFAULT_NBME_LABEL = "🧠 NBME"
DEFAULT_NBME_BASE_TAGS = ["##Missed-Qs::NBME"]
DEFAULT_AMBOSS_LABEL = "🦠 Amboss"
DEFAULT_AMBOSS_BASE_TAG = "##Missed-Qs::Amboss"
DEFAULT_OTHER_RESOURCES = ["Kaplan", "True-Learn", "NBOME"]
DEFAULT_KEY_TAG_BASE = "#Custom::#KEY"
DEFAULT_CORRECT_GUESS_TAGS = ["#Custom::correct_marked"]
DEFAULT_TEST_RANGE_BLOCK_SIZE = 25

# ? Prompt/format behavior
PROMPT_BEHAVIOR_BASE_ONLY = "base_only"
PROMPT_STYLE_RANGE_THEN_NUMBER = "range_then_number"
PROMPT_STYLE_NUMBER_ONLY = "number_only"

# ? Hardcoded UI messages (intentionally not configurable)
DEFAULT_MISSED_TAGS_MENU_LABEL = "Missed Tags ❌"
DEFAULT_MSG_NO_NOTES_SELECTED = "❌ No notes selected."
DEFAULT_MSG_INVALID_TEST_NUMBER = "❌ Please enter a valid integer test number."
DEFAULT_ACTION_LABEL_BASE = "♦️Base"
DEFAULT_ACTION_LABEL_MULTI_MISSED = "2x Missed 📌"
DEFAULT_ACTION_LABEL_KEY_INFO = "Key Info 🗝️"
DEFAULT_ACTION_LABEL_CORRECT_GUESS = "Guessed Correct 🎫"
DEFAULT_PROMPT_TITLE_GENERIC = "Enter Test Number"
DEFAULT_PROMPT_LABEL_GENERIC = "Test #:"

PROMPT_TITLE_UWORLD = "Enter UWorld Test Number"
PROMPT_TITLE_NBME_FORM = "Enter NBME Form"
PROMPT_LABEL_NBME_FORM = "Form #:"
PROMPT_TITLE_AMBOSS = "Enter Amboss Test Number"
PROMPT_TITLE_TRUE_LEARN = "Enter True-Learn Test Number"

# ? Runtime state (reloaded from config)
MISSED_BASE_TAG = list(DEFAULT_BASE_MISSED_TAGS)
ENABLED_Q_BANKS = {bank.upper() for bank in DEFAULT_Q_BANKS}

SUBSET_1_NAME = DEFAULT_UWORLD_LABEL
SUBSET_1_TAG = list(DEFAULT_UWORLD_BASE_TAGS)
SUBSET_2_NAME = DEFAULT_NBME_LABEL
SUBSET_2_TAG = list(DEFAULT_NBME_BASE_TAGS)

AMBOSS_TOP_LEVEL_NAME = DEFAULT_AMBOSS_LABEL
AMBOSS_BASE_TAG = DEFAULT_AMBOSS_BASE_TAG
AMBOSS_BLANK_BEHAVIOR = PROMPT_BEHAVIOR_BASE_ONLY
AMBOSS_NUMBER_STYLE = PROMPT_STYLE_NUMBER_ONLY
AMBOSS_REMOVE_FROM_OTHER_MENU = True

MULTI_MISS_TAG = DEFAULT_MULTI_MISS_TAG
OTHER_SUFFIX = DEFAULT_OTHER_SUFFIX
OTHER_RESOURCES = list(DEFAULT_OTHER_RESOURCES)
KEY_TAG_BASE = DEFAULT_KEY_TAG_BASE
CORRECT_GUESS_TAGS = list(DEFAULT_CORRECT_GUESS_TAGS)
TEST_RANGE_BLOCK_SIZE = DEFAULT_TEST_RANGE_BLOCK_SIZE
DEFAULT_NBME_TAG_PREFIX_RUNTIME = DEFAULT_NBME_TAG_PREFIX
DEFAULT_TEST_TAG_PREFIX_RUNTIME = DEFAULT_TEST_TAG_PREFIX

MISSED_TAGS_MENU_LABEL = DEFAULT_MISSED_TAGS_MENU_LABEL
MSG_NO_NOTES_SELECTED = DEFAULT_MSG_NO_NOTES_SELECTED
MSG_INVALID_TEST_NUMBER = DEFAULT_MSG_INVALID_TEST_NUMBER
ACTION_LABEL_BASE = DEFAULT_ACTION_LABEL_BASE
ACTION_LABEL_MULTI_MISSED = DEFAULT_ACTION_LABEL_MULTI_MISSED
ACTION_LABEL_KEY_INFO = DEFAULT_ACTION_LABEL_KEY_INFO
ACTION_LABEL_CORRECT_GUESS = DEFAULT_ACTION_LABEL_CORRECT_GUESS
PROMPT_TITLE_GENERIC = DEFAULT_PROMPT_TITLE_GENERIC
PROMPT_LABEL_GENERIC = DEFAULT_PROMPT_LABEL_GENERIC

# ? Action keys
ACTION_KEY_BASE_PLAIN = "base_plain"
ACTION_KEY_KEY_INFO = "add_key_info_action"
ACTION_KEY_CORRECT_GUESS = "correct_guess"
ACTION_KEY_NBME_FORM_PROMPT = "nbme_form_prompt"
ACTION_KEY_UWORLD_TEST_PROMPT = "uw_test_prompt"
ACTION_KEY_AMBOSS_TEST_PROMPT = "amboss_test_prompt"
ACTION_KEY_TRUE_LEARN_TEST_PROMPT = "true_learn_test_prompt"
ACTION_KEY_OTHER_RESOURCE = "other_resource"

# ? Exclude list for auto-month context
EXCLUDE_AUTO_MISS = [
    ACTION_KEY_KEY_INFO,
    ACTION_KEY_BASE_PLAIN,
    ACTION_KEY_CORRECT_GUESS,
]
# ! -------------------------------------------------------------------------


# $ Compose a full Missed-Qs tag path with the base prefix
def base_tag_path(*parts: str) -> str:
    base = MISSED_BASE_TAG[0] if MISSED_BASE_TAG else DEFAULT_BASE_MISSED_TAGS[0]
    return "::".join([base, *[part for part in parts if part]])


def _to_string_list(value: Any, fallback: list[str]) -> list[str]:
    if isinstance(value, list):
        out = [str(v).strip() for v in value if str(v).strip()]
        return out or list(fallback)
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return list(fallback)


def _to_text(value: Any, fallback: str) -> str:
    text = str(value).strip()
    return text or fallback


def _to_optional_text(value: Any) -> str:
    text = str(value).strip()
    return text


def _to_bool(value: Any, fallback: bool) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    return fallback


def _to_positive_int(value: Any, fallback: int) -> int:
    try:
        parsed = int(str(value).strip())
    except Exception:
        return fallback
    return parsed if parsed > 0 else fallback


def _normalize_q_banks(raw: Any, fallback: list[str]) -> set[str]:
    if isinstance(raw, list):
        values = [str(v).strip().upper() for v in raw if str(v).strip()]
        return set(values)

    if isinstance(raw, str) and raw.strip():
        values = [chunk.strip().upper() for chunk in raw.split(",") if chunk.strip()]
        return set(values)

    return {str(v).strip().upper() for v in fallback if str(v).strip()}


def _is_bank_enabled(bank_name: str) -> bool:
    return bank_name.strip().upper() in ENABLED_Q_BANKS


def scrub_resource_label_to_tag(label: str) -> str:
    cleaned = str(label).strip()
    cleaned = re.sub(r"[^A-Za-z0-9\- ]+", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _uw_base_tag() -> str:
    for cand in SUBSET_1_TAG + SUBSET_2_TAG:
        if "UW_Base" in cand or "::UW" in cand:
            return cand
    return base_tag_path(DEFAULT_TEST_TAG_PREFIX_RUNTIME)


def _nbme_base_tag() -> str:
    for cand in SUBSET_2_TAG + SUBSET_1_TAG:
        upper_cand = cand.upper()
        if "::NBME" in upper_cand or "NBME_BASE" in upper_cand:
            return cand
    return base_tag_path(DEFAULT_NBME_TAG_PREFIX_RUNTIME)


def _reload_runtime_config() -> None:
    global MISSED_BASE_TAG
    global ENABLED_Q_BANKS
    global SUBSET_1_NAME
    global SUBSET_1_TAG
    global SUBSET_2_NAME
    global SUBSET_2_TAG
    global AMBOSS_TOP_LEVEL_NAME
    global AMBOSS_BASE_TAG
    global AMBOSS_BLANK_BEHAVIOR
    global AMBOSS_NUMBER_STYLE
    global AMBOSS_REMOVE_FROM_OTHER_MENU
    global MULTI_MISS_TAG
    global OTHER_SUFFIX
    global OTHER_RESOURCES
    global KEY_TAG_BASE
    global CORRECT_GUESS_TAGS
    global TEST_RANGE_BLOCK_SIZE
    global DEFAULT_NBME_TAG_PREFIX_RUNTIME
    global DEFAULT_TEST_TAG_PREFIX_RUNTIME
    global MISSED_TAGS_MENU_LABEL
    global MSG_NO_NOTES_SELECTED
    global MSG_INVALID_TEST_NUMBER
    global ACTION_LABEL_BASE
    global ACTION_LABEL_MULTI_MISSED
    global ACTION_LABEL_KEY_INFO
    global ACTION_LABEL_CORRECT_GUESS
    global PROMPT_TITLE_GENERIC
    global PROMPT_LABEL_GENERIC

    legacy_cfg: dict[str, Any] = {}
    for section_name in LEGACY_CONFIG_SECTIONS:
        section_data = ConfigManager(section_name).load()
        if isinstance(section_data, dict):
            legacy_cfg = ConfigManager.deep_merge_dicts(legacy_cfg, section_data)

    section_cfg = ConfigManager(CONFIG_SECTION).load()
    merged_cfg = ConfigManager.deep_merge_dicts(
        legacy_cfg,
        section_cfg if isinstance(section_cfg, dict) else {},
    )

    defaults_cfg = merged_cfg.get("defaults", {})
    if not isinstance(defaults_cfg, dict):
        defaults_cfg = {}

    ui_cfg = merged_cfg.get("ui", {})
    if not isinstance(ui_cfg, dict):
        ui_cfg = {}

    actions_cfg = merged_cfg.get("actions", {})
    if not isinstance(actions_cfg, dict):
        actions_cfg = {}

    base_cfg = actions_cfg.get("base", {})
    if not isinstance(base_cfg, dict):
        base_cfg = {}

    uworld_cfg = actions_cfg.get("uworld", {})
    if not isinstance(uworld_cfg, dict):
        uworld_cfg = {}

    nbme_cfg = actions_cfg.get("nbme", {})
    if not isinstance(nbme_cfg, dict):
        nbme_cfg = {}

    amboss_cfg = actions_cfg.get("amboss", {})
    if not isinstance(amboss_cfg, dict):
        amboss_cfg = {}

    multi_missed_cfg = actions_cfg.get("multi_missed", {})
    if not isinstance(multi_missed_cfg, dict):
        multi_missed_cfg = {}

    key_info_cfg = actions_cfg.get("key_info", {})
    if not isinstance(key_info_cfg, dict):
        key_info_cfg = {}

    correct_guess_cfg = actions_cfg.get("correct_guess", {})
    if not isinstance(correct_guess_cfg, dict):
        correct_guess_cfg = {}

    other_cfg = actions_cfg.get("other", {})
    if not isinstance(other_cfg, dict):
        other_cfg = {}

    # Menu label:
    # - Canonical: defaults.menu_label
    # - Compat alias: ui.menu_label (wins when explicitly set)
    defaults_menu_label = _to_text(
        defaults_cfg.get("menu_label", DEFAULT_MISSED_TAGS_MENU_LABEL),
        DEFAULT_MISSED_TAGS_MENU_LABEL,
    )
    ui_menu_label = _to_optional_text(ui_cfg.get("menu_label", merged_cfg.get("menu_label", "")))
    MISSED_TAGS_MENU_LABEL = ui_menu_label or defaults_menu_label

    # Hardcoded by request: these remain code-only constants.
    MSG_NO_NOTES_SELECTED = DEFAULT_MSG_NO_NOTES_SELECTED
    MSG_INVALID_TEST_NUMBER = DEFAULT_MSG_INVALID_TEST_NUMBER

    ACTION_LABEL_BASE = _to_text(
        base_cfg.get("label", ui_cfg.get("action_label_base", DEFAULT_ACTION_LABEL_BASE)),
        DEFAULT_ACTION_LABEL_BASE,
    )
    ACTION_LABEL_MULTI_MISSED = _to_text(
        multi_missed_cfg.get(
            "label",
            ui_cfg.get("action_label_multi_missed", DEFAULT_ACTION_LABEL_MULTI_MISSED),
        ),
        DEFAULT_ACTION_LABEL_MULTI_MISSED,
    )
    ACTION_LABEL_KEY_INFO = _to_text(
        key_info_cfg.get("label", ui_cfg.get("action_label_key_info", DEFAULT_ACTION_LABEL_KEY_INFO)),
        DEFAULT_ACTION_LABEL_KEY_INFO,
    )
    ACTION_LABEL_CORRECT_GUESS = _to_text(
        correct_guess_cfg.get(
            "label",
            ui_cfg.get("action_label_correct_guess", DEFAULT_ACTION_LABEL_CORRECT_GUESS),
        ),
        DEFAULT_ACTION_LABEL_CORRECT_GUESS,
    )

    PROMPT_TITLE_GENERIC = DEFAULT_PROMPT_TITLE_GENERIC
    PROMPT_LABEL_GENERIC = DEFAULT_PROMPT_LABEL_GENERIC

    MISSED_BASE_TAG = _to_string_list(
        base_cfg.get("tags", merged_cfg.get("base_missed_tag", merged_cfg.get("missed_base_tag", []))),
        fallback=DEFAULT_BASE_MISSED_TAGS,
    )

    DEFAULT_TEST_TAG_PREFIX_RUNTIME = _to_text(
        uworld_cfg.get("default_tag_prefix", DEFAULT_TEST_TAG_PREFIX),
        DEFAULT_TEST_TAG_PREFIX,
    )
    DEFAULT_NBME_TAG_PREFIX_RUNTIME = _to_text(
        nbme_cfg.get("default_tag_prefix", DEFAULT_NBME_TAG_PREFIX),
        DEFAULT_NBME_TAG_PREFIX,
    )

    SUBSET_1_NAME = _to_text(
        uworld_cfg.get("label", merged_cfg.get("subset_1_name", DEFAULT_UWORLD_LABEL)),
        DEFAULT_UWORLD_LABEL,
    )
    SUBSET_1_TAG = _to_string_list(
        uworld_cfg.get("base_tags", merged_cfg.get("subset_tag_1", merged_cfg.get("subset_1_tag", []))),
        fallback=[base_tag_path(DEFAULT_TEST_TAG_PREFIX_RUNTIME)],
    )

    SUBSET_2_NAME = _to_text(
        nbme_cfg.get("label", merged_cfg.get("subset_2_name", DEFAULT_NBME_LABEL)),
        DEFAULT_NBME_LABEL,
    )
    SUBSET_2_TAG = _to_string_list(
        nbme_cfg.get("base_tags", merged_cfg.get("subset_tag_2", merged_cfg.get("subset_2_tag", []))),
        fallback=[base_tag_path(DEFAULT_NBME_TAG_PREFIX_RUNTIME)],
    )

    AMBOSS_TOP_LEVEL_NAME = _to_text(
        amboss_cfg.get("label", DEFAULT_AMBOSS_LABEL),
        DEFAULT_AMBOSS_LABEL,
    )
    AMBOSS_BASE_TAG = _to_text(
        amboss_cfg.get("base_tag", DEFAULT_AMBOSS_BASE_TAG),
        DEFAULT_AMBOSS_BASE_TAG,
    )
    AMBOSS_BLANK_BEHAVIOR = _to_text(
        amboss_cfg.get("blank_behavior", PROMPT_BEHAVIOR_BASE_ONLY),
        PROMPT_BEHAVIOR_BASE_ONLY,
    )
    AMBOSS_NUMBER_STYLE = _to_text(
        amboss_cfg.get("number_style", PROMPT_STYLE_NUMBER_ONLY),
        PROMPT_STYLE_NUMBER_ONLY,
    )
    AMBOSS_REMOVE_FROM_OTHER_MENU = _to_bool(
        amboss_cfg.get("remove_from_other_menu", True),
        True,
    )

    MULTI_MISS_TAG = _to_text(
        multi_missed_cfg.get("tag_segment", DEFAULT_MULTI_MISS_TAG),
        DEFAULT_MULTI_MISS_TAG,
    )

    KEY_TAG_BASE = _to_text(
        key_info_cfg.get("tag_base", DEFAULT_KEY_TAG_BASE),
        DEFAULT_KEY_TAG_BASE,
    )

    CORRECT_GUESS_TAGS = _to_string_list(
        correct_guess_cfg.get("tags", DEFAULT_CORRECT_GUESS_TAGS),
        fallback=DEFAULT_CORRECT_GUESS_TAGS,
    )

    legacy_other_menu = merged_cfg.get("other_menu", {})
    if not isinstance(legacy_other_menu, dict):
        legacy_other_menu = {}

    OTHER_RESOURCES = _to_string_list(
        other_cfg.get("resources", legacy_other_menu.get("resources", DEFAULT_OTHER_RESOURCES)),
        fallback=DEFAULT_OTHER_RESOURCES,
    )
    OTHER_SUFFIX = _to_text(
        other_cfg.get("tag_suffix", DEFAULT_OTHER_SUFFIX),
        DEFAULT_OTHER_SUFFIX,
    )

    TEST_RANGE_BLOCK_SIZE = _to_positive_int(
        uworld_cfg.get("test_range_block_size", DEFAULT_TEST_RANGE_BLOCK_SIZE),
        DEFAULT_TEST_RANGE_BLOCK_SIZE,
    )

    ENABLED_Q_BANKS = _normalize_q_banks(
        merged_cfg.get("Q_Banks", DEFAULT_Q_BANKS),
        fallback=DEFAULT_Q_BANKS,
    )


_reload_runtime_config()


def get_missed_month_tag() -> str:
    now = datetime.now()
    base = MISSED_BASE_TAG[0] if MISSED_BASE_TAG else DEFAULT_BASE_MISSED_TAGS[0]
    return f"{base}::{now.year}::{now.strftime('%m')}_{now.strftime('%B')}"


def get_key_info_tag() -> str:
    now = datetime.now()
    return f"{KEY_TAG_BASE}::{now.year}::{now.strftime('%m')}_{now.strftime('%B')}"


def get_correct_guess_tags() -> list[str]:
    return list(CORRECT_GUESS_TAGS)


def get_rotation_key_info_tag() -> str:
    """Backward-compatible alias for older imports."""
    return get_key_info_tag()


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


def apply_tags_to_selected_notes(browser, tag_list: list[str], action_key: str):
    _reload_runtime_config()

    col = browser.mw.col
    nids = browser.selectedNotes()
    if not nids:
        return

    final = list(tag_list or [])
    if action_key not in set(EXCLUDE_AUTO_MISS):
        final.append(get_missed_month_tag())

    seen = set()
    final_tags: list[str] = []
    for tag in final:
        if tag and tag not in seen:
            seen.add(tag)
            final_tags.append(tag)

    for nid in nids:
        note = col.get_note(nid)
        current = set(note.tags)
        for tag in final_tags:
            if tag not in current:
                _add_tag_safe(note, tag)
        _save_note_safe(col, note)

    browser.model.reset()
    tooltip(f"✅ Applied {len(final_tags)} tags to {len(nids)} notes.")


def add_base_plain_action(browser, menu):
    action = QAction(ACTION_LABEL_BASE, browser)
    action.triggered.connect(
        lambda _: apply_tags_to_selected_notes(browser, MISSED_BASE_TAG, action_key=ACTION_KEY_BASE_PLAIN)
    )
    menu.addAction(action)


def add_missed_tag_menu_items(browser, menu):
    _reload_runtime_config()

    tag_menu = QMenu(MISSED_TAGS_MENU_LABEL, browser)
    tag_menu.setStyleSheet(
        """
        QMenu::item {
            padding-top: 4.5px;
            padding-bottom: 4.5px;
            padding-left: 6px;
            padding-right: 6px;
        }
        QMenu::item:selected {
            background-color: rgba(120, 160, 255, 60);  /* subtle hover highlight */
        }
    """
    )

    add_uworld_tags(browser, tag_menu)
    add_nbme_tag(browser, tag_menu)
    add_amboss_tag(browser, tag_menu)
    add_base_plain_action(browser, tag_menu)
    tag_menu.addSeparator()

    add_multi_tag(browser, tag_menu)
    tag_menu.addSeparator()

    add_key_info_action(browser, tag_menu)
    add_correct_guess_action(browser, tag_menu)
    tag_menu.addSeparator()

    add_other_resources_actions(browser, tag_menu)

    if tag_menu.actions():
        menu.addSeparator()
        menu.addMenu(tag_menu)


def add_nbme_tag(browser, menu):
    if not _is_bank_enabled("NBME"):
        return

    base_tag = _nbme_base_tag()
    action = QAction(f"{SUBSET_2_NAME:<24}", browser)

    def on_trigger():
        form_value, ok = QInputDialog.getText(browser, PROMPT_TITLE_NBME_FORM, PROMPT_LABEL_NBME_FORM)
        if not ok:
            return

        try:
            form_number = int((form_value or "").strip())
        except ValueError:
            showInfo(MSG_INVALID_TEST_NUMBER)
            return

        if form_number <= 0:
            showInfo(MSG_INVALID_TEST_NUMBER)
            return

        if not browser.selectedNotes():
            showInfo(MSG_NO_NOTES_SELECTED)
            return

        formatted_tag = f"{base_tag}::Form_{form_number}"
        apply_tags_to_selected_notes(
            browser,
            [formatted_tag],
            action_key=ACTION_KEY_NBME_FORM_PROMPT,
        )

    action.triggered.connect(on_trigger)
    menu.addAction(action)


def add_amboss_tag(browser, menu):
    if not _is_bank_enabled("AMBOSS"):
        return

    action = QAction(f"{AMBOSS_TOP_LEVEL_NAME:<24}", browser)
    action.triggered.connect(
        make_test_prompt_handler(
            browser,
            AMBOSS_BASE_TAG,
            action_key=ACTION_KEY_AMBOSS_TEST_PROMPT,
            title=PROMPT_TITLE_AMBOSS,
            label=PROMPT_LABEL_GENERIC,
            blank_behavior=AMBOSS_BLANK_BEHAVIOR,
            number_style=AMBOSS_NUMBER_STYLE,
        )
    )
    menu.addAction(action)


def add_multi_tag(browser, menu):
    multi_tag = base_tag_path(MULTI_MISS_TAG)
    add_static_action(
        browser,
        menu,
        f"{ACTION_LABEL_MULTI_MISSED:<24}",
        [multi_tag],
        action_key="multi_missed",
    )


def add_uworld_tags(browser, menu):
    if not _is_bank_enabled("UWORLD"):
        return

    base = _uw_base_tag()
    if SUBSET_1_NAME and base:
        action = QAction(f"{SUBSET_1_NAME:<24}", browser)
        action.triggered.connect(
            make_test_prompt_handler(
                browser,
                base,
                action_key=ACTION_KEY_UWORLD_TEST_PROMPT,
                title=PROMPT_TITLE_UWORLD,
                label=PROMPT_LABEL_GENERIC,
                blank_behavior=PROMPT_BEHAVIOR_BASE_ONLY,
                number_style=PROMPT_STYLE_RANGE_THEN_NUMBER,
            )
        )
        menu.addAction(action)


def add_other_resources_actions(browser, menu):
    for resource_name in OTHER_RESOURCES:
        label = str(resource_name).strip()
        canonical = scrub_resource_label_to_tag(resource_name)

        if AMBOSS_REMOVE_FROM_OTHER_MENU and canonical.lower() == "amboss":
            continue

        if canonical == "True-Learn":
            base_tag = base_tag_path(OTHER_SUFFIX, canonical)
            action = QAction(label, browser)
            handler = make_test_prompt_handler(
                browser,
                base_tag,
                action_key=ACTION_KEY_TRUE_LEARN_TEST_PROMPT,
                title=PROMPT_TITLE_TRUE_LEARN,
                label=PROMPT_LABEL_GENERIC,
                blank_behavior=PROMPT_BEHAVIOR_BASE_ONLY,
                number_style=PROMPT_STYLE_NUMBER_ONLY,
            )
            action.triggered.connect(handler)
            menu.addAction(action)
            continue

        resource_tag = base_tag_path(OTHER_SUFFIX, canonical)
        action = QAction(label, browser)

        def on_click(_, rtag=resource_tag):
            if not browser.selectedNotes():
                showInfo(MSG_NO_NOTES_SELECTED)
                return
            tags_to_apply = MISSED_BASE_TAG + [rtag]
            apply_tags_to_selected_notes(browser, tags_to_apply, action_key=ACTION_KEY_OTHER_RESOURCE)

        action.triggered.connect(on_click)
        menu.addAction(action)


def make_test_prompt_handler(
    browser,
    base_tag: str,
    action_key: str,
    title: str | None = None,
    label: str | None = None,
    blank_behavior: str = PROMPT_BEHAVIOR_BASE_ONLY,
    number_style: str = PROMPT_STYLE_RANGE_THEN_NUMBER,
):
    """
    number_style:
      - "range_then_number" -> base_tag::<lower-upper>::NN
      - "number_only" -> base_tag::NN

    blank_behavior is accepted for compatibility. Blank and non-numeric values
    resolve to base_tag in current behavior.
    """

    def on_trigger():
        prompt_title = (title or PROMPT_TITLE_GENERIC).strip() or PROMPT_TITLE_GENERIC
        prompt_label = (label or PROMPT_LABEL_GENERIC).strip() or PROMPT_LABEL_GENERIC
        test_num, ok = QInputDialog.getText(browser, prompt_title, prompt_label)
        if not ok:
            return

        test_num = (test_num or "").strip()
        normalized_number_style = (
            PROMPT_STYLE_RANGE_THEN_NUMBER
            if number_style == PROMPT_STYLE_RANGE_THEN_NUMBER
            else PROMPT_STYLE_NUMBER_ONLY
        )

        if test_num == "":
            if blank_behavior == PROMPT_BEHAVIOR_BASE_ONLY:
                formatted_tag = f"{base_tag}"
            else:
                formatted_tag = f"{base_tag}"
        else:
            try:
                test_number = int(test_num)
            except ValueError:
                if blank_behavior == PROMPT_BEHAVIOR_BASE_ONLY:
                    formatted_tag = f"{base_tag}"
                else:
                    formatted_tag = f"{base_tag}"
            else:
                if normalized_number_style == PROMPT_STYLE_RANGE_THEN_NUMBER:
                    lower = ((test_number - 1) // TEST_RANGE_BLOCK_SIZE) * TEST_RANGE_BLOCK_SIZE + 1
                    upper = lower + TEST_RANGE_BLOCK_SIZE - 1
                    range_tag = f"{lower}-{upper}"
                    formatted_tag = f"{base_tag}::{range_tag}::{test_number:02d}"
                else:
                    formatted_tag = f"{base_tag}::{test_number:02d}"

        if not browser.selectedNotes():
            showInfo(MSG_NO_NOTES_SELECTED)
            return

        apply_tags_to_selected_notes(browser, [formatted_tag], action_key=action_key)

    return on_trigger


def add_static_action(browser, menu, set_name: str, tags: list[str], action_key: str):
    action = QAction(set_name, browser)
    action.triggered.connect(
        lambda _, tags=tags, k=action_key: apply_tags_to_selected_notes(browser, tags, action_key=k)
    )
    menu.addAction(action)


def add_key_info_action(browser, menu):
    action = QAction(ACTION_LABEL_KEY_INFO, browser)

    def on_click():
        if not browser.selectedNotes():
            showInfo(MSG_NO_NOTES_SELECTED)
            return
        key_tag = get_key_info_tag()
        apply_tags_to_selected_notes(browser, [key_tag], action_key=ACTION_KEY_KEY_INFO)

    action.triggered.connect(on_click)
    menu.addAction(action)


def add_correct_guess_action(browser, menu):
    action = QAction(ACTION_LABEL_CORRECT_GUESS, browser)
    action.triggered.connect(
        lambda _: apply_tags_to_selected_notes(
            browser,
            get_correct_guess_tags(),
            action_key=ACTION_KEY_CORRECT_GUESS,
        )
    )
    menu.addAction(action)
