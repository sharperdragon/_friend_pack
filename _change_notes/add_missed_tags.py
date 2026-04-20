# pyright: reportMissingImports=false
from __future__ import annotations

from datetime import datetime
from typing import Any

from aqt.qt import QAction, QInputDialog, QMenu
from aqt.utils import showInfo, tooltip

from ..menu_styles import build_context_submenu_item_stylesheet
from ..utils.config_manager import ConfigManager

# ! ----------------------------- CONFIG SECTIONS -----------------------------
CONFIG_SECTION = "add_missed_tags"
# ! -------------------------------------------------------------------------

# ! ----------------------------- USER-TUNABLE CONSTANTS -----------------------------
# ? Base/scaffold defaults
DEFAULT_PRIMARY_MISSED_TAG = "##Missed-Qs"
DEFAULT_BASE_MISSED_TAGS = [DEFAULT_PRIMARY_MISSED_TAG]
DEFAULT_Q_BANKS = ["UWORLD", "NBME", "AMBOSS"]
DEFAULT_TEST_TAG_PREFIX = "UW_Tests"
DEFAULT_NBME_TAG_PREFIX = "NBME"
DEFAULT_MULTI_MISS_TAG = "2x"

# ? Action defaults
DEFAULT_UWORLD_LABEL = "🛃UWorld"
DEFAULT_UWORLD_BASE_TAGS = ["##Missed-Qs::UW_Tests"]
DEFAULT_NBME_LABEL = "🧠 NBME"
DEFAULT_NBME_BASE_TAGS = ["##Missed-Qs::NBME"]
DEFAULT_AMBOSS_LABEL = "🦠 Amboss"
DEFAULT_AMBOSS_BASE_TAG = "##Missed-Qs::Amboss"
DEFAULT_OTHER_SUBMENU_BOOL = True
DEFAULT_OTHER_SUBMENU_LABEL = "Other"
DEFAULT_OTHER_TAG_SEGMENT_GROUP = True
DEFAULT_OTHER_GROUP_SEGMENT = "Other"
DEFAULT_OTHER_ADD_MISSED_DATE_CONTEXT = False
DEFAULT_OTHER_ACTIONS = [
    {"menu_label": "Kaplan", "tag_segment": "Kaplan", "prompt": {"kind": "none"}},
    {"menu_label": "True-learn", "tag_segment": "True-learn", "prompt": {"kind": "none"}},
]
DEFAULT_CORRECT_GUESS_TAGS = ["#Custom::correct_marked"]
DEFAULT_TEST_RANGE_BLOCK_SIZE = 25
DEFAULT_INCLUDE_DAY_SEGMENT = True

# ? Prompt/format behavior
PROMPT_STYLE_RANGE_THEN_NUMBER = "range_then_number"
PROMPT_STYLE_NUMBER_ONLY = "number_only"
PROMPT_KIND_NONE = "none"
PROMPT_KIND_NUMBER = "number"
PROMPT_KIND_FORM = "form"
DEFAULT_FORM_INPUT_ITEMS = ["Form"]

# ? Hardcoded UI messages (intentionally not configurable)
DEFAULT_MISSED_TAGS_MENU_LABEL = "Missed Tags ❌"
DEFAULT_MSG_NO_NOTES_SELECTED = "❌ No notes selected."
DEFAULT_MSG_INVALID_TEST_NUMBER = "❌ Please enter a valid integer test number."
DEFAULT_ACTION_LABEL_BASE = "♦️Base"
DEFAULT_ACTION_LABEL_MULTI_MISSED = "2x Missed 📌"
DEFAULT_ACTION_LABEL_CORRECT_GUESS = "Guessed Correct 🎫"
DEFAULT_PROMPT_TITLE_GENERIC = "Enter Test Number"
DEFAULT_PROMPT_LABEL_GENERIC = "Test #:"

PROMPT_TITLE_UWORLD = "Enter UWorld Test Number"
PROMPT_TITLE_NBME_FORM = "Enter NBME Form"
PROMPT_LABEL_NBME_FORM = "Form #:"
PROMPT_TITLE_AMBOSS = "Enter Amboss Test Number"

# ? Runtime state (reloaded from config)
MISSED_BASE_TAG = list(DEFAULT_BASE_MISSED_TAGS)
PRIMARY_MISSED_TAG = DEFAULT_PRIMARY_MISSED_TAG
ENABLED_Q_BANKS = {bank.upper() for bank in DEFAULT_Q_BANKS}

SUBSET_1_NAME = DEFAULT_UWORLD_LABEL
SUBSET_1_TAG = list(DEFAULT_UWORLD_BASE_TAGS)
SUBSET_2_NAME = DEFAULT_NBME_LABEL
SUBSET_2_TAG = list(DEFAULT_NBME_BASE_TAGS)

AMBOSS_TOP_LEVEL_NAME = DEFAULT_AMBOSS_LABEL
AMBOSS_BASE_TAG = DEFAULT_AMBOSS_BASE_TAG
AMBOSS_PROMPT_KIND = PROMPT_KIND_NUMBER
AMBOSS_NUMBER_STYLE = PROMPT_STYLE_NUMBER_ONLY
AMBOSS_PROMPT_RANGE_BLOCK_SIZE = DEFAULT_TEST_RANGE_BLOCK_SIZE

MULTI_MISS_TAG = DEFAULT_MULTI_MISS_TAG
OTHER_SUBMENU_BOOL = DEFAULT_OTHER_SUBMENU_BOOL
OTHER_SUBMENU_LABEL = DEFAULT_OTHER_SUBMENU_LABEL
OTHER_CHILD_OF_PRIMARY = True
OTHER_TAG_SEGMENT_GROUP = DEFAULT_OTHER_TAG_SEGMENT_GROUP
OTHER_GROUP_SEGMENT = DEFAULT_OTHER_GROUP_SEGMENT
OTHER_ACTIONS: list[dict[str, Any]] = [dict(item) for item in DEFAULT_OTHER_ACTIONS]
CORRECT_GUESS_TAGS = list(DEFAULT_CORRECT_GUESS_TAGS)
TEST_RANGE_BLOCK_SIZE = DEFAULT_TEST_RANGE_BLOCK_SIZE
DEFAULT_NBME_TAG_PREFIX_RUNTIME = DEFAULT_NBME_TAG_PREFIX
DEFAULT_TEST_TAG_PREFIX_RUNTIME = DEFAULT_TEST_TAG_PREFIX
INCLUDE_DAY_SEGMENT = DEFAULT_INCLUDE_DAY_SEGMENT
UWORLD_PROMPT_KIND = PROMPT_KIND_NUMBER
UWORLD_NUMBER_STYLE = PROMPT_STYLE_RANGE_THEN_NUMBER
UWORLD_RANGE_BLOCK_SIZE = DEFAULT_TEST_RANGE_BLOCK_SIZE
UWORLD_PROMPT_INPUT_ITEMS = list(DEFAULT_FORM_INPUT_ITEMS)
NBME_PROMPT_KIND = PROMPT_KIND_FORM
NBME_NUMBER_STYLE = PROMPT_STYLE_NUMBER_ONLY
NBME_RANGE_BLOCK_SIZE = DEFAULT_TEST_RANGE_BLOCK_SIZE
NBME_PROMPT_INPUT_ITEMS = list(DEFAULT_FORM_INPUT_ITEMS)
AMBOSS_PROMPT_INPUT_ITEMS = list(DEFAULT_FORM_INPUT_ITEMS)

MISSED_TAGS_MENU_LABEL = DEFAULT_MISSED_TAGS_MENU_LABEL
MSG_NO_NOTES_SELECTED = DEFAULT_MSG_NO_NOTES_SELECTED
MSG_INVALID_TEST_NUMBER = DEFAULT_MSG_INVALID_TEST_NUMBER
ACTION_LABEL_BASE = DEFAULT_ACTION_LABEL_BASE
ACTION_LABEL_MULTI_MISSED = DEFAULT_ACTION_LABEL_MULTI_MISSED
ACTION_LABEL_CORRECT_GUESS = DEFAULT_ACTION_LABEL_CORRECT_GUESS
PROMPT_TITLE_GENERIC = DEFAULT_PROMPT_TITLE_GENERIC
PROMPT_LABEL_GENERIC = DEFAULT_PROMPT_LABEL_GENERIC

# ? Action keys
ACTION_KEY_BASE_PLAIN = "base_plain"
ACTION_KEY_CORRECT_GUESS = "correct_guess"
ACTION_KEY_NBME_FORM_PROMPT = "nbme_form_prompt"
ACTION_KEY_UWORLD_TEST_PROMPT = "uw_test_prompt"
ACTION_KEY_AMBOSS_TEST_PROMPT = "amboss_test_prompt"
ACTION_KEY_OTHER_RESOURCE = "other_resource"
ACTION_KEY_MULTI_MISSED = "multi_missed"

DEFAULT_ACTION_MISSED_DATE_CONTEXT: dict[str, bool] = {
    ACTION_KEY_BASE_PLAIN: False,
    ACTION_KEY_UWORLD_TEST_PROMPT: True,
    ACTION_KEY_NBME_FORM_PROMPT: True,
    ACTION_KEY_AMBOSS_TEST_PROMPT: True,
    ACTION_KEY_MULTI_MISSED: True,
    ACTION_KEY_CORRECT_GUESS: False,
    ACTION_KEY_OTHER_RESOURCE: True,
}
ACTION_MISSED_DATE_CONTEXT: dict[str, bool] = dict(DEFAULT_ACTION_MISSED_DATE_CONTEXT)
# ! -------------------------------------------------------------------------


# $ Compose a full Missed-Qs tag path with the base prefix
def base_tag_path(*parts: str) -> str:
    base = PRIMARY_MISSED_TAG or DEFAULT_PRIMARY_MISSED_TAG
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


def _prompt_label_from_input_item(item: str, fallback: str) -> str:
    text = str(item or "").strip()
    if not text:
        return fallback
    base = text.rstrip(":").strip()
    if not base:
        return fallback
    if base.endswith("#"):
        return f"{base}:"
    return f"{base} #:"


def _read_menu_label(cfg: dict[str, Any], fallback: str) -> str:
    menu_label = cfg.get("menu_label")
    if isinstance(menu_label, str) and menu_label.strip():
        return menu_label.strip()
    # Backward compatibility with older key name.
    return _to_text(cfg.get("label", fallback), fallback)


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


def _to_prompt_kind(value: Any, fallback: str) -> str:
    text = str(value).strip().lower()
    if text in {PROMPT_KIND_NONE, PROMPT_KIND_NUMBER, PROMPT_KIND_FORM}:
        return text
    return fallback


def _to_prompt_number_style(value: Any, fallback: str) -> str:
    text = str(value).strip()
    if text in {PROMPT_STYLE_RANGE_THEN_NUMBER, PROMPT_STYLE_NUMBER_ONLY}:
        return text
    return fallback


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _get_saved_prompt_input(prompt_key: str) -> str:
    if not prompt_key:
        return ""
    section_cfg = _as_dict(ConfigManager.get_section(CONFIG_SECTION, default={}))
    runtime_cfg = _as_dict(section_cfg.get("runtime"))
    last_inputs = _as_dict(runtime_cfg.get("last_prompt_inputs"))
    value = last_inputs.get(prompt_key, "")
    return value if isinstance(value, str) else ""


def _save_prompt_input(prompt_key: str, prompt_value: str) -> None:
    if not prompt_key:
        return

    try:
        section_cfg = _as_dict(ConfigManager.get_section(CONFIG_SECTION, default={}))
        runtime_cfg = _as_dict(section_cfg.get("runtime"))
        last_inputs = _as_dict(runtime_cfg.get("last_prompt_inputs"))

        normalized_value = str(prompt_value)
        current_value = last_inputs.get(prompt_key)
        if isinstance(current_value, str) and current_value == normalized_value:
            return

        updated_section = ConfigManager.deep_merge_dicts({}, section_cfg)
        updated_runtime_cfg = _as_dict(updated_section.get("runtime"))
        updated_last_inputs = _as_dict(updated_runtime_cfg.get("last_prompt_inputs"))
        updated_last_inputs[prompt_key] = normalized_value
        updated_runtime_cfg["last_prompt_inputs"] = updated_last_inputs
        updated_section["runtime"] = updated_runtime_cfg
        ConfigManager.save_section(CONFIG_SECTION, updated_section)
    except Exception:
        # Prompt-memory persistence should not block tagging behavior.
        return


def _text_prompt_with_default(parent: Any, title: str, label: str, default_text: str = "") -> tuple[str, bool]:
    dialog = QInputDialog(parent)
    dialog.setInputMode(QInputDialog.InputMode.TextInput)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    dialog.setTextValue(default_text)
    accepted = bool(dialog.exec())
    return dialog.textValue(), accepted


def _split_tag_path(text: str) -> list[str]:
    return [part.strip() for part in str(text).split("::") if part.strip()]


def _tag_from_primary_segment(segment_path: str) -> str:
    raw = str(segment_path or "").strip()
    if not raw:
        return PRIMARY_MISSED_TAG or DEFAULT_PRIMARY_MISSED_TAG
    primary = PRIMARY_MISSED_TAG or DEFAULT_PRIMARY_MISSED_TAG
    if raw == primary:
        return primary
    prefix = f"{primary}::"
    if raw.startswith(prefix):
        raw = raw[len(prefix):]
    return base_tag_path(*_split_tag_path(raw))


def _resolve_child_of_primary_flag(
    action_cfg: dict[str, Any],
    *,
    default_child: bool,
    legacy_absolute_keys: tuple[str, ...] = (),
) -> bool:
    if "child_of_primary_missed" in action_cfg:
        return _to_bool(action_cfg.get("child_of_primary_missed"), default_child)
    for key in legacy_absolute_keys:
        if key in action_cfg:
            return False
    return default_child


def _resolve_action_tags(
    action_cfg: dict[str, Any],
    *,
    child_of_primary: bool,
    default_segments: list[str],
    default_absolute_tags: list[str],
    legacy_segment_keys: tuple[str, ...] = (),
    legacy_absolute_keys: tuple[str, ...] = (),
) -> list[str]:
    if child_of_primary:
        segment_source: Any = action_cfg.get("tag_segment")
        if segment_source is None:
            segment_source = action_cfg.get("tag_segments")
        if segment_source is None:
            for key in legacy_segment_keys:
                if key in action_cfg:
                    segment_source = action_cfg.get(key)
                    break
        segments = _to_string_list(segment_source, fallback=default_segments)
        return [_tag_from_primary_segment(seg) for seg in segments]

    absolute_source: Any = action_cfg.get("absolute_tags")
    if absolute_source is None:
        for key in legacy_absolute_keys:
            if key in action_cfg:
                absolute_source = action_cfg.get(key)
                break
    return _to_string_list(absolute_source, fallback=default_absolute_tags)


def _resolve_action_prompt(
    action_cfg: dict[str, Any],
    *,
    default_kind: str,
    default_number_style: str,
    default_range_block_size: int,
    default_form_input_items: list[str] | None = None,
    legacy_number_style_keys: tuple[str, ...] = (),
    legacy_range_block_size_keys: tuple[str, ...] = (),
) -> tuple[str, str, int, list[str]]:
    prompt_cfg = action_cfg.get("prompt", {})
    if not isinstance(prompt_cfg, dict):
        prompt_cfg = {}

    fallback_form_input_items = (
        list(default_form_input_items)
        if isinstance(default_form_input_items, list) and default_form_input_items
        else list(DEFAULT_FORM_INPUT_ITEMS)
    )

    kind = _to_prompt_kind(prompt_cfg.get("kind", default_kind), default_kind)

    number_style_source: Any = prompt_cfg.get("number_style")
    if number_style_source is None:
        for key in legacy_number_style_keys:
            if key in action_cfg:
                number_style_source = action_cfg.get(key)
                break
    number_style = _to_prompt_number_style(number_style_source, default_number_style)

    range_block_size_source: Any = prompt_cfg.get("range_block_size")
    if range_block_size_source is None:
        for key in legacy_range_block_size_keys:
            if key in action_cfg:
                range_block_size_source = action_cfg.get(key)
                break
    range_block_size = _to_positive_int(range_block_size_source, default_range_block_size)

    input_items = _to_string_list(
        prompt_cfg.get("input_items"),
        fallback=fallback_form_input_items,
    )

    return kind, number_style, range_block_size, input_items


def _set_missed_date_context_from_cfg(action_cfg: dict[str, Any], action_key: str, fallback: bool) -> None:
    ACTION_MISSED_DATE_CONTEXT[action_key] = _to_bool(
        action_cfg.get("add_missed_date_context", fallback),
        fallback,
    )


def _is_bank_enabled(bank_name: str) -> bool:
    return bank_name.strip().upper() in ENABLED_Q_BANKS


def _normalize_other_actions(raw: Any) -> list[dict[str, Any]]:
    return _normalize_other_actions_with_prompt_defaults(
        raw,
        default_prompt_kind=PROMPT_KIND_NONE,
        default_prompt_number_style=PROMPT_STYLE_NUMBER_ONLY,
        default_prompt_range_block_size=DEFAULT_TEST_RANGE_BLOCK_SIZE,
        default_prompt_input_items=DEFAULT_FORM_INPUT_ITEMS,
    )


def _normalize_other_actions_with_prompt_defaults(
    raw: Any,
    *,
    default_prompt_kind: str,
    default_prompt_number_style: str,
    default_prompt_range_block_size: int,
    default_prompt_input_items: list[str],
) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        source = raw
        fallback_to_defaults = False
    else:
        source = DEFAULT_OTHER_ACTIONS
        fallback_to_defaults = True
    out: list[dict[str, Any]] = []

    for item in source:
        if not isinstance(item, dict):
            continue

        menu_label = str(item.get("menu_label", "")).strip()
        tag_segment = str(item.get("tag_segment", "")).strip()
        if not menu_label or not tag_segment:
            continue

        (
            prompt_kind,
            prompt_number_style,
            prompt_range_block_size,
            prompt_input_items,
        ) = _resolve_action_prompt(
            item,
            default_kind=default_prompt_kind,
            default_number_style=default_prompt_number_style,
            default_range_block_size=default_prompt_range_block_size,
            default_form_input_items=default_prompt_input_items,
        )
        out.append(
            {
                "menu_label": menu_label,
                "tag_segment": tag_segment,
                "prompt_kind": prompt_kind,
                "prompt_number_style": prompt_number_style,
                "prompt_range_block_size": prompt_range_block_size,
                "prompt_input_items": prompt_input_items,
            }
        )

    if out:
        return out
    if fallback_to_defaults:
        return [dict(item) for item in DEFAULT_OTHER_ACTIONS]
    return []


def _get_input_dialog_item(
    parent: Any,
    title: str,
    label: str,
    items: list[str],
    current_index: int = 0,
    editable: bool = False,
) -> tuple[str, bool]:
    """
    Wrapper for QInputDialog.getItem.

    Runtime Qt bindings provide this static method, but some type stubs omit it.
    """
    dialog_api: Any = QInputDialog
    selected_item, ok = dialog_api.getItem(
        parent,
        title,
        label,
        items,
        current_index,
        editable,
    )
    return str(selected_item), bool(ok)


def _other_action_base_tag(action_tag_segment: str) -> str:
    segment = str(action_tag_segment or "").strip()
    if not segment:
        return ""

    parts: list[str] = []
    if OTHER_CHILD_OF_PRIMARY:
        parts.append(PRIMARY_MISSED_TAG or DEFAULT_PRIMARY_MISSED_TAG)
    if OTHER_TAG_SEGMENT_GROUP:
        parts.append(_to_text(OTHER_GROUP_SEGMENT, DEFAULT_OTHER_GROUP_SEGMENT))
    parts.append(segment)
    return "::".join([part for part in parts if part])


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
    global PRIMARY_MISSED_TAG
    global ENABLED_Q_BANKS
    global SUBSET_1_NAME
    global SUBSET_1_TAG
    global SUBSET_2_NAME
    global SUBSET_2_TAG
    global UWORLD_PROMPT_KIND
    global UWORLD_NUMBER_STYLE
    global UWORLD_RANGE_BLOCK_SIZE
    global UWORLD_PROMPT_INPUT_ITEMS
    global NBME_PROMPT_KIND
    global NBME_NUMBER_STYLE
    global NBME_RANGE_BLOCK_SIZE
    global NBME_PROMPT_INPUT_ITEMS
    global AMBOSS_TOP_LEVEL_NAME
    global AMBOSS_PROMPT_KIND
    global AMBOSS_BASE_TAG
    global AMBOSS_NUMBER_STYLE
    global AMBOSS_PROMPT_RANGE_BLOCK_SIZE
    global AMBOSS_PROMPT_INPUT_ITEMS
    global MULTI_MISS_TAG
    global OTHER_SUBMENU_BOOL
    global OTHER_SUBMENU_LABEL
    global OTHER_CHILD_OF_PRIMARY
    global OTHER_TAG_SEGMENT_GROUP
    global OTHER_GROUP_SEGMENT
    global OTHER_ACTIONS
    global CORRECT_GUESS_TAGS
    global TEST_RANGE_BLOCK_SIZE
    global DEFAULT_NBME_TAG_PREFIX_RUNTIME
    global DEFAULT_TEST_TAG_PREFIX_RUNTIME
    global INCLUDE_DAY_SEGMENT
    global MISSED_TAGS_MENU_LABEL
    global MSG_NO_NOTES_SELECTED
    global MSG_INVALID_TEST_NUMBER
    global ACTION_LABEL_BASE
    global ACTION_LABEL_MULTI_MISSED
    global ACTION_LABEL_CORRECT_GUESS
    global PROMPT_TITLE_GENERIC
    global PROMPT_LABEL_GENERIC
    global ACTION_MISSED_DATE_CONTEXT

    section_cfg = ConfigManager.get_section(CONFIG_SECTION, default={})
    merged_cfg = section_cfg if isinstance(section_cfg, dict) else {}

    defaults_cfg = merged_cfg.get("defaults", {})
    if not isinstance(defaults_cfg, dict):
        defaults_cfg = {}

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

    correct_guess_cfg = actions_cfg.get("correct_guess", {})
    if not isinstance(correct_guess_cfg, dict):
        correct_guess_cfg = {}

    other_cfg = actions_cfg.get("other", {})
    if not isinstance(other_cfg, dict):
        other_cfg = {}
    other_tagging_cfg = other_cfg.get("tagging", {})
    if not isinstance(other_tagging_cfg, dict):
        other_tagging_cfg = {}

    action_defaults_cfg = merged_cfg.get("action_defaults", {})
    if not isinstance(action_defaults_cfg, dict):
        action_defaults_cfg = {}
    action_defaults_prompt_cfg = action_defaults_cfg.get("prompt", {})
    if not isinstance(action_defaults_prompt_cfg, dict):
        action_defaults_prompt_cfg = {}

    has_action_default_include_day_segment = "include_day_segment" in action_defaults_cfg
    action_default_include_day_segment = _to_bool(
        action_defaults_cfg.get("include_day_segment", DEFAULT_INCLUDE_DAY_SEGMENT),
        DEFAULT_INCLUDE_DAY_SEGMENT,
    )

    has_action_default_add_missed_date_context = "add_missed_date_context" in action_defaults_cfg
    action_default_add_missed_date_context = _to_bool(
        action_defaults_cfg.get("add_missed_date_context", True),
        True,
    )

    has_action_default_child_of_primary = "child_of_primary_missed" in action_defaults_cfg
    action_default_child_of_primary = _to_bool(
        action_defaults_cfg.get("child_of_primary_missed", True),
        True,
    )

    has_action_default_prompt_kind = "kind" in action_defaults_prompt_cfg
    action_default_prompt_kind = _to_prompt_kind(
        action_defaults_prompt_cfg.get("kind", PROMPT_KIND_NONE),
        PROMPT_KIND_NONE,
    )

    has_action_default_prompt_number_style = "number_style" in action_defaults_prompt_cfg
    action_default_prompt_number_style = _to_prompt_number_style(
        action_defaults_prompt_cfg.get("number_style", PROMPT_STYLE_NUMBER_ONLY),
        PROMPT_STYLE_NUMBER_ONLY,
    )

    has_action_default_prompt_range_block_size = "range_block_size" in action_defaults_prompt_cfg
    action_default_prompt_range_block_size = _to_positive_int(
        action_defaults_prompt_cfg.get("range_block_size", DEFAULT_TEST_RANGE_BLOCK_SIZE),
        DEFAULT_TEST_RANGE_BLOCK_SIZE,
    )

    has_action_default_prompt_input_items = "input_items" in action_defaults_prompt_cfg
    action_default_prompt_input_items = _to_string_list(
        action_defaults_prompt_cfg.get("input_items"),
        fallback=DEFAULT_FORM_INPUT_ITEMS,
    )

    legacy_date_cfg = merged_cfg.get("date", {})
    if not isinstance(legacy_date_cfg, dict):
        legacy_date_cfg = {}

    PRIMARY_MISSED_TAG = _to_text(
        merged_cfg.get("primary_missed_tag", DEFAULT_PRIMARY_MISSED_TAG),
        DEFAULT_PRIMARY_MISSED_TAG,
    )

    MISSED_TAGS_MENU_LABEL = _to_text(
        merged_cfg.get(
            "menu_label",
            defaults_cfg.get("menu_label", DEFAULT_MISSED_TAGS_MENU_LABEL),
        ),
        DEFAULT_MISSED_TAGS_MENU_LABEL,
    )

    # Hardcoded by request: these remain code-only constants.
    MSG_NO_NOTES_SELECTED = DEFAULT_MSG_NO_NOTES_SELECTED
    MSG_INVALID_TEST_NUMBER = DEFAULT_MSG_INVALID_TEST_NUMBER

    ACTION_LABEL_BASE = _read_menu_label(base_cfg, DEFAULT_ACTION_LABEL_BASE)
    ACTION_LABEL_MULTI_MISSED = _read_menu_label(multi_missed_cfg, DEFAULT_ACTION_LABEL_MULTI_MISSED)
    ACTION_LABEL_CORRECT_GUESS = _read_menu_label(correct_guess_cfg, DEFAULT_ACTION_LABEL_CORRECT_GUESS)

    PROMPT_TITLE_GENERIC = DEFAULT_PROMPT_TITLE_GENERIC
    PROMPT_LABEL_GENERIC = DEFAULT_PROMPT_LABEL_GENERIC

    ACTION_MISSED_DATE_CONTEXT = dict(DEFAULT_ACTION_MISSED_DATE_CONTEXT)

    base_child_of_primary = _resolve_child_of_primary_flag(
        base_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else False,
        legacy_absolute_keys=("tags",),
    )
    MISSED_BASE_TAG = _resolve_action_tags(
        base_cfg,
        child_of_primary=base_child_of_primary,
        default_segments=[""],
        default_absolute_tags=[PRIMARY_MISSED_TAG],
        legacy_absolute_keys=("tags",),
    )
    _set_missed_date_context_from_cfg(
        base_cfg,
        ACTION_KEY_BASE_PLAIN,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_BASE_PLAIN]
        ),
    )

    DEFAULT_TEST_TAG_PREFIX_RUNTIME = _to_text(
        uworld_cfg.get("default_tag_prefix", DEFAULT_TEST_TAG_PREFIX),
        DEFAULT_TEST_TAG_PREFIX,
    )
    DEFAULT_NBME_TAG_PREFIX_RUNTIME = _to_text(
        nbme_cfg.get("default_tag_prefix", DEFAULT_NBME_TAG_PREFIX),
        DEFAULT_NBME_TAG_PREFIX,
    )

    SUBSET_1_NAME = _read_menu_label(uworld_cfg, DEFAULT_UWORLD_LABEL)
    uworld_child_of_primary = _resolve_child_of_primary_flag(
        uworld_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else True,
        legacy_absolute_keys=("base_tags",),
    )
    SUBSET_1_TAG = _resolve_action_tags(
        uworld_cfg,
        child_of_primary=uworld_child_of_primary,
        default_segments=[DEFAULT_TEST_TAG_PREFIX_RUNTIME],
        default_absolute_tags=[base_tag_path(DEFAULT_TEST_TAG_PREFIX_RUNTIME)],
        legacy_absolute_keys=("base_tags",),
    )
    (
        UWORLD_PROMPT_KIND,
        UWORLD_NUMBER_STYLE,
        UWORLD_RANGE_BLOCK_SIZE,
        UWORLD_PROMPT_INPUT_ITEMS,
    ) = _resolve_action_prompt(
        uworld_cfg,
        default_kind=action_default_prompt_kind if has_action_default_prompt_kind else PROMPT_KIND_NUMBER,
        default_number_style=(
            action_default_prompt_number_style
            if has_action_default_prompt_number_style
            else PROMPT_STYLE_RANGE_THEN_NUMBER
        ),
        default_range_block_size=(
            action_default_prompt_range_block_size
            if has_action_default_prompt_range_block_size
            else DEFAULT_TEST_RANGE_BLOCK_SIZE
        ),
        default_form_input_items=(
            action_default_prompt_input_items
            if has_action_default_prompt_input_items
            else DEFAULT_FORM_INPUT_ITEMS
        ),
        legacy_range_block_size_keys=("test_range_block_size",),
    )
    _set_missed_date_context_from_cfg(
        uworld_cfg,
        ACTION_KEY_UWORLD_TEST_PROMPT,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_UWORLD_TEST_PROMPT]
        ),
    )

    SUBSET_2_NAME = _read_menu_label(nbme_cfg, DEFAULT_NBME_LABEL)
    nbme_child_of_primary = _resolve_child_of_primary_flag(
        nbme_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else True,
        legacy_absolute_keys=("base_tags",),
    )
    SUBSET_2_TAG = _resolve_action_tags(
        nbme_cfg,
        child_of_primary=nbme_child_of_primary,
        default_segments=[DEFAULT_NBME_TAG_PREFIX_RUNTIME],
        default_absolute_tags=[base_tag_path(DEFAULT_NBME_TAG_PREFIX_RUNTIME)],
        legacy_absolute_keys=("base_tags",),
    )
    (
        NBME_PROMPT_KIND,
        NBME_NUMBER_STYLE,
        NBME_RANGE_BLOCK_SIZE,
        NBME_PROMPT_INPUT_ITEMS,
    ) = _resolve_action_prompt(
        nbme_cfg,
        default_kind=action_default_prompt_kind if has_action_default_prompt_kind else PROMPT_KIND_FORM,
        default_number_style=(
            action_default_prompt_number_style
            if has_action_default_prompt_number_style
            else PROMPT_STYLE_NUMBER_ONLY
        ),
        default_range_block_size=(
            action_default_prompt_range_block_size
            if has_action_default_prompt_range_block_size
            else DEFAULT_TEST_RANGE_BLOCK_SIZE
        ),
        default_form_input_items=(
            action_default_prompt_input_items
            if has_action_default_prompt_input_items
            else DEFAULT_FORM_INPUT_ITEMS
        ),
    )
    _set_missed_date_context_from_cfg(
        nbme_cfg,
        ACTION_KEY_NBME_FORM_PROMPT,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_NBME_FORM_PROMPT]
        ),
    )

    AMBOSS_TOP_LEVEL_NAME = _read_menu_label(amboss_cfg, DEFAULT_AMBOSS_LABEL)
    amboss_child_of_primary = _resolve_child_of_primary_flag(
        amboss_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else True,
        legacy_absolute_keys=("base_tag",),
    )
    amboss_default_segment = _to_text(
        amboss_cfg.get("tag_segment", "Amboss"),
        "Amboss",
    )
    amboss_tags = _resolve_action_tags(
        amboss_cfg,
        child_of_primary=amboss_child_of_primary,
        default_segments=[amboss_default_segment],
        default_absolute_tags=[DEFAULT_AMBOSS_BASE_TAG],
        legacy_segment_keys=("tag_segment",),
        legacy_absolute_keys=("base_tag",),
    )
    AMBOSS_BASE_TAG = amboss_tags[0] if amboss_tags else DEFAULT_AMBOSS_BASE_TAG
    (
        AMBOSS_PROMPT_KIND,
        AMBOSS_NUMBER_STYLE,
        AMBOSS_PROMPT_RANGE_BLOCK_SIZE,
        AMBOSS_PROMPT_INPUT_ITEMS,
    ) = _resolve_action_prompt(
        amboss_cfg,
        default_kind=action_default_prompt_kind if has_action_default_prompt_kind else PROMPT_KIND_NUMBER,
        default_number_style=(
            action_default_prompt_number_style
            if has_action_default_prompt_number_style
            else PROMPT_STYLE_NUMBER_ONLY
        ),
        default_range_block_size=(
            action_default_prompt_range_block_size
            if has_action_default_prompt_range_block_size
            else DEFAULT_TEST_RANGE_BLOCK_SIZE
        ),
        default_form_input_items=(
            action_default_prompt_input_items
            if has_action_default_prompt_input_items
            else DEFAULT_FORM_INPUT_ITEMS
        ),
        legacy_number_style_keys=("number_style",),
    )
    _set_missed_date_context_from_cfg(
        amboss_cfg,
        ACTION_KEY_AMBOSS_TEST_PROMPT,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_AMBOSS_TEST_PROMPT]
        ),
    )

    multi_missed_child_of_primary = _resolve_child_of_primary_flag(
        multi_missed_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else True,
        legacy_absolute_keys=("absolute_tag",),
    )
    multi_missed_tags = _resolve_action_tags(
        multi_missed_cfg,
        child_of_primary=multi_missed_child_of_primary,
        default_segments=[DEFAULT_MULTI_MISS_TAG],
        default_absolute_tags=[base_tag_path(DEFAULT_MULTI_MISS_TAG)],
        legacy_segment_keys=("tag_segment",),
        legacy_absolute_keys=("absolute_tag",),
    )
    MULTI_MISS_TAG = multi_missed_tags[0] if multi_missed_tags else base_tag_path(DEFAULT_MULTI_MISS_TAG)
    _set_missed_date_context_from_cfg(
        multi_missed_cfg,
        ACTION_KEY_MULTI_MISSED,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_MULTI_MISSED]
        ),
    )

    correct_guess_child_of_primary = _resolve_child_of_primary_flag(
        correct_guess_cfg,
        default_child=action_default_child_of_primary if has_action_default_child_of_primary else False,
        legacy_absolute_keys=("tags",),
    )
    CORRECT_GUESS_TAGS = _resolve_action_tags(
        correct_guess_cfg,
        child_of_primary=correct_guess_child_of_primary,
        default_segments=["correct_marked"],
        default_absolute_tags=DEFAULT_CORRECT_GUESS_TAGS,
        legacy_absolute_keys=("tags",),
    )
    _set_missed_date_context_from_cfg(
        correct_guess_cfg,
        ACTION_KEY_CORRECT_GUESS,
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_CORRECT_GUESS]
        ),
    )

    OTHER_SUBMENU_BOOL = _to_bool(
        other_cfg.get("submenu_bool", DEFAULT_OTHER_SUBMENU_BOOL),
        DEFAULT_OTHER_SUBMENU_BOOL,
    )
    OTHER_SUBMENU_LABEL = _to_text(
        other_cfg.get("submenu_label", DEFAULT_OTHER_SUBMENU_LABEL),
        DEFAULT_OTHER_SUBMENU_LABEL,
    )
    OTHER_CHILD_OF_PRIMARY = _to_bool(
        other_tagging_cfg.get(
            "child_of_primary_missed",
            action_default_child_of_primary if has_action_default_child_of_primary else True,
        ),
        action_default_child_of_primary if has_action_default_child_of_primary else True,
    )
    OTHER_TAG_SEGMENT_GROUP = _to_bool(
        other_tagging_cfg.get("tag_segment_group", DEFAULT_OTHER_TAG_SEGMENT_GROUP),
        DEFAULT_OTHER_TAG_SEGMENT_GROUP,
    )
    OTHER_GROUP_SEGMENT = _to_text(
        other_tagging_cfg.get("group_segment", DEFAULT_OTHER_GROUP_SEGMENT),
        DEFAULT_OTHER_GROUP_SEGMENT,
    )
    ACTION_MISSED_DATE_CONTEXT[ACTION_KEY_OTHER_RESOURCE] = _to_bool(
        other_tagging_cfg.get(
            "add_missed_date_context",
            (
                action_default_add_missed_date_context
                if has_action_default_add_missed_date_context
                else DEFAULT_OTHER_ADD_MISSED_DATE_CONTEXT
            ),
        ),
        (
            action_default_add_missed_date_context
            if has_action_default_add_missed_date_context
            else DEFAULT_OTHER_ADD_MISSED_DATE_CONTEXT
        ),
    )
    OTHER_ACTIONS = _normalize_other_actions_with_prompt_defaults(
        other_cfg.get("actions", DEFAULT_OTHER_ACTIONS),
        default_prompt_kind=action_default_prompt_kind if has_action_default_prompt_kind else PROMPT_KIND_NONE,
        default_prompt_number_style=(
            action_default_prompt_number_style
            if has_action_default_prompt_number_style
            else PROMPT_STYLE_NUMBER_ONLY
        ),
        default_prompt_range_block_size=(
            action_default_prompt_range_block_size
            if has_action_default_prompt_range_block_size
            else DEFAULT_TEST_RANGE_BLOCK_SIZE
        ),
        default_prompt_input_items=(
            action_default_prompt_input_items
            if has_action_default_prompt_input_items
            else DEFAULT_FORM_INPUT_ITEMS
        ),
    )
    TEST_RANGE_BLOCK_SIZE = UWORLD_RANGE_BLOCK_SIZE

    include_day_segment_raw = merged_cfg.get(
        "include_day_segment",
        legacy_date_cfg.get(
            "include_day_segment",
            (
                action_default_include_day_segment
                if has_action_default_include_day_segment
                else DEFAULT_INCLUDE_DAY_SEGMENT
            ),
        ),
    )
    INCLUDE_DAY_SEGMENT = _to_bool(include_day_segment_raw, DEFAULT_INCLUDE_DAY_SEGMENT)

    # Hardcoded by request: bank visibility is no longer configurable.
    ENABLED_Q_BANKS = {bank.upper() for bank in DEFAULT_Q_BANKS}


_reload_runtime_config()


def get_missed_month_tag() -> str:
    now = datetime.now()
    base = PRIMARY_MISSED_TAG or DEFAULT_PRIMARY_MISSED_TAG
    month_segment = f"{now.strftime('%m')}_{now.strftime('%B')}"
    tag = f"{base}::{now.year}::{month_segment}"
    if INCLUDE_DAY_SEGMENT:
        tag = f"{tag}::{now.strftime('%d')}"
    return tag


def get_correct_guess_tags() -> list[str]:
    return list(CORRECT_GUESS_TAGS)


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
    if ACTION_MISSED_DATE_CONTEXT.get(action_key, True):
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


def add_nbme_tag(browser, menu):
    if not _is_bank_enabled("NBME"):
        return

    base_tag = _nbme_base_tag()
    action = QAction(f"{SUBSET_2_NAME:<24}", browser)
    if NBME_PROMPT_KIND == PROMPT_KIND_NONE:
        action.triggered.connect(
            lambda _: apply_tags_to_selected_notes(
                browser,
                [base_tag],
                action_key=ACTION_KEY_NBME_FORM_PROMPT,
            )
        )
    elif NBME_PROMPT_KIND == PROMPT_KIND_FORM:
        action.triggered.connect(
            make_form_prompt_handler(
                browser,
                base_tag,
                action_key=ACTION_KEY_NBME_FORM_PROMPT,
                title=PROMPT_TITLE_NBME_FORM,
                label=PROMPT_LABEL_NBME_FORM,
                input_items=NBME_PROMPT_INPUT_ITEMS,
            )
        )
    else:
        action.triggered.connect(
            make_test_prompt_handler(
                browser,
                base_tag,
                action_key=ACTION_KEY_NBME_FORM_PROMPT,
                title=PROMPT_TITLE_NBME_FORM,
                label=PROMPT_LABEL_NBME_FORM,
                number_style=NBME_NUMBER_STYLE,
                range_block_size=NBME_RANGE_BLOCK_SIZE,
            )
        )
    menu.addAction(action)


def add_amboss_tag(browser, menu):
    if not _is_bank_enabled("AMBOSS"):
        return

    action = QAction(f"{AMBOSS_TOP_LEVEL_NAME:<24}", browser)
    if AMBOSS_PROMPT_KIND == PROMPT_KIND_NONE:
        action.triggered.connect(
            lambda _: apply_tags_to_selected_notes(
                browser,
                [AMBOSS_BASE_TAG],
                action_key=ACTION_KEY_AMBOSS_TEST_PROMPT,
            )
        )
    elif AMBOSS_PROMPT_KIND == PROMPT_KIND_FORM:
        action.triggered.connect(
            make_form_prompt_handler(
                browser,
                AMBOSS_BASE_TAG,
                action_key=ACTION_KEY_AMBOSS_TEST_PROMPT,
                title=PROMPT_TITLE_AMBOSS,
                label=PROMPT_LABEL_GENERIC,
                input_items=AMBOSS_PROMPT_INPUT_ITEMS,
            )
        )
    else:
        action.triggered.connect(
            make_test_prompt_handler(
                browser,
                AMBOSS_BASE_TAG,
                action_key=ACTION_KEY_AMBOSS_TEST_PROMPT,
                title=PROMPT_TITLE_AMBOSS,
                label=PROMPT_LABEL_GENERIC,
                number_style=AMBOSS_NUMBER_STYLE,
                range_block_size=AMBOSS_PROMPT_RANGE_BLOCK_SIZE,
            )
        )
    menu.addAction(action)


def add_multi_tag(browser, menu):
    multi_tag = MULTI_MISS_TAG
    add_static_action(
        browser,
        menu,
        f"{ACTION_LABEL_MULTI_MISSED:<24}",
        [multi_tag],
        action_key=ACTION_KEY_MULTI_MISSED,
    )


def add_uworld_tags(browser, menu):
    if not _is_bank_enabled("UWORLD"):
        return

    base = _uw_base_tag()
    if SUBSET_1_NAME and base:
        action = QAction(f"{SUBSET_1_NAME:<24}", browser)
        if UWORLD_PROMPT_KIND == PROMPT_KIND_NONE:
            action.triggered.connect(
                lambda _: apply_tags_to_selected_notes(
                    browser,
                    [base],
                    action_key=ACTION_KEY_UWORLD_TEST_PROMPT,
                )
            )
        elif UWORLD_PROMPT_KIND == PROMPT_KIND_FORM:
            action.triggered.connect(
                make_form_prompt_handler(
                    browser,
                    base,
                    action_key=ACTION_KEY_UWORLD_TEST_PROMPT,
                    title=PROMPT_TITLE_UWORLD,
                    label=PROMPT_LABEL_GENERIC,
                    input_items=UWORLD_PROMPT_INPUT_ITEMS,
                )
            )
        else:
            action.triggered.connect(
                make_test_prompt_handler(
                    browser,
                    base,
                    action_key=ACTION_KEY_UWORLD_TEST_PROMPT,
                    title=PROMPT_TITLE_UWORLD,
                    label=PROMPT_LABEL_GENERIC,
                    number_style=UWORLD_NUMBER_STYLE,
                    range_block_size=UWORLD_RANGE_BLOCK_SIZE,
                )
            )
        menu.addAction(action)


def add_other_resources_actions(browser, menu):
    if not OTHER_ACTIONS:
        return

    action_target_menu = menu
    submenu = None
    if OTHER_SUBMENU_BOOL:
        submenu = QMenu(OTHER_SUBMENU_LABEL, browser)
        submenu_stylesheet = build_context_submenu_item_stylesheet()
        if submenu_stylesheet:
            submenu.setStyleSheet(submenu_stylesheet)
        action_target_menu = submenu

    for item in OTHER_ACTIONS:
        menu_label = str(item.get("menu_label", "")).strip()
        tag_segment = str(item.get("tag_segment", "")).strip()
        if not menu_label or not tag_segment:
            continue

        base_tag = _other_action_base_tag(tag_segment)
        if not base_tag:
            continue

        prompt_kind = _to_prompt_kind(item.get("prompt_kind", PROMPT_KIND_NONE), PROMPT_KIND_NONE)
        prompt_number_style = _to_prompt_number_style(
            item.get("prompt_number_style", PROMPT_STYLE_NUMBER_ONLY),
            PROMPT_STYLE_NUMBER_ONLY,
        )
        prompt_range_block_size = _to_positive_int(
            item.get("prompt_range_block_size", DEFAULT_TEST_RANGE_BLOCK_SIZE),
            DEFAULT_TEST_RANGE_BLOCK_SIZE,
        )
        prompt_input_items = _to_string_list(
            item.get("prompt_input_items"),
            fallback=DEFAULT_FORM_INPUT_ITEMS,
        )

        action = QAction(menu_label, browser)
        if prompt_kind == PROMPT_KIND_NONE:
            action.triggered.connect(
                lambda _, btag=base_tag: apply_tags_to_selected_notes(
                    browser,
                    [btag],
                    action_key=ACTION_KEY_OTHER_RESOURCE,
                )
            )
        elif prompt_kind == PROMPT_KIND_FORM:
            action.triggered.connect(
                make_form_prompt_handler(
                    browser,
                    base_tag,
                    action_key=ACTION_KEY_OTHER_RESOURCE,
                    title=f"Enter {menu_label}",
                    label=PROMPT_LABEL_GENERIC,
                    input_items=prompt_input_items,
                )
            )
        else:
            action.triggered.connect(
                make_test_prompt_handler(
                    browser,
                    base_tag,
                    action_key=ACTION_KEY_OTHER_RESOURCE,
                    title=f"Enter {menu_label}",
                    label=PROMPT_LABEL_GENERIC,
                    number_style=prompt_number_style,
                    range_block_size=prompt_range_block_size,
                )
            )
        action_target_menu.addAction(action)

    if submenu is not None and submenu.actions():
        menu.addMenu(submenu)


def make_form_prompt_handler(
    browser,
    base_tag: str,
    action_key: str,
    title: str | None = None,
    label: str | None = None,
    input_items: list[str] | None = None,
):
    def on_trigger():
        prompt_title = (title or PROMPT_TITLE_GENERIC).strip() or PROMPT_TITLE_GENERIC
        fallback_prompt_label = (label or PROMPT_LABEL_GENERIC).strip() or PROMPT_LABEL_GENERIC

        normalized_items = _to_string_list(
            input_items,
            fallback=DEFAULT_FORM_INPUT_ITEMS,
        )
        if len(normalized_items) > 1:
            selected_item, item_ok = _get_input_dialog_item(
                browser,
                prompt_title,
                "Select item:",
                normalized_items,
                0,
                False,
            )
            if not item_ok:
                return
            form_prefix = str(selected_item).strip() or DEFAULT_FORM_INPUT_ITEMS[0]
        else:
            form_prefix = normalized_items[0]

        prompt_label = _prompt_label_from_input_item(form_prefix, fallback_prompt_label)
        saved_form_value = _get_saved_prompt_input(action_key)
        form_value, ok = _text_prompt_with_default(
            browser,
            prompt_title,
            prompt_label,
            default_text=saved_form_value,
        )
        if not ok:
            return

        normalized_form_value = (form_value or "").strip()
        if normalized_form_value == "":
            _save_prompt_input(action_key, "")
            showInfo(MSG_INVALID_TEST_NUMBER)
            return

        try:
            form_number = int(normalized_form_value)
        except ValueError:
            showInfo(MSG_INVALID_TEST_NUMBER)
            return

        if form_number <= 0:
            showInfo(MSG_INVALID_TEST_NUMBER)
            return
        _save_prompt_input(action_key, normalized_form_value)

        if not browser.selectedNotes():
            showInfo(MSG_NO_NOTES_SELECTED)
            return

        separator = "" if form_prefix.endswith("_") else "_"
        formatted_tag = f"{base_tag}::{form_prefix}{separator}{form_number}"
        apply_tags_to_selected_notes(browser, [formatted_tag], action_key=action_key)

    return on_trigger


def make_test_prompt_handler(
    browser,
    base_tag: str,
    action_key: str,
    title: str | None = None,
    label: str | None = None,
    number_style: str = PROMPT_STYLE_RANGE_THEN_NUMBER,
    range_block_size: int = DEFAULT_TEST_RANGE_BLOCK_SIZE,
):
    """
    number_style:
      - "range_then_number" -> base_tag::<lower-upper>::NN
      - "number_only" -> base_tag::NN

    Blank and non-numeric values resolve to base_tag.
    """

    def on_trigger():
        prompt_title = (title or PROMPT_TITLE_GENERIC).strip() or PROMPT_TITLE_GENERIC
        prompt_label = (label or PROMPT_LABEL_GENERIC).strip() or PROMPT_LABEL_GENERIC
        saved_test_num = _get_saved_prompt_input(action_key)
        test_num, ok = _text_prompt_with_default(
            browser,
            prompt_title,
            prompt_label,
            default_text=saved_test_num,
        )
        if not ok:
            return

        test_num = (test_num or "").strip()
        normalized_number_style = (
            PROMPT_STYLE_RANGE_THEN_NUMBER
            if number_style == PROMPT_STYLE_RANGE_THEN_NUMBER
            else PROMPT_STYLE_NUMBER_ONLY
        )

        if test_num == "":
            _save_prompt_input(action_key, "")
            formatted_tag = f"{base_tag}"
        else:
            try:
                test_number = int(test_num)
            except ValueError:
                formatted_tag = f"{base_tag}"
            else:
                _save_prompt_input(action_key, test_num)
                if normalized_number_style == PROMPT_STYLE_RANGE_THEN_NUMBER:
                    block_size = _to_positive_int(range_block_size, TEST_RANGE_BLOCK_SIZE)
                    lower = ((test_number - 1) // block_size) * block_size + 1
                    upper = lower + block_size - 1
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
