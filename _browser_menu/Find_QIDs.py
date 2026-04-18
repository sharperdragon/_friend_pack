# Find_QIDs.py — _Find_QIDs (refactored to use helper.py)
# 18-40_11-05

# ========== DEBUG IMPORT ==========
try:
    # Reuse the add-on's debug logger from loader.py
    from .loader import _dbg  # type: ignore[attr-defined]
except Exception:
    # Fallback: no-op debug function if loader._dbg is not available
    def _dbg(msg: str) -> None:
        return

_dbg("Find_QIDs: module imported")

from typing import List, Optional
from aqt import mw
from aqt.browser import Browser
from aqt.qt import (
    QAction, QDialog, QVBoxLayout, QLabel, QPlainTextEdit,
    QDialogButtonBox, QPushButton, QWidget, Qt, QHBoxLayout,
    QApplication, QComboBox, QShortcut, QKeySequence, QLineEdit,
    QCheckBox
)

# =========================
# Compatibility constants
# =========================
QT_ARROW_KEY_LEFT_NAME = "Key_Left"
QT_ARROW_KEY_RIGHT_NAME = "Key_Right"


def _resolve_dialog_button(button_name: str):
    """Resolve QDialogButtonBox button enum across Qt6/Qt5 layouts."""
    standard_button = getattr(QDialogButtonBox, "StandardButton", None)
    if standard_button is not None:
        value = getattr(standard_button, button_name, None)
        if value is not None:
            return value
    return getattr(QDialogButtonBox, button_name)


def _resolve_qt_key(key_name: str):
    """Resolve key enum across Qt6 nested enum and Qt5 flat enum."""
    qt6_keys = getattr(Qt, "Key", None)
    if qt6_keys is not None:
        value = getattr(qt6_keys, key_name, None)
        if value is not None:
            return value
    return getattr(Qt, key_name, None)


def _resolve_window_non_modal():
    """Resolve non-modal window enum value across Qt6/Qt5."""
    modality_enum = getattr(Qt, "WindowModality", None)
    if modality_enum is not None:
        value = getattr(modality_enum, "NonModal", None)
        if value is not None:
            return value
    return getattr(Qt, "NonModal", None)


BUTTON_OK = _resolve_dialog_button("Ok")
BUTTON_CANCEL = _resolve_dialog_button("Cancel")
KEY_LEFT = _resolve_qt_key(QT_ARROW_KEY_LEFT_NAME)
KEY_RIGHT = _resolve_qt_key(QT_ARROW_KEY_RIGHT_NAME)
WINDOW_MODALITY_NON_MODAL = _resolve_window_non_modal()

from aqt.utils import tooltip, showWarning, qconnect
from .module_configs import load_module_config

# === Import thin, shared logic from helper.py ==========================
# ! Keep Find_QIDs.py as UI wiring only; all logic lives in helper.py
from .helper import (
    CONFIG_KEY_DEFAULT_MISSED_ONLY,
    CONFIG_KEY_MISSED_TAG,
    get_config,                    # config access (for future UI needs)
    check_integrity,               # legacy CSV validator for Tools dialog
    parse_qids_from_csv,           # strict comma-separated parsing
    parse_qids_anydelim,           # free-form parsing for Browser menu
    qid_to_tag,                    # build tag queries for stepper
    run_browser_query,             # execute a query in Browser
    ensure_browser,                # get or open a Browser
    execute_search,                # end-to-end: notify → build query → run
)

# ----------------------------------------------------------------------
# Tools menu flow (legacy UI preserved)
# ----------------------------------------------------------------------
def show_dialog():
    """
    UI: Prompt for comma-separated QIDs and optional 'missed only' filter,
    then run a combined OR-query via execute_search().
    """
    _dbg("Find_QIDs: show_dialog START")
    dialog = MissedQIDDialog()
    if not dialog.exec():
        _dbg("Find_QIDs: show_dialog cancelled")
        return

    qid_list = dialog.qid_input.text()
    missed_only = dialog.missed_only_checkbox.isChecked()
    _dbg(
        f"Find_QIDs: show_dialog got input len={len(qid_list)}, "
        f"missed_only={missed_only}"
    )

    if not check_integrity(qid_list):
        _dbg("Find_QIDs: show_dialog check_integrity FAILED")
        showWarning("Invalid input")
        return

    try:
        ids = parse_qids_from_csv(qid_list)  # List[int]
        _dbg(f"Find_QIDs: show_dialog parsed {len(ids)} ids")
    except Exception as e:
        _dbg(f"Find_QIDs: show_dialog parse_qids_from_csv ERROR: {e}")
        showWarning(f"Invalid input:\n{e}")
        return

    _dbg("Find_QIDs: show_dialog calling execute_search()")
    execute_search(ids, missed_only)

class MissedQIDDialog(QDialog):
    """Simple dialog for comma-separated QIDs and a missed-only toggle."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paste UWorld Question IDs")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        self.qid_input = QLineEdit(self)
        layout.addWidget(QLabel("Paste UWorld question IDs (comma-separated):"))
        layout.addWidget(self.qid_input)

        missed_label = "##Missed-Qs filter"
        # * Config-driven default for the missed-only toggle
        try:
            cfg = get_config()
            missed_tag = str(cfg.get(CONFIG_KEY_MISSED_TAG, "##Missed-Qs")).strip() or "##Missed-Qs"
            missed_label = f"{missed_tag} filter"
            default_missed_only = bool(cfg.get(CONFIG_KEY_DEFAULT_MISSED_ONLY, False))
            _dbg(
                f"Find_QIDs: MissedQIDDialog default_missed_only={default_missed_only} "
                f"(cfg_keys={list(cfg.keys())})"
            )
        except Exception as e:
            _dbg(f"Find_QIDs: MissedQIDDialog root config load ERROR: {e}")
            try:
                cfg = load_module_config("Find_QIDs")
                default_missed_only = bool(cfg.get("default_missed_only", False))
            except Exception as fallback_err:
                _dbg(f"Find_QIDs: MissedQIDDialog module config fallback ERROR: {fallback_err}")
                # ! Fail-safe: never block dialog if config is missing/bad
                default_missed_only = False
        self.missed_only_checkbox = QCheckBox(missed_label, self)
        self.missed_only_checkbox.setChecked(default_missed_only)
        layout.addWidget(self.missed_only_checkbox)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK", self)
        self.cancel_button = QPushButton("Cancel", self)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # --- Geometry (horizontally centered, near top of screen) ---
        geo = QApplication.primaryScreen().availableGeometry()
        x = geo.center().x() - self.width() // 2   
        y = geo.top() + 40                          
        self.move(x, y)

        layout.addLayout(button_layout)

# Register the legacy Tools menu entry
TOOLS_MENU_ACTION_GUARD_ATTR = "_friend_pack_find_qids_tools_action_registered"
if (
    mw is not None
    and hasattr(mw, "form")
    and hasattr(mw.form, "menuTools")
    and not getattr(mw, TOOLS_MENU_ACTION_GUARD_ATTR, False)
):
    action = QAction("Find notes UW qids 🌀", mw)
    qconnect(action.triggered, show_dialog)
    mw.form.menuTools.addAction(action)
    setattr(mw, TOOLS_MENU_ACTION_GUARD_ATTR, True)

# =====================  FIND QIDs BROWSER MENU (TRIMMED DROP-IN)  =====================
# Adds Browser menu actions under top-level Custom:
#   [Search all (OR)] / [Search 1-by-1]
# Now fully delegates to helper.py to keep __init__ thin.

# -----------------------------------------------------------------------------
# // Dialogs used by the Browser menu
# -----------------------------------------------------------------------------
class _FQIDS_QIDInput(QDialog):
    """Paste QIDs (any delimiter)."""
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("Find QIDs")
        self.setModal(True)

        self.edit = QPlainTextEdit(self)
        self.edit.setPlaceholderText("Paste QIDs (any delimiter: spaces, commas, new lines)...")

        btns = QDialogButtonBox(BUTTON_OK | BUTTON_CANCEL, self)

        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addWidget(QLabel("Paste QIDs:"))
        lay.addWidget(self.edit)
        lay.addWidget(btns)

        # --- Geometry (horizontally centered, near top of screen) ---
        self.setFixedSize(500, 260)   # Adjust as desired
        geo = QApplication.primaryScreen().availableGeometry()
        x = geo.center().x() - self.width() // 2   # horizontal center
        y = geo.top() + 20                          # ~80 px from top; adjust as needed
        self.move(x, y)

    def text(self) -> str:
        return self.edit.toPlainText().strip()


def _extract_qid_from_query_tail(tag_query: str) -> str:
    """
    Extract trailing QID from query forms like:
    - tag:re:<parent>::123$
    - tag:<parent>::123
    """
    parts = str(tag_query).strip().rsplit("::", 1)
    if len(parts) != 2:
        return "?"
    candidate = parts[1].rstrip("$")
    return candidate if candidate.isdigit() else "?"


class _FQIDS_Stepper(QDialog):
    """Step through QIDs one-by-one; with jump, previous, and next."""
    def __init__(self, browser, tags: List[str], parent: Optional[QWidget] = None):
        super().__init__(parent)
        if WINDOW_MODALITY_NON_MODAL is not None:
            self.setWindowModality(WINDOW_MODALITY_NON_MODAL)
        self.browser = browser
        self.tags = tags
        self.i = -1
        self.setWindowTitle("Find QIDs: 1-by-1")

        # Extract plain QIDs from tag-query tails.
        self.qids = [_extract_qid_from_query_tail(t) for t in self.tags]
        # Fast lookup QID -> first index
        self.qid_to_idx = {q: idx for idx, q in enumerate(self.qids) if q != "?"}

        # --- UI widgets ---
        self.lbl = QLabel(self)  # status line
        self.combo = QComboBox(self)
        self.combo.addItems(self.qids)
        self.btn_prev = QPushButton("Previous", self)
        self.btn_next = QPushButton("Next", self)

        # --- Signals ---
        self.btn_prev.clicked.connect(self._prev)
        self.btn_next.clicked.connect(self._next)
        # Prefer robust signal connections across Qt versions
        connected = False
        try:
            self.combo.textActivated.connect(self._jump_to_qid)  # type: ignore[attr-defined]
            connected = True
        except Exception:
            pass
        if not connected:
            try:
                self.combo.currentTextChanged.connect(self._jump_to_qid)
                connected = True
            except Exception:
                pass
        if not connected:
            try:
                self.combo.activated.connect(lambda idx: self._seek_to(int(idx)))
            except Exception:
                pass

        # Keyboard shortcuts: ← = Prev, → = Next
        if KEY_LEFT is not None:
            QShortcut(QKeySequence(KEY_LEFT), self, activated=self._prev)
        if KEY_RIGHT is not None:
            QShortcut(QKeySequence(KEY_RIGHT), self, activated=self._next)

        # --- Layout ---
        lay = QVBoxLayout(self)
        lay.addWidget(self.lbl)
        jump_row = QHBoxLayout()
        jump_row.addWidget(self.combo)
        lay.addLayout(jump_row)
        ctrl_row = QHBoxLayout()
        ctrl_row.addWidget(self.btn_prev)
        ctrl_row.addWidget(self.btn_next)
        lay.addLayout(ctrl_row)

        # --- Geometry (resizable + initial position) ---
        self.resize(220, 120)
        self.setSizeGripEnabled(True)

        # Place inside the Browser, near its top-left content corner
        from aqt.qt import QPoint
        origin = self.browser.mapToGlobal(self.browser.rect().topLeft())  # client area TL
        MARGIN_X = 18   # tweak to taste
        MARGIN_Y = 14   # tweak to taste
        self.move(int(origin.x() + MARGIN_X), int(origin.y() + MARGIN_Y))

        # Initialize at the first item
        self._seek_to(0)

    # Core navigation helpers
    def _seek_to(self, index: int):
        if index < 0 or index >= len(self.tags):
            # Finished range
            if index >= len(self.tags):
                tooltip("Finished 1-by-1 search.", parent=self.browser)
                self.accept()
            return
        self.i = index
        self._run_current()

    def _run_current(self):
        tag_query = self.tags[self.i]
        run_browser_query(self.browser, tag_query)  # delegate to helper
        # Update UI state
        total = len(self.tags)
        current_qid = self.qids[self.i] if self.i < len(self.qids) else "?"
        self.lbl.setText(f"QID {self.i+1}/{total} — current: {current_qid}")
        # Sync combo selection
        if self.combo.currentIndex() != self.i:
            self.combo.setCurrentIndex(self.i)
        # Enable/disable bounds
        self.btn_prev.setEnabled(self.i > 0)
        self.btn_next.setEnabled(self.i < total - 1)

    def _prev(self):
        self._seek_to(self.i - 1)

    def _next(self):
        self._seek_to(self.i + 1)

    def _jump_to_qid(self, qid: str):
        qid = qid.strip()
        idx = self.qid_to_idx.get(qid)
        if idx is None:
            tooltip(f"QID not found: {qid}", parent=self.browser)
            return
        self._seek_to(idx)

# -----------------------------------------------------------------------------
# // Actions for Browser menu
# -----------------------------------------------------------------------------
def _fqids_prompt_qids(parent: QWidget) -> List[str]:
    dlg = _FQIDS_QIDInput(parent)
    if dlg.exec():
        text = dlg.text()
        _dbg(f"Find_QIDs: _fqids_prompt_qids input len={len(text)}")
        try:
            qids = parse_qids_anydelim(text)
            _dbg(f"Find_QIDs: _fqids_prompt_qids parsed {len(qids)} qids")
            return qids
        except Exception as e:
            _dbg(f"Find_QIDs: _fqids_prompt_qids parse_qids_anydelim ERROR: {e}")
            showWarning(f"Invalid QID input:\n{e}")
            return []
    _dbg("Find_QIDs: _fqids_prompt_qids cancelled")
    return []

def _fqids_search_all(browser) -> None:
    """
    Mirror Tools-menu behavior but invoked from Browser:
    - Use MissedQIDDialog (checkbox + strict CSV)
    - Delegate actual execution to execute_search()
    """
    _dbg("Find_QIDs: _fqids_search_all START")
    dlg = MissedQIDDialog()
    if not dlg.exec():
        _dbg("Find_QIDs: _fqids_search_all cancelled")
        return
    qid_list = dlg.qid_input.text()
    missed_only = dlg.missed_only_checkbox.isChecked()
    _dbg(
        f"Find_QIDs: _fqids_search_all got input len={len(qid_list)}, "
        f"missed_only={missed_only}"
    )
    if not check_integrity(qid_list):
        _dbg("Find_QIDs: _fqids_search_all check_integrity FAILED")
        showWarning("Invalid input")
        return
    try:
        ids = parse_qids_from_csv(qid_list)
        _dbg(f"Find_QIDs: _fqids_search_all parsed {len(ids)} ids")
    except Exception as e:
        _dbg(f"Find_QIDs: _fqids_search_all parse_qids_from_csv ERROR: {e}")
        showWarning(f"Invalid input:\n{e}")
        return
    _dbg("Find_QIDs: _fqids_search_all calling execute_search()")
    execute_search(ids, missed_only)

def _fqids_search_step(browser) -> None:
    """
    Free-form paste; step through each QID's tag query individually.
    """
    _dbg("Find_QIDs: _fqids_search_step START")
    qids = _fqids_prompt_qids(browser)
    if not qids:
        _dbg("Find_QIDs: _fqids_search_step no QIDs parsed")
        showWarning("No QIDs found.")
        return
    tags = [qid_to_tag(q, regex=True) for q in qids]
    _dbg(
        f"Find_QIDs: _fqids_search_step built {len(tags)} tag queries "
        f"from {len(qids)} QIDs"
    )
    _FQIDS_Stepper(browser, tags, parent=browser).show()

# -----------------------------------------------------------------------------
# // Public entrypoints for _browser_menu
# -----------------------------------------------------------------------------
def run_search_all_from_browser(browser: Browser) -> None:
    """Entry point for _browser_menu → Custom → Search all."""
    _dbg("Find_QIDs: run_search_all_from_browser called")
    _fqids_search_all(browser)


def run_search_one_by_one_from_browser(browser: Browser) -> None:
    """Entry point for _browser_menu → Custom → Search 1-by-1."""
    _dbg("Find_QIDs: run_search_one_by_one_from_browser called")
    _fqids_search_step(browser)

# ===================  END FIND QIDs BROWSER MENU (TRIMMED DROP-IN)  ===================
