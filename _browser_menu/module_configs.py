from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Optional

from aqt import mw

from .config_ui import ModuleConfigDialog, FindQidsSettingsDialog

try:
    # Reuse debug logger from loader.py
    from .loader import _dbg  # type: ignore[attr-defined]
except Exception:
    def _dbg(msg: str) -> None:
        return

try:
    from ..config_manager import ConfigManager as RootConfigManager
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
    "TAG_PREFIX",
    "MISSED_tag",
    "default_missed_only",
)
FIND_QIDS_DEFAULT_CONFIG: dict[str, Any] = {
    "UW_STEP": False,
    "UW_COMLEX": False,
    "QID_parent_tag": "",
    "TAG_PREFIX": "#UWorld::\\w+::",
    "MISSED_tag": "##Missed-Qs",
    "default_missed_only": False,
}

MODULE_CONFIG_KEYS: dict[str, tuple[str, ...]] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_CONFIG_KEYS,
}
MODULE_CONFIG_SECTIONS: dict[str, str] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_ROOT_SECTION,
}
MODULE_CONFIG_LEGACY_ALIASES: dict[str, dict[str, tuple[str, ...]]] = {
    FIND_QIDS_MODULE_NAME: {
        "MISSED_tag": ("MISSED_FILTER", "MISSED_FILTER_TAG"),
    },
}
MODULE_CONFIG_DEFAULTS: dict[str, dict[str, Any]] = {
    FIND_QIDS_MODULE_NAME: FIND_QIDS_DEFAULT_CONFIG,
}
MODULE_CONFIG_DOC_PATHS: dict[str, str] = {
    FIND_QIDS_MODULE_NAME: "config.md",
}


def _normalize_module_value(module_name: str, key: str, value: Any) -> Any:
    if module_name == FIND_QIDS_MODULE_NAME and key in {"QID_parent_tag", "TAG_PREFIX"}:
        text = str(value or "").strip()
        if text.startswith("tag:re:"):
            text = text[len("tag:re:"):]
        elif text.startswith("tag:"):
            text = text[len("tag:"):]
        text = text.strip().rstrip(":").strip()
        if key == "QID_parent_tag":
            return text
        return text or FIND_QIDS_DEFAULT_CONFIG["TAG_PREFIX"].rstrip(":")

    if module_name == FIND_QIDS_MODULE_NAME and key == "MISSED_tag":
        text = str(value or "").strip()
        if text.startswith("tag:re:"):
            text = text[len("tag:re:"):]
        elif text.startswith("tag:"):
            text = text[len("tag:"):]
        text = text.strip()
        return text or FIND_QIDS_DEFAULT_CONFIG["MISSED_tag"]
    return copy.deepcopy(value)


def _module_md_path(module_name: str) -> Path:
    base_dir = Path(__file__).resolve().parent
    mapped_path = MODULE_CONFIG_DOC_PATHS.get(module_name)
    if mapped_path:
        return base_dir / mapped_path
    return base_dir / module_name / "config.md"


def _load_markdown(path: Path) -> str:
    _dbg(f"module_configs: _load_markdown -> {path}")
    if not path.exists():
        _dbg(f"module_configs: _load_markdown missing -> {path}")
        return ""
    try:
        text = path.read_text(encoding="utf-8")
        _dbg(f"module_configs: _load_markdown OK ({path}, length={len(text)})")
        return text
    except Exception as e:
        _dbg(f"module_configs: _load_markdown ERROR ({path}): {e}")
        return ""


def _module_default_config(module_name: str) -> dict[str, Any]:
    return copy.deepcopy(MODULE_CONFIG_DEFAULTS.get(module_name, {}))


def _module_keys(module_name: str) -> tuple[str, ...]:
    return MODULE_CONFIG_KEYS.get(module_name, ())


def _module_section(module_name: str) -> Optional[str]:
    return MODULE_CONFIG_SECTIONS.get(module_name)


def _module_aliases(module_name: str) -> dict[str, tuple[str, ...]]:
    return MODULE_CONFIG_LEGACY_ALIASES.get(module_name, {})


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
    aliases = _module_aliases(module_name)
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
        elif key in source:
            # Legacy fallback for old flat configs.
            result[key] = _normalize_module_value(module_name, key, source[key])
        else:
            for alias_key in aliases.get(key, ()):
                if alias_key in section_cfg:
                    result[key] = _normalize_module_value(module_name, key, section_cfg[alias_key])
                    break
                if alias_key in source:
                    result[key] = _normalize_module_value(module_name, key, source[alias_key])
                    break
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


def save_module_config(module_name: str, new_config: dict[str, Any]) -> None:
    if RootConfigManager is None:
        _dbg("module_configs: save_module_config skipped (RootConfigManager unavailable)")
        return

    keys = _module_keys(module_name)
    section_name = _module_section(module_name)
    if not keys:
        _dbg(f"module_configs: save_module_config skipped (unknown module '{module_name}')")
        return

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
        RootConfigManager.save_full_config(overrides)
        _dbg(
            f"module_configs: save_module_config for '{module_name}' OK "
            f"(saved keys={list(keys)})"
        )
    except Exception as e:
        _dbg(f"module_configs: save_module_config ERROR for '{module_name}': {e}")


def open_module_config_dialog(module_name: str, title: Optional[str] = None) -> None:
    """
    Open a JSON config editor dialog for a supported module.

    Runtime values are loaded from root config.json defaults + profile overrides.
    """
    _dbg(f"module_configs: open_module_config_dialog START for '{module_name}'")

    default_cfg = _load_default_config(module_name)
    merged_cfg = load_module_config(module_name)
    md_text = _load_markdown(_module_md_path(module_name))
    window_title = title or f"{module_name} - Config"

    dlg = ModuleConfigDialog(
        module_name=module_name,
        merged_config=merged_cfg,
        default_config=default_cfg,
        md_text=md_text,
        title=window_title,
        parent=mw,
    )

    _dbg(f"module_configs: open_module_config_dialog EXEC for '{module_name}'")
    if dlg.exec():
        new_cfg = dlg.result_config()
        if new_cfg is not None:
            save_module_config(module_name, new_cfg)


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
