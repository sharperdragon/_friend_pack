from typing import Callable, Optional

from aqt import mw
from aqt.qt import (
    QButtonGroup,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    Qt,
    QVBoxLayout,
    QWidget,
)
from aqt.utils import showInfo


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
FIND_QIDS_LABEL_MISSED_QUESTIONS_TAG = "Parent Missed Tag"
FIND_QIDS_UW_MODE_FALLBACK = "fallback"
FIND_QIDS_UW_MODE_STEP = "step"
FIND_QIDS_UW_MODE_COMLEX = "comlex"
FIND_QIDS_SAVE_FAILURE_MESSAGE = (
    "Unable to save settings through Anki addon manager. "
    "Make sure Anki is fully initialized."
)


class FindQidsSettingsDialog(QDialog):
    """Form-based settings editor for the Find QIDs module."""

    def __init__(
        self,
        merged_config: dict,
        default_config: dict,
        title: str = "QID search settings",
        on_save: Optional[Callable[[dict], bool | None]] = None,
        on_close: Optional[Callable[[], None]] = None,
        parent=None,
    ):
        super().__init__(parent or mw)

        self._default_config = default_config or {}
        self._parsed_config: Optional[dict] = None
        self._on_save = on_save
        self._on_close = on_close

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
    def _mode_from_uw_flags(uw_step: bool, uw_comlex: bool) -> str:
        if uw_step and not uw_comlex:
            return FIND_QIDS_UW_MODE_STEP
        if uw_comlex and not uw_step:
            return FIND_QIDS_UW_MODE_COMLEX
        if uw_step and uw_comlex:
            # Legacy/ambiguous state: preserve previous behavior by preferring STEP.
            return FIND_QIDS_UW_MODE_STEP
        return FIND_QIDS_UW_MODE_FALLBACK

    @staticmethod
    def _uw_flags_from_mode(mode: str) -> tuple[bool, bool]:
        if mode == FIND_QIDS_UW_MODE_STEP:
            return True, False
        if mode == FIND_QIDS_UW_MODE_COMLEX:
            return False, True
        return False, False

    def _merged_with_defaults(self, source: Optional[dict]) -> dict:
        merged = dict(self._default_config or {})
        if isinstance(source, dict):
            merged.update(source)
        return merged

    def _set_uw_mode(self, mode: str) -> None:
        self.uw_fallback_radio.setChecked(mode == FIND_QIDS_UW_MODE_FALLBACK)
        self.uw_step_radio.setChecked(mode == FIND_QIDS_UW_MODE_STEP)
        self.uw_comlex_radio.setChecked(mode == FIND_QIDS_UW_MODE_COMLEX)

    def _selected_uw_mode(self) -> str:
        if self.uw_step_radio.isChecked():
            return FIND_QIDS_UW_MODE_STEP
        if self.uw_comlex_radio.isChecked():
            return FIND_QIDS_UW_MODE_COMLEX
        return FIND_QIDS_UW_MODE_FALLBACK

    def _visible_defaults(self) -> dict[str, object]:
        merged_defaults = self._merged_with_defaults(None)
        uw_mode = self._mode_from_uw_flags(
            self._normalize_bool(merged_defaults.get("UW_STEP", False)),
            self._normalize_bool(merged_defaults.get("UW_COMLEX", False)),
        )
        return {
            "QID_parent_tag": str(merged_defaults.get("QID_parent_tag", "")).strip(),
            "MISSED_tag": str(merged_defaults.get("MISSED_tag", DEFAULT_MISSED_TAG)).strip(),
            "UW_MODE": uw_mode,
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
        self.uw_fallback_radio = QRadioButton("Fallback / Custom", self)
        self.uw_step_radio = QRadioButton("STEP", self)
        self.uw_comlex_radio = QRadioButton("COMLEX", self)
        self.uw_version_group = QButtonGroup(self)
        self.uw_version_group.setExclusive(True)
        self.uw_version_group.addButton(self.uw_fallback_radio)
        self.uw_version_group.addButton(self.uw_step_radio)
        self.uw_version_group.addButton(self.uw_comlex_radio)
        uw_version_layout.addWidget(self.uw_fallback_radio)
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
        uw_mode = self._mode_from_uw_flags(
            self._normalize_bool(cfg.get("UW_STEP", False)),
            self._normalize_bool(cfg.get("UW_COMLEX", False)),
        )
        self._set_uw_mode(uw_mode)
        self.missed_tag_input.setText(str(cfg.get("MISSED_tag", "")).strip())
        self.qid_parent_tag_input.setFocus()

    def save_config(self) -> None:
        uw_mode = self._selected_uw_mode()
        uw_step, uw_comlex = self._uw_flags_from_mode(uw_mode)
        self._parsed_config = {
            "QID_parent_tag": self.qid_parent_tag_input.text().strip(),
            "UW_STEP": uw_step,
            "UW_COMLEX": uw_comlex,
            "MISSED_tag": self.missed_tag_input.text().strip(),
        }
        if callable(self._on_save):
            try:
                save_ok = self._on_save(self._parsed_config)
            except Exception:
                showInfo(FIND_QIDS_SAVE_FAILURE_MESSAGE)
                return
            if save_ok is False:
                showInfo(FIND_QIDS_SAVE_FAILURE_MESSAGE)
                return
        self.accept()

    def restore_defaults(self) -> None:
        visible_defaults = self._visible_defaults()
        self.qid_parent_tag_input.setText(str(visible_defaults["QID_parent_tag"]))
        self.missed_tag_input.setText(str(visible_defaults["MISSED_tag"]))
        self._set_uw_mode(str(visible_defaults["UW_MODE"]))

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
