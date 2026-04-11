from __future__ import annotations

import copy
from typing import Any

from ..config_manager import ConfigManager as RootConfigManager


class ConfigManager:
    """
    Compatibility wrapper for legacy `_change_notes_shua` imports.

    Runtime config now comes only from the root `_friend_pack/config.json`
    defaults plus profile overrides in Anki's config bucket.
    """

    ROOT_ADDON_NAME = RootConfigManager.ADDON_NAME

    def __init__(self, addon_name: str, global_config_name: str = None):
        self.addon_name = addon_name
        self.global_config_name = global_config_name
        self.last_load_errors: list[str] = []
        self.config = self.load_config()

    def reload(self):
        self.config = self.load_config()
        return self.config

    def load(self):
        return self.load_config()

    @classmethod
    def load_user_overrides(cls) -> dict:
        return RootConfigManager.load_user_overrides()

    @classmethod
    def load_effective_config(cls) -> tuple[dict, list[str]]:
        return RootConfigManager.load_effective_config(), []

    @classmethod
    def list_sections(cls) -> list[str]:
        effective = RootConfigManager.load_effective_config()
        return sorted(k for k in effective.keys() if isinstance(k, str))

    @classmethod
    def get_default_section(cls, section: str) -> dict:
        defaults = RootConfigManager.load_default_config()
        data = defaults.get(section, {})
        return copy.deepcopy(data) if isinstance(data, dict) else {}

    @classmethod
    def get_override_section(cls, section: str) -> dict:
        overrides = RootConfigManager.load_user_overrides()
        data = overrides.get(section, {})
        return copy.deepcopy(data) if isinstance(data, dict) else {}

    @classmethod
    def get_effective_section(cls, section: str) -> dict:
        data = RootConfigManager.get_section(section, default={})
        return data if isinstance(data, dict) else {}

    @classmethod
    def get_effective_section_with_aliases(
        cls,
        section: str,
        aliases: list[str] | tuple[str, ...] = (),
    ) -> dict:
        effective = RootConfigManager.load_effective_config()
        for key in (section, *aliases):
            data = effective.get(key)
            if isinstance(data, dict):
                return copy.deepcopy(data)
        return {}

    @classmethod
    def save_section_override(cls, section: str, section_override: dict):
        if not isinstance(section_override, dict):
            raise ValueError(f"Section override for '{section}' must be a JSON object.")
        RootConfigManager.save_section(section, section_override)

    @classmethod
    def clear_section_override(cls, section: str):
        overrides = RootConfigManager.load_user_overrides()
        if section in overrides:
            del overrides[section]
            RootConfigManager.save_full_config(overrides)

    @classmethod
    def clear_all_overrides(cls):
        RootConfigManager.reset_overrides()

    def load_config(self):
        effective = RootConfigManager.load_effective_config()
        self.last_load_errors = []

        if self.addon_name == self.ROOT_ADDON_NAME:
            if self.global_config_name:
                target = effective.get(self.global_config_name, {})
                return copy.deepcopy(target) if isinstance(target, dict) else {}
            return copy.deepcopy(effective)

        section_data = effective.get(self.addon_name, {})
        section_dict = copy.deepcopy(section_data) if isinstance(section_data, dict) else {}

        if self.global_config_name:
            global_section = effective.get(self.global_config_name, {})
            global_dict = copy.deepcopy(global_section) if isinstance(global_section, dict) else {}
            return self.deep_merge_dicts(global_dict, section_dict)

        return section_dict

    def save_config(self, new_config):
        if not isinstance(new_config, dict):
            raise ValueError("Configuration must be a JSON object.")

        if self.addon_name == self.ROOT_ADDON_NAME:
            RootConfigManager.save_full_config(new_config)
        else:
            RootConfigManager.save_section(self.addon_name, new_config)

        self.config = copy.deepcopy(new_config)

    def get(self, key, default=None):
        if not isinstance(self.config, dict):
            return default
        return self.config.get(key, default)

    def set(self, key, value):
        if not isinstance(self.config, dict):
            self.config = {}
        self.config[key] = value
        self.save_config(self.config)

    @staticmethod
    def deep_merge_dicts(base: dict, override: dict) -> dict:
        return RootConfigManager.deep_merge_dicts(base, override)
