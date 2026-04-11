from __future__ import annotations

import json

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
