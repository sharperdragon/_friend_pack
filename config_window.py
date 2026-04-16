from __future__ import annotations

import json
from typing import Any

# pyright: reportMissingImports=false
# mypy: disable_error_code=import
from aqt import mw
from aqt.qt import (
    QAction,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSplitter,
    Qt,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import showInfo

from .config_manager import ConfigManager


# =========================
# User-tunable constants
# =========================
MENU_LABEL = "Friend Pack Config"
WINDOW_TITLE = "Friend Pack Config"
REGISTER_FLAG_ATTR = "_friend_pack_config_menu_registered"
REGISTER_ACTION_ATTR = "_friend_pack_config_menu_action"

WINDOW_MARGIN_PX = 60
EDITOR_MIN_WIDTH = 420
EDITOR_MIN_HEIGHT = 520
HELP_MIN_WIDTH = 260
HELP_MIN_HEIGHT = 420


class FriendPackConfigDialog(QDialog):
    """Top-level JSON config editor for _friend_pack."""

    def __init__(self, parent=None):
        super().__init__(parent or mw)

        self._default_config = ConfigManager.load_default_config()
        self._effective_config = ConfigManager.load_effective_config()
        self._help_md = ConfigManager.load_config_markdown()

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self._init_geometry()
        self._build_ui()

    def _init_geometry(self) -> None:
        try:
            screen = mw.app.primaryScreen().availableGeometry()
            margin = WINDOW_MARGIN_PX
            self.setGeometry(
                screen.x() + margin,
                screen.y() + margin,
                max(700, screen.width() - 2 * margin),
                max(500, screen.height() - 2 * margin),
            )
        except Exception:
            self.resize(1100, 760)

    def _build_ui(self) -> None:
        root_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Configuration Settings"))

        self.config_editor = QTextEdit()
        self.config_editor.setMinimumSize(EDITOR_MIN_WIDTH, EDITOR_MIN_HEIGHT)
        self.config_editor.setPlainText(
            json.dumps(self._effective_config or {}, indent=4, ensure_ascii=False)
        )
        left_layout.addWidget(self.config_editor, stretch=6)

        btn_row = QHBoxLayout()

        restore_btn = QPushButton("Restore Defaults")
        restore_btn.clicked.connect(self.restore_defaults)
        btn_row.addWidget(restore_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_config)
        btn_row.addWidget(save_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        left_layout.addLayout(btn_row)

        left_widget = QWidget()
        left_widget.setMinimumWidth(EDITOR_MIN_WIDTH)
        left_widget.setLayout(left_layout)

        self.help_view = QTextBrowser()
        self.help_view.setMinimumSize(HELP_MIN_WIDTH, HELP_MIN_HEIGHT)
        self.help_view.setOpenExternalLinks(True)
        self._render_help_markdown()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.help_view)

        initial_left = max(480, int(self.width() * 0.5))
        initial_right = max(300, self.width() - initial_left)
        splitter.setSizes([initial_left, initial_right])

        root_layout.addWidget(splitter)
        self.setLayout(root_layout)

    def _render_help_markdown(self) -> None:
        text = self._help_md.strip()
        if not text:
            text = "# No config.md found"

        if hasattr(self.help_view, "setMarkdown"):
            self.help_view.setMarkdown(text)
        else:
            self.help_view.setPlainText(text)

    @staticmethod
    def _type_name(value: object) -> str:
        return type(value).__name__

    def _validate_config_structure(self, cfg: dict[str, Any]) -> list[str]:
        """
        Lightweight structural checks to prevent runtime-breaking saves.
        """
        errors: list[str] = []

        def section_dict(section_name: str) -> dict[str, Any] | None:
            value = cfg.get(section_name)
            if value is None:
                return None
            if not isinstance(value, dict):
                errors.append(
                    f"Invalid `{section_name}`: expected object, got {self._type_name(value)}."
                )
                return None
            return value

        def expect_string(container: dict[str, Any], key: str, path: str) -> None:
            if key in container and not isinstance(container[key], str):
                errors.append(
                    f"Invalid `{path}`: expected string, got {self._type_name(container[key])}."
                )

        def expect_bool(container: dict[str, Any], key: str, path: str) -> None:
            if key in container and type(container[key]) is not bool:
                errors.append(
                    f"Invalid `{path}`: expected boolean, got {self._type_name(container[key])}."
                )

        def expect_int(container: dict[str, Any], key: str, path: str) -> None:
            if key in container and (not isinstance(container[key], int) or isinstance(container[key], bool)):
                errors.append(
                    f"Invalid `{path}`: expected integer, got {self._type_name(container[key])}."
                )

        def expect_string_list(value: Any, path: str) -> None:
            if not isinstance(value, list):
                errors.append(f"Invalid `{path}`: expected array of strings, got {self._type_name(value)}.")
                return
            for idx, item in enumerate(value):
                if not isinstance(item, str):
                    errors.append(
                        f"Invalid `{path}[{idx}]`: expected string, got {self._type_name(item)}."
                    )
                    break

        add_custom_tags = section_dict("add_custom_tags")
        if add_custom_tags is not None:
            expect_string(add_custom_tags, "submenu_label", "add_custom_tags.submenu_label")
            if "presets" in add_custom_tags:
                presets = add_custom_tags["presets"]
                if not isinstance(presets, list):
                    errors.append(
                        f"Invalid `add_custom_tags.presets`: expected array, got {self._type_name(presets)}."
                    )
                else:
                    for idx, preset in enumerate(presets):
                        if not isinstance(preset, dict):
                            errors.append(
                                f"Invalid `add_custom_tags.presets[{idx}]`: expected object, got {self._type_name(preset)}."
                            )
                            continue
                        expect_string(preset, "label", f"add_custom_tags.presets[{idx}].label")
                        if "tags" in preset:
                            expect_string_list(preset["tags"], f"add_custom_tags.presets[{idx}].tags")

        add_missed_tags = section_dict("add_missed_tags")
        if add_missed_tags is not None:
            defaults = add_missed_tags.get("defaults")
            if defaults is not None:
                if not isinstance(defaults, dict):
                    errors.append(
                        f"Invalid `add_missed_tags.defaults`: expected object, got {self._type_name(defaults)}."
                    )
                else:
                    expect_string(defaults, "menu_label", "add_missed_tags.defaults.menu_label")

            actions = add_missed_tags.get("actions")
            if actions is not None:
                if not isinstance(actions, dict):
                    errors.append(
                        f"Invalid `add_missed_tags.actions`: expected object, got {self._type_name(actions)}."
                    )
                else:
                    def action_dict(action_name: str) -> dict[str, Any] | None:
                        action_value = actions.get(action_name)
                        if action_value is None:
                            return None
                        if not isinstance(action_value, dict):
                            errors.append(
                                f"Invalid `add_missed_tags.actions.{action_name}`: expected object, got {self._type_name(action_value)}."
                            )
                            return None
                        return action_value

                    base = action_dict("base")
                    if base is not None:
                        expect_string(base, "label", "add_missed_tags.actions.base.label")
                        if "tags" in base:
                            expect_string_list(base["tags"], "add_missed_tags.actions.base.tags")

                    uworld = action_dict("uworld")
                    if uworld is not None:
                        expect_string(uworld, "label", "add_missed_tags.actions.uworld.label")
                        if "base_tags" in uworld:
                            expect_string_list(uworld["base_tags"], "add_missed_tags.actions.uworld.base_tags")
                        expect_string(uworld, "default_tag_prefix", "add_missed_tags.actions.uworld.default_tag_prefix")
                        expect_int(uworld, "test_range_block_size", "add_missed_tags.actions.uworld.test_range_block_size")

                    nbme = action_dict("nbme")
                    if nbme is not None:
                        expect_string(nbme, "label", "add_missed_tags.actions.nbme.label")
                        if "base_tags" in nbme:
                            expect_string_list(nbme["base_tags"], "add_missed_tags.actions.nbme.base_tags")
                        expect_string(nbme, "default_tag_prefix", "add_missed_tags.actions.nbme.default_tag_prefix")

                    amboss = action_dict("amboss")
                    if amboss is not None:
                        expect_string(amboss, "label", "add_missed_tags.actions.amboss.label")
                        expect_string(amboss, "base_tag", "add_missed_tags.actions.amboss.base_tag")
                        expect_string(amboss, "number_style", "add_missed_tags.actions.amboss.number_style")
                        expect_bool(amboss, "remove_from_other_menu", "add_missed_tags.actions.amboss.remove_from_other_menu")

                    multi_missed = action_dict("multi_missed")
                    if multi_missed is not None:
                        expect_string(multi_missed, "label", "add_missed_tags.actions.multi_missed.label")
                        expect_string(multi_missed, "tag_segment", "add_missed_tags.actions.multi_missed.tag_segment")

                    key_info = action_dict("key_info")
                    if key_info is not None:
                        expect_string(key_info, "label", "add_missed_tags.actions.key_info.label")
                        expect_string(key_info, "tag_base", "add_missed_tags.actions.key_info.tag_base")

                    correct_guess = action_dict("correct_guess")
                    if correct_guess is not None:
                        expect_string(correct_guess, "label", "add_missed_tags.actions.correct_guess.label")
                        if "tags" in correct_guess:
                            expect_string_list(correct_guess["tags"], "add_missed_tags.actions.correct_guess.tags")

                    other = action_dict("other")
                    if other is not None:
                        if "resources" in other:
                            expect_string_list(other["resources"], "add_missed_tags.actions.other.resources")
                        expect_string(other, "tag_suffix", "add_missed_tags.actions.other.tag_suffix")

            if "Q_Banks" in add_missed_tags:
                expect_string_list(add_missed_tags["Q_Banks"], "add_missed_tags.Q_Banks")

            date_cfg = add_missed_tags.get("date")
            if date_cfg is not None:
                if not isinstance(date_cfg, dict):
                    errors.append(
                        f"Invalid `add_missed_tags.date`: expected object, got {self._type_name(date_cfg)}."
                    )
                else:
                    expect_bool(
                        date_cfg,
                        "include_day_segment",
                        "add_missed_tags.date.include_day_segment",
                    )

        browser_menu = section_dict("browser_menu")
        if browser_menu is not None:
            expect_string(browser_menu, "top_menu_title", "browser_menu.top_menu_title")

        find_qids = section_dict("find_QIDs")
        if find_qids is not None:
            expect_bool(find_qids, "UW_STEP", "find_QIDs.UW_STEP")
            expect_bool(find_qids, "UW_COMLEX", "find_QIDs.UW_COMLEX")
            expect_string(find_qids, "QID_parent_tag", "find_QIDs.QID_parent_tag")
            expect_string(find_qids, "TAG_PREFIX", "find_QIDs.TAG_PREFIX")
            expect_string(find_qids, "MISSED_tag", "find_QIDs.MISSED_tag")
            expect_bool(find_qids, "default_missed_only", "find_QIDs.default_missed_only")

        return errors

    def restore_defaults(self) -> None:
        self.config_editor.setPlainText(
            json.dumps(self._default_config or {}, indent=4, ensure_ascii=False)
        )

    def save_config(self) -> None:
        raw = self.config_editor.toPlainText()

        try:
            cfg = json.loads(raw)
        except json.JSONDecodeError as exc:
            showInfo(f"Error: Invalid JSON format.\n\n{exc}")
            return

        if not isinstance(cfg, dict):
            showInfo("Error: Top-level JSON must be an object (dictionary).")
            return

        validation_errors = self._validate_config_structure(cfg)
        if validation_errors:
            shown_errors = validation_errors[:12]
            more_count = len(validation_errors) - len(shown_errors)
            details = "\n".join(f"- {err}" for err in shown_errors)
            if more_count > 0:
                details += f"\n- ...and {more_count} more issue(s)."
            showInfo(f"Error: Config validation failed.\n\n{details}")
            return

        ok = ConfigManager.save_full_config(cfg)
        if not ok:
            showInfo(
                "Unable to save config through Anki addon manager. "
                "Make sure Anki is fully initialized."
            )
            return

        self.accept()


def open_friend_pack_config_window(parent=None) -> None:
    """Open the Friend Pack top-level config dialog."""
    dlg = FriendPackConfigDialog(parent=parent or mw)
    dlg.exec()


def register_friend_pack_config_menu() -> bool:
    """Register Tools -> Friend Pack Config once per Anki session."""
    try:
        if mw is None or not hasattr(mw, "form") or not hasattr(mw.form, "menuTools"):
            return False
    except Exception:
        return False

    if getattr(mw, REGISTER_FLAG_ATTR, False):
        return True

    try:
        action = QAction(MENU_LABEL, mw)
        action.triggered.connect(lambda _checked=False: open_friend_pack_config_window(mw))
        mw.form.menuTools.addAction(action)

        setattr(mw, REGISTER_ACTION_ATTR, action)
        setattr(mw, REGISTER_FLAG_ATTR, True)
        return True
    except Exception:
        return False
