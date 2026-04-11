"""Unified addon entrypoint for _friend_pack."""

from __future__ import annotations

import copy
from typing import Any

from aqt import mw


def _resolve_canonical_config_key() -> str:
    """Use the installed addon folder/package name as the config bucket key."""
    pkg = (__package__ or "").strip()
    if pkg:
        return pkg.split(".", 1)[0]

    name = (__name__ or "").strip()
    if name and name != "__main__":
        return name.split(".", 1)[0]

    return "_friend_pack"


CANONICAL_CONFIG_KEY = _resolve_canonical_config_key()
LEGACY_CONFIG_KEYS = ("_browser_menu", "_change_notes_shua", "_anki_friend_pack")


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _read_config_bucket(addon_key: str) -> dict[str, Any]:
    try:
        data = mw.addonManager.getConfig(addon_key) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _migrate_legacy_config_if_needed() -> None:
    try:
        if mw is None or not hasattr(mw, "addonManager"):
            return
    except Exception:
        return

    canonical = _read_config_bucket(CANONICAL_CONFIG_KEY)

    merged_legacy: dict[str, Any] = {}
    for key in LEGACY_CONFIG_KEYS:
        merged_legacy = _deep_merge(merged_legacy, _read_config_bucket(key))

    merged = _deep_merge(merged_legacy, canonical)
    if merged != canonical:
        try:
            mw.addonManager.writeConfig(CANONICAL_CONFIG_KEY, merged)
        except Exception:
            return


_migrate_legacy_config_if_needed()

# Register top-level config window menu action (defensive: never block addon init).
try:
    from .config_window import register_friend_pack_config_menu  # noqa: E402

    register_friend_pack_config_menu()
except Exception:
    pass

# Import both internal addons to register their hooks.
from . import _browser_menu  # noqa: E402,F401
from . import _change_notes  # noqa: E402,F401
