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


def _resolve_addon_name() -> str:
    """Resolve canonical addon key based on package name."""
    pkg = (__package__ or "").strip()
    if pkg:
        return pkg.split(".", 1)[0]
    return FALLBACK_ADDON_NAME


class ConfigManager:
    """Top-level config manager for _friend_pack defaults + overrides."""

    ADDON_NAME = _resolve_addon_name()
    ROOT_DIR = Path(__file__).resolve().parent
    DEFAULT_CONFIG_PATH = ROOT_DIR / DEFAULT_CONFIG_FILENAME
    DEFAULT_DOC_PATH = ROOT_DIR / DEFAULT_CONFIG_DOC_FILENAME

    @classmethod
    def _read_json_file(cls, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

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
        return cls._read_json_file(cls.DEFAULT_CONFIG_PATH)

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

        return data if isinstance(data, dict) else {}

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

        addon_manager = cls._get_addon_manager()
        if addon_manager is None:
            return False

        try:
            addon_manager.writeConfig(cls.ADDON_NAME, new_config)
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

        next_config = cls.load_effective_config()
        next_config[section] = copy.deepcopy(section_config)
        return cls.save_full_config(next_config)

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
