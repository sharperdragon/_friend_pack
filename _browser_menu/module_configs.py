from __future__ import annotations

import copy
from typing import Any, Optional

from aqt import mw

from .qid_config_ui import FindQidsSettingsDialog

try:
    # Reuse debug logger from loader.py
    from .loader import _dbg  # type: ignore[attr-defined]
except Exception:
    def _dbg(msg: str) -> None:
        return

try:
    from ..utils.config_manager import ConfigManager as RootConfigManager
except Exception:
    RootConfigManager = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Config mapping: module name -> root config section/keys/defaults
# ---------------------------------------------------------------------------
FIND_QIDS_MODULE_NAME = "Find_QIDs"
FIND_QIDS_ROOT_SECTION = "find_QIDs"
FIND_QIDS_CONFIG_KEYS = (
    "UW_STEP",
    "UW_COMLEX",
    "QID_parent_tag",
    "MISSED_tag",
    "default_missed_only",
)
FIND_QIDS_DEFAULT_CONFIG: dict[str, Any] = {
    "UW_STEP": False,
    "UW_COMLEX": False,
    "QID_parent_tag": "",
    "MISSED_tag": "##Missed-Qs",
    "default_missed_only": False,
}

MODULE_CONFIG_KEYS: dict[str, tuple[str, ...]] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_CONFIG_KEYS,
}
MODULE_CONFIG_SECTIONS: dict[str, str] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_ROOT_SECTION,
}
MODULE_CONFIG_DEFAULTS: dict[str, dict[str, Any]] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_DEFAULT_CONFIG,
}


def _to_bool(value: Any, fallback: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off", ""}:
            return False
    return fallback


def _normalize_module_value(module_name: str, key: str, value: Any) -> Any:
    if module_name == FIND_QIDS_MODULE_NAME and key in {"UW_STEP", "UW_COMLEX", "default_missed_only"}:
        fallback = bool(FIND_QIDS_DEFAULT_CONFIG.get(key, False))
        return _to_bool(value, fallback=fallback)

    if module_name == FIND_QIDS_MODULE_NAME and key == "QID_parent_tag":
        text = str(value or "").strip()
        if text.startswith("tag:re:"):
            text = text[len("tag:re:"):]
        elif text.startswith("tag:"):
            text = text[len("tag:"):]
        text = text.strip().rstrip(":").strip()
        return text

    if module_name == FIND_QIDS_MODULE_NAME and key == "MISSED_tag":
        text = str(value or "").strip()
        if text.startswith("tag:re:"):
            text = text[len("tag:re:"):]
        elif text.startswith("tag:"):
            text = text[len("tag:"):]
        text = text.strip()
        return text or FIND_QIDS_DEFAULT_CONFIG["MISSED_tag"]
    return copy.deepcopy(value)


def _module_default_config(module_name: str) -> dict[str, Any]:
    return copy.deepcopy(MODULE_CONFIG_DEFAULTS.get(module_name, {}))


def _module_keys(module_name: str) -> tuple[str, ...]:
    return MODULE_CONFIG_KEYS.get(module_name, ())


def _module_section(module_name: str) -> Optional[str]:
    return MODULE_CONFIG_SECTIONS.get(module_name)


def _read_root_default_config() -> dict[str, Any]:
    if RootConfigManager is None:
        return {}
    try:
        data = RootConfigManager.load_default_config()
    except Exception as e:
        _dbg(f"module_configs: _read_root_default_config ERROR: {e}")
        return {}
    return data if isinstance(data, dict) else {}


def _read_root_effective_config() -> dict[str, Any]:
    if RootConfigManager is None:
        return {}
    try:
        data = RootConfigManager.load_effective_config()
    except Exception as e:
        _dbg(f"module_configs: _read_root_effective_config ERROR: {e}")
        return {}
    return data if isinstance(data, dict) else {}


def _extract_module_config(source: dict[str, Any], module_name: str) -> dict[str, Any]:
    keys = _module_keys(module_name)
    section_name = _module_section(module_name)
    defaults = _module_default_config(module_name)
    if not keys:
        return defaults

    section_cfg = {}
    if section_name:
        maybe_section = source.get(section_name)
        if isinstance(maybe_section, dict):
            section_cfg = maybe_section

    result = defaults
    for key in keys:
        if key in section_cfg:
            result[key] = _normalize_module_value(module_name, key, section_cfg[key])
    return result


def _load_default_config(module_name: str) -> dict[str, Any]:
    root_defaults = _read_root_default_config()
    default_cfg = _extract_module_config(root_defaults, module_name)
    _dbg(
        f"module_configs: _load_default_config for '{module_name}' "
        f"(keys={list(default_cfg.keys())})"
    )
    return default_cfg


def load_module_config(module_name: str) -> dict[str, Any]:
    root_effective = _read_root_effective_config()
    merged = _extract_module_config(root_effective, module_name)
    _dbg(
        f"module_configs: load_module_config for '{module_name}' "
        f"(keys={list(merged.keys())})"
    )
    return merged


def save_module_config(module_name: str, new_config: dict[str, Any]) -> bool:
    if not isinstance(new_config, dict):
        _dbg(
            f"module_configs: save_module_config skipped for '{module_name}' "
            "(new_config is not an object)"
        )
        return False

    if RootConfigManager is None:
        _dbg("module_configs: save_module_config skipped (RootConfigManager unavailable)")
        return False

    keys = _module_keys(module_name)
    section_name = _module_section(module_name)
    if not keys:
        _dbg(f"module_configs: save_module_config skipped (unknown module '{module_name}')")
        return False

    overrides = RootConfigManager.load_user_overrides()
    if not isinstance(overrides, dict):
        overrides = {}

    if section_name:
        section_overrides = overrides.get(section_name, {})
        if not isinstance(section_overrides, dict):
            section_overrides = {}
        section_overrides = copy.deepcopy(section_overrides)
        for key in keys:
            if key in new_config:
                section_overrides[key] = _normalize_module_value(module_name, key, new_config[key])
        overrides[section_name] = section_overrides
    else:
        for key in keys:
            if key in new_config:
                overrides[key] = _normalize_module_value(module_name, key, new_config[key])

    try:
        ok = RootConfigManager.save_full_config(overrides)
        if not ok:
            _dbg(
                f"module_configs: save_module_config returned False for '{module_name}' "
                f"(keys={list(keys)})"
            )
            return False
        _dbg(
            f"module_configs: save_module_config for '{module_name}' OK "
            f"(saved keys={list(keys)})"
        )
        return True
    except Exception as e:
        _dbg(f"module_configs: save_module_config ERROR for '{module_name}': {e}")
        return False


def open_find_qids_config(_browser: object) -> None:
    """
    Entry point for browser menu action: opens Find_QIDs settings form.
    """
    _dbg("module_configs: open_find_qids_config called")
    existing = getattr(mw, "_friend_pack_find_qids_settings_dialog", None)
    if existing is not None:
        try:
            existing.raise_()
            existing.activateWindow()
            return
        except Exception:
            pass

    default_cfg = _load_default_config(FIND_QIDS_MODULE_NAME)
    merged_cfg = load_module_config(FIND_QIDS_MODULE_NAME)

    dlg = FindQidsSettingsDialog(
        merged_config=merged_cfg,
        default_config=default_cfg,
        title="QID search settings",
        on_save=lambda cfg: save_module_config(FIND_QIDS_MODULE_NAME, cfg),
        on_close=lambda: setattr(mw, "_friend_pack_find_qids_settings_dialog", None),
        parent=mw,
    )
    setattr(mw, "_friend_pack_find_qids_settings_dialog", dlg)
    dlg.show()
