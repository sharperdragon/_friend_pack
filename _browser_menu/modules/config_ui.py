import json
from importlib import import_module
from typing import Callable, Optional

from aqt.qt import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
    QSplitter,
    Qt,
    QWidget,
    QTextEdit,
    QLineEdit,
    QRadioButton,
    QButtonGroup,
    QDialogButtonBox,
)
from aqt import mw
from aqt.utils import showInfo


MARKDOWN_MODULE_NAME = "markdown"

FIND_QIDS_SETTINGS_WINDOW_WIDTH = 640
FIND_QIDS_SETTINGS_WINDOW_HEIGHT = 240
FIND_QIDS_SETTINGS_MIN_WIDTH = 560
FIND_QIDS_SETTINGS_MIN_HEIGHT = 220
FIND_QIDS_SETTINGS_TOP_OFFSET_RATIO = 0.04
FIND_QIDS_SETTINGS_TOP_OFFSET_MIN = 16
FIND_QIDS_FIELD_LABEL_WIDTH = 130
FIND_QIDS_FIELD_MIN_HEIGHT = 28
FIND_QIDS_GROUP_VERTICAL_SPACING = 8
FIND_QIDS_GROUP_HORIZONTAL_SPACING = 12
FIND_QIDS_ROOT_SPACING = 8
FIND_QIDS_ROOT_MARGIN = 6
DEFAULT_MISSED_TAG = "##Missed-Qs"
FIND_QIDS_LABEL_UWORLD_VERSION = "UWorld version"
FIND_QIDS_LABEL_QID_PARENT_TAG = "QID parent tag"
FIND_QIDS_LABEL_MISSED_QUESTIONS_TAG = "Missed questions tag"


def _markdown_to_html(md_text: str) -> str:
    """Convert markdown text to HTML when the optional markdown package is available."""
    try:
        markdown_module = import_module(MARKDOWN_MODULE_NAME)
        to_html = getattr(markdown_module, "markdown", None)
        if callable(to_html):
            return str(to_html(md_text))
    except Exception:
        pass
    return md_text


class ModuleConfigDialog(QDialog):
    """
    Generic module config dialog used by _browser_menu.

    All file/path logic is handled in module_configs.py; this class is only
    responsible for:
      - rendering the merged JSON config
      - rendering the markdown help text
      - providing Restore Defaults based on an in-memory default_config dict
      - validating JSON on Save and returning the edited dict
    """

    def __init__(
        self,
        module_name: str,
        merged_config: dict,
        default_config: dict,
        md_text: str,
        title: str,
        parent=None,
    ):
        super().__init__(parent or mw)

        self._module_name = module_name
        self._default_config = default_config or {}
        self._parsed_config: Optional[dict] = None
        self._splitter: Optional[QSplitter] = None

        # Overall window: start near full-screen but with a fixed margin on each side
        screen = mw.app.primaryScreen().availableGeometry()
        margin = 50  # pixels of padding between dialog and screen edges
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setGeometry(  # x, y, width, height
            screen.x() + margin,
            screen.y() + margin,
            screen.width() - 2 * margin,
            screen.height() - 2 * margin,
        )

        # === Left panel: JSON config editor ===
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Configuration Settings"))

        self.config_editor = QTextEdit()
        self.config_editor.setPlainText(
            json.dumps(merged_config or {}, indent=4, ensure_ascii=False)
        )
        # * JSON editor minimum size: prevents the text area from collapsing too small
        #   width = 300px, height = 300px; actual size can grow beyond this
        self.config_editor.setMinimumSize(300, 500)
        left_panel.addWidget(self.config_editor, stretch=6)

        # Buttons: Restore Defaults / Save
        button_layout = QHBoxLayout()
        restore_button = QPushButton("Restore Defaults")
        restore_button.clicked.connect(self.restore_defaults)
        button_layout.addWidget(restore_button)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_config)
        button_layout.addWidget(save_button)

        left_panel.addLayout(button_layout)

        # === Right panel: markdown / help text ===
        self.help_text = QTextBrowser()
        self.help_text.setOpenExternalLinks(True)

        if md_text:
            try:
                html = _markdown_to_html(md_text)
            except Exception:
                # Fallback: just show raw text if markdown conversion fails
                html = md_text
        else:
            html = "<b>No config.md found for this module.</b>"

        self.help_text.setHtml(html)
        self.help_text.setMinimumSize(200, 400)
        self.help_text.setStyleSheet(
            """
            QTextBrowser {
                background: transparent;
                border: none;
                padding: 2px;
                margin: 2px;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 3px;
                margin: 0px 2px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(100, 100, 100, 0.4);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(100, 100, 100, 0.7);
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            """
        )

        # === Splitter layout (unchanged) ===
        left_widget = QWidget()
        # * Container for JSON editor and buttons
        #   This minimum width works together with the splitter sizes below
        #   to avoid squashing the editor too much when the window is narrow.
        left_widget.setMinimumWidth(300)
        left_widget.setLayout(left_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.help_text)
        self._splitter = splitter

        # * Initial splitter setup:
        #   - Give the config editor roughly half of the dialog width
        #   - But never let it be narrower than 450px
        #   - Keep the guide pane at least 300px wide
        initial_config_width = max(400, int(self.width() * 0.5))
        initial_guide_width = max(200, self.width() - initial_config_width)
        splitter.setSizes([initial_config_width, initial_guide_width])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        self.raise_()
        self.activateWindow()
        self._adjust_splitter()

    def _adjust_splitter(self) -> None:
        """Keep a stable left/right ratio with minimum widths on resize."""
        if self._splitter is None:
            return
        total_width = self.width()
        desired_config = int(total_width * 0.4)
        config_width = max(450, desired_config)
        guide_width = max(300, total_width - config_width)
        self._splitter.setSizes([config_width, guide_width])

    def resizeEvent(self, event) -> None:
        self._adjust_splitter()
        super().resizeEvent(event)

    def save_config(self) -> None:
        """
        Validate JSON in the editor and, if valid, store it and close
        the dialog with accept(). The actual disk write is handled by
        the caller (module_configs.save_module_config).
        """
        raw_text = self.config_editor.toPlainText()
        try:
            cfg = json.loads(raw_text)
        except json.JSONDecodeError as e:
            showInfo(f"Error: Invalid JSON format.\n\n{e}")
            return

        if not isinstance(cfg, dict):
            showInfo("Error: Top-level JSON must be an object (dictionary).")
            return

        self._parsed_config = cfg
        self.accept()

    def restore_defaults(self) -> None:
        """
        Replace the editor contents with the default_config dict provided
        at construction time.
        """
        self.config_editor.setPlainText(
            json.dumps(self._default_config or {}, indent=4, ensure_ascii=False)
        )

    def result_config(self) -> Optional[dict]:
        """
        Return the parsed config dict if Save was pressed and JSON was
        valid, otherwise None.
        """
        return self._parsed_config


class FindQidsSettingsDialog(QDialog):
    """Form-based settings editor for the Find QIDs module."""

    def __init__(
        self,
        merged_config: dict,
        default_config: dict,
        title: str = "QID search settings",
        on_save: Optional[Callable[[dict], None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent or mw)

        self._default_config = default_config or {}
        self._parsed_config: Optional[dict] = None
        self._on_save = on_save
        self._on_close = on_close
        self._syncing_uw_version = False

        self.setWindowTitle(title)
        window_flag_window = getattr(Qt.WindowType, "Window", 0)
        window_flag_on_top = getattr(Qt.WindowType, "WindowStaysOnTopHint", 0)
        self.setWindowFlags(window_flag_window | window_flag_on_top)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.resize(FIND_QIDS_SETTINGS_WINDOW_WIDTH, FIND_QIDS_SETTINGS_WINDOW_HEIGHT)
        self.setMinimumSize(FIND_QIDS_SETTINGS_MIN_WIDTH, FIND_QIDS_SETTINGS_MIN_HEIGHT)

        self._build_ui()
        self._load_values(merged_config)
        self._position_near_top_center()
        self.raise_()
        self.activateWindow()

    @staticmethod
    def _normalize_bool(value: object) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on"}:
                return True
            if normalized in {"0", "false", "no", "off", ""}:
                return False
        return bool(value)

    @staticmethod
    def _normalize_uw_version(uw_step: bool, uw_comlex: bool) -> tuple[bool, bool]:
        # STEP is the default whenever selection is ambiguous.
        if uw_comlex and not uw_step:
            return False, True
        return True, False

    def _merged_with_defaults(self, source: Optional[dict]) -> dict:
        merged = dict(self._default_config or {})
        if isinstance(source, dict):
            merged.update(source)
        return merged

    def _set_uw_version(self, step_selected: bool) -> None:
        self._syncing_uw_version = True
        self.uw_step_radio.setChecked(step_selected)
        self.uw_comlex_radio.setChecked(not step_selected)
        self._syncing_uw_version = False

    def _on_uw_step_toggled(self, checked: bool) -> None:
        if self._syncing_uw_version:
            return
        if checked:
            self._set_uw_version(True)
        elif not self.uw_comlex_radio.isChecked():
            self._set_uw_version(True)

    def _on_uw_comlex_toggled(self, checked: bool) -> None:
        if self._syncing_uw_version:
            return
        if checked:
            self._set_uw_version(False)
        elif not self.uw_step_radio.isChecked():
            self._set_uw_version(True)

    def _wire_live_updates(self) -> None:
        self.uw_step_radio.toggled.connect(self._on_uw_step_toggled)
        self.uw_comlex_radio.toggled.connect(self._on_uw_comlex_toggled)

    def _visible_defaults(self) -> dict[str, object]:
        merged_defaults = self._merged_with_defaults(None)
        uw_step, uw_comlex = self._normalize_uw_version(
            self._normalize_bool(merged_defaults.get("UW_STEP", False)),
            self._normalize_bool(merged_defaults.get("UW_COMLEX", False)),
        )
        return {
            "QID_parent_tag": str(merged_defaults.get("QID_parent_tag", "")).strip(),
            "MISSED_tag": str(merged_defaults.get("MISSED_tag", DEFAULT_MISSED_TAG)).strip(),
            "UW_STEP": uw_step,
            "UW_COMLEX": uw_comlex,
        }

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(FIND_QIDS_ROOT_SPACING)
        root.setContentsMargins(
            FIND_QIDS_ROOT_MARGIN,
            FIND_QIDS_ROOT_MARGIN,
            FIND_QIDS_ROOT_MARGIN,
            FIND_QIDS_ROOT_MARGIN,
        )
        form_grid = QGridLayout()
        form_grid.setHorizontalSpacing(FIND_QIDS_GROUP_HORIZONTAL_SPACING)
        form_grid.setVerticalSpacing(FIND_QIDS_GROUP_VERTICAL_SPACING)
        form_grid.setColumnStretch(0, 0)
        form_grid.setColumnStretch(1, 1)

        row = 0
        uw_version_label = QLabel(FIND_QIDS_LABEL_UWORLD_VERSION, self)
        uw_version_label.setMinimumWidth(FIND_QIDS_FIELD_LABEL_WIDTH)
        uw_version_widget = QWidget(self)
        uw_version_layout = QHBoxLayout(uw_version_widget)
        uw_version_layout.setContentsMargins(0, 0, 0, 0)
        uw_version_layout.setSpacing(FIND_QIDS_GROUP_HORIZONTAL_SPACING)
        self.uw_step_radio = QRadioButton("STEP", self)
        self.uw_comlex_radio = QRadioButton("COMLEX", self)
        self.uw_version_group = QButtonGroup(self)
        self.uw_version_group.setExclusive(True)
        self.uw_version_group.addButton(self.uw_step_radio)
        self.uw_version_group.addButton(self.uw_comlex_radio)
        uw_version_layout.addWidget(self.uw_step_radio)
        uw_version_layout.addWidget(self.uw_comlex_radio)
        uw_version_layout.addStretch(1)
        form_grid.addWidget(uw_version_label, row, 0)
        form_grid.addWidget(uw_version_widget, row, 1)
        row += 1

        missed_tag_label = QLabel(FIND_QIDS_LABEL_MISSED_QUESTIONS_TAG, self)
        missed_tag_label.setMinimumWidth(FIND_QIDS_FIELD_LABEL_WIDTH)
        self.missed_tag_input = QLineEdit(self)
        self.missed_tag_input.setMinimumHeight(FIND_QIDS_FIELD_MIN_HEIGHT)
        form_grid.addWidget(missed_tag_label, row, 0)
        form_grid.addWidget(self.missed_tag_input, row, 1)
        row += 1

        qid_parent_label = QLabel(FIND_QIDS_LABEL_QID_PARENT_TAG, self)
        qid_parent_label.setMinimumWidth(FIND_QIDS_FIELD_LABEL_WIDTH)
        self.qid_parent_tag_input = QLineEdit(self)
        self.qid_parent_tag_input.setMinimumHeight(FIND_QIDS_FIELD_MIN_HEIGHT)
        form_grid.addWidget(qid_parent_label, row, 0)
        form_grid.addWidget(self.qid_parent_tag_input, row, 1)

        form_widget = QWidget(self)
        form_widget.setLayout(form_grid)
        root.addWidget(form_widget, 0)
        root.addStretch(1)

        button_row = QHBoxLayout()
        restore_btn = QPushButton("Restore Defaults", self)
        restore_btn.clicked.connect(self.restore_defaults)
        button_row.addWidget(restore_btn)

        button_row.addStretch(1)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        if self.save_button is not None:
            self.save_button.setText("Save")
            self.save_button.clicked.connect(self.save_config)
        else:
            self.save_button = QPushButton("Save", self)
            self.save_button.clicked.connect(self.save_config)
            button_row.addWidget(self.save_button)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_button is not None:
            cancel_button.setText("Cancel")
            cancel_button.clicked.connect(self.reject)
        else:
            fallback_cancel = QPushButton("Cancel", self)
            fallback_cancel.clicked.connect(self.reject)
            button_row.addWidget(fallback_cancel)
        button_row.addWidget(button_box)
        root.addLayout(button_row)
        self._wire_live_updates()

    def _position_near_top_center(self) -> None:
        try:
            geo = mw.app.primaryScreen().availableGeometry()
            x = geo.center().x() - self.width() // 2
            y = geo.top() + max(
                FIND_QIDS_SETTINGS_TOP_OFFSET_MIN,
                int(geo.height() * FIND_QIDS_SETTINGS_TOP_OFFSET_RATIO),
            )
            self.move(x, y)
        except Exception:
            pass

    def _load_values(self, source: Optional[dict]) -> None:
        cfg = self._merged_with_defaults(source)
        self.qid_parent_tag_input.setText(str(cfg.get("QID_parent_tag", "")).strip())
        uw_step, _ = self._normalize_uw_version(
            self._normalize_bool(cfg.get("UW_STEP", False)),
            self._normalize_bool(cfg.get("UW_COMLEX", False)),
        )
        self._set_uw_version(uw_step)
        self.missed_tag_input.setText(str(cfg.get("MISSED_tag", "")).strip())
        self.qid_parent_tag_input.setFocus()

    def save_config(self) -> None:
        self._parsed_config = {
            "QID_parent_tag": self.qid_parent_tag_input.text().strip(),
            "UW_STEP": self.uw_step_radio.isChecked(),
            "UW_COMLEX": self.uw_comlex_radio.isChecked(),
            "MISSED_tag": self.missed_tag_input.text().strip(),
        }
        if callable(self._on_save):
            self._on_save(self._parsed_config)
        self.accept()

    def restore_defaults(self) -> None:
        visible_defaults = self._visible_defaults()
        self.qid_parent_tag_input.setText(str(visible_defaults["QID_parent_tag"]))
        self.missed_tag_input.setText(str(visible_defaults["MISSED_tag"]))
        self._set_uw_version(bool(visible_defaults["UW_STEP"]))

    def accept(self) -> None:
        super().accept()
        if callable(self._on_close):
            self._on_close()

    def reject(self) -> None:
        super().reject()
        if callable(self._on_close):
            self._on_close()

    def result_config(self) -> Optional[dict]:
        return self._parsed_config
