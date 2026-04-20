from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

# pyright: reportMissingImports=false
# mypy: disable_error_code=import
try:
    from aqt import mw
except Exception:  # pragma: no cover - defensive import fallback
    mw = None  # type: ignore[assignment]


# =========================
# User-tunable constants
# =========================
FALLBACK_ADDON_NAME = "_friend_pack"
DEFAULT_CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG_DOC_FILENAME = "config.md"
DEFAULT_CONFIG_FALLBACK: dict[str, Any] = {
    "add_custom_tags": {
        "submenu_label": "Custom Tags",
        "presets": [],
    },
    "add_missed_tags": {
        "menu_label": "Missed Tags",
        "primary_missed_tag": "##Missed-Qs",
        "include_day_segment": True,
        "action_defaults": {},
        "actions": {},
    },
    "browser_menu": {
        "top_menu_title": "Custom",
    },
    "find_QIDs": {
        "UW_STEP": False,
        "UW_COMLEX": False,
        "QID_parent_tag": "",
        "MISSED_tag": "##Missed-Qs",
        "default_missed_only": False,
    },
}


def _resolve_addon_name() -> str:
    """Resolve canonical addon key based on package name."""
    pkg = (__package__ or "").strip()
    if pkg:
        return pkg.split(".", 1)[0]
    return FALLBACK_ADDON_NAME


class ConfigManager:
    """Top-level config manager for _friend_pack defaults + overrides."""

    ADDON_NAME = _resolve_addon_name()
    PACKAGE_DIR = Path(__file__).resolve().parent
    ADDON_ROOT_DIR = PACKAGE_DIR.parent
    DEFAULT_CONFIG_PATH = ADDON_ROOT_DIR / DEFAULT_CONFIG_FILENAME
    DEFAULT_DOC_PATH = ADDON_ROOT_DIR / DEFAULT_CONFIG_DOC_FILENAME

    @staticmethod
    def _ensure_json_object(value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    @classmethod
    def _read_json_file(cls, path: Path) -> dict[str, Any]:
        if not path.exists() or not path.is_file():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return cls._ensure_json_object(data)

    @classmethod
    def _sanitize_default_config(cls, raw: dict[str, Any]) -> dict[str, Any]:
        merged = cls.deep_merge_dicts(DEFAULT_CONFIG_FALLBACK, cls._ensure_json_object(raw))
        for section_name, section_default in DEFAULT_CONFIG_FALLBACK.items():
            if isinstance(section_default, dict) and not isinstance(merged.get(section_name), dict):
                merged[section_name] = copy.deepcopy(section_default)
        return merged

    @classmethod
    def _addon_manager_available(cls) -> bool:
        try:
            return mw is not None and hasattr(mw, "addonManager")
        except Exception:
            return False

    @classmethod
    def _get_addon_manager(cls) -> Any | None:
        """Return Anki's addonManager when available, otherwise None."""
        if not cls._addon_manager_available():
            return None
        try:
            return getattr(mw, "addonManager", None)
        except Exception:
            return None

    @classmethod
    def deep_merge_dicts(cls, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Recursively merge dictionaries. Lists/scalars are replaced."""
        merged = copy.deepcopy(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(merged.get(key), dict):
                merged[key] = cls.deep_merge_dicts(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged

    @classmethod
    def load_default_config(cls) -> dict[str, Any]:
        """Load shipped defaults from root config.json."""
        raw = cls._read_json_file(cls.DEFAULT_CONFIG_PATH)
        return cls._sanitize_default_config(raw)

    @classmethod
    def load_user_overrides(cls) -> dict[str, Any]:
        """Load user-level config bucket from Anki addon manager."""
        addon_manager = cls._get_addon_manager()
        if addon_manager is None:
            return {}

        try:
            data = addon_manager.getConfig(cls.ADDON_NAME) or {}
        except Exception:
            return {}

        # Defensive copy so callers never mutate addon-manager-owned objects in place.
        return copy.deepcopy(cls._ensure_json_object(data))

    @classmethod
    def load_effective_config(cls) -> dict[str, Any]:
        """Load defaults merged with current profile overrides."""
        defaults = cls.load_default_config()
        overrides = cls.load_user_overrides()
        return cls.deep_merge_dicts(defaults, overrides)

    @classmethod
    def get_section(cls, section: str, default: Any = None) -> Any:
        """Return a deep-copied section from effective config."""
        cfg = cls.load_effective_config()
        if section in cfg:
            return copy.deepcopy(cfg[section])
        return copy.deepcopy(default)

    @classmethod
    def save_full_config(cls, new_config: dict[str, Any]) -> bool:
        """Persist full config into the addon's user config bucket."""
        if not isinstance(new_config, dict):
            raise ValueError("Top-level config must be a JSON object.")

        # Ensure config can be serialized as JSON before attempting write.
        try:
            json.dumps(new_config, ensure_ascii=False)
        except Exception:
            return False

        addon_manager = cls._get_addon_manager()
        if addon_manager is None:
            return False

        try:
            addon_manager.writeConfig(cls.ADDON_NAME, copy.deepcopy(new_config))
            return True
        except Exception:
            return False

    @classmethod
    def save_section(cls, section: str, section_config: dict[str, Any]) -> bool:
        """Update a single top-level section while preserving other keys."""
        if not isinstance(section, str) or not section.strip():
            raise ValueError("Section name must be a non-empty string.")
        if not isinstance(section_config, dict):
            raise ValueError("Section config must be a JSON object.")

        # Save section changes into user overrides only (do not persist full defaults).
        next_overrides = cls.load_user_overrides()
        next_overrides[section] = copy.deepcopy(section_config)
        return cls.save_full_config(next_overrides)

    @classmethod
    def reset_overrides(cls) -> bool:
        """Clear user overrides for this addon in the current profile."""
        addon_manager = cls._get_addon_manager()
        if addon_manager is None:
            return False

        try:
            addon_manager.writeConfig(cls.ADDON_NAME, {})
            return True
        except Exception:
            return False

    @classmethod
    def load_config_markdown(cls) -> str:
        """Load the root config markdown help text."""
        try:
            return cls.DEFAULT_DOC_PATH.read_text(encoding="utf-8")
        except Exception:
            return ""
