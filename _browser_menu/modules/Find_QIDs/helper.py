# helper.py — _Find_QIDs
# 18-27_11-05
from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any, Dict, List, Optional, Sequence, Union

from aqt import mw, gui_hooks  # noqa: F401  # (imported for type / runtime context)
from aqt.browser import Browser
from aqt.qt import QApplication
from aqt.utils import tooltip, showWarning


# ======================================================================
# $ Essentials at the top (your preference)
# ======================================================================
CONFIG_SECTION_FIND_QIDS = "find_QIDs"

CONFIG_KEY_UW_STEP = "UW_STEP"
CONFIG_KEY_UW_COMLEX = "UW_COMLEX"
CONFIG_KEY_QID_PARENT_TAG = "QID_parent_tag"
CONFIG_KEY_TAG_PREFIX = "TAG_PREFIX"
CONFIG_KEY_MISSED_TAG = "MISSED_tag"
CONFIG_KEY_DEFAULT_MISSED_ONLY = "default_missed_only"

LEGACY_CONFIG_KEY_MISSED_FILTER = "MISSED_FILTER"
LEGACY_CONFIG_KEY_MISSED_FILTER_TAG = "MISSED_FILTER_TAG"

DEFAULT_UW_STEP = False
DEFAULT_UW_COMLEX = False
DEFAULT_QID_PARENT_TAG = ""
DEFAULT_TAG_PREFIX = "#UWorld::\\w+::"
DEFAULT_MISSED_TAG = "##Missed-Qs"
DEFAULT_MISSED_ONLY = False

STEP_PARENT_TAG = "#UWORLD::STEP"
COMLEX_PARENT_TAG = "#UWORLD::COMLEX"

# Collection API fallback order for note lookups (legacy/new).
COLLECTION_FIND_NOTES_METHODS = ("find_notes", "findNotes")

# When lookup API is unavailable/unknown, avoid misleading "No cards found" warnings.
SUPPRESS_MISSING_TOOLTIP_ON_UNKNOWN_LOOKUP = True

# ! Do not edit: conservative, add-on local defaults (overridden by config)
_DEFAULTS: Dict[str, Any] = {
    CONFIG_KEY_UW_STEP: DEFAULT_UW_STEP,
    CONFIG_KEY_UW_COMLEX: DEFAULT_UW_COMLEX,
    CONFIG_KEY_QID_PARENT_TAG: DEFAULT_QID_PARENT_TAG,
    CONFIG_KEY_TAG_PREFIX: DEFAULT_TAG_PREFIX,
    CONFIG_KEY_MISSED_TAG: DEFAULT_MISSED_TAG,
    CONFIG_KEY_DEFAULT_MISSED_ONLY: DEFAULT_MISSED_ONLY,
}


# ======================================================================
# Config helpers
# ======================================================================
def _addon_root_key() -> str:
    """
    Resolve the root package name Anki uses for this add-on’s config bucket.
    Works in both nested and standalone import layouts.
    """
    pkg = __package__ or ""
    if pkg:
        return pkg.split(".", 1)[0]
    return "_friend_pack"


def _normalize_missed_tag(value: Any) -> str:
    """
    Normalize MISSED_tag as a raw parent tag.

    Legacy values that include search prefixes (tag:/tag:re:) are reduced
    to the raw tag text so config remains source-of-truth in raw form.
    """
    text = str(value or "").strip()
    if not text:
        return DEFAULT_MISSED_TAG
    if text.startswith("tag:re:"):
        text = text[len("tag:re:"):]
    elif text.startswith("tag:"):
        text = text[len("tag:"):]
    text = text.strip()
    return text or DEFAULT_MISSED_TAG


def _strip_tag_query_prefix(value: str) -> str:
    if value.startswith("tag:re:"):
        return value[len("tag:re:"):]
    if value.startswith("tag:"):
        return value[len("tag:"):]
    return value


def normalize_parent_tag_expr(value: Any, fallback: str = "") -> str:
    """
    Normalize a parent-tag expression used for QID lookup.

    Returns canonical parent form without trailing ":" delimiters.
    """
    text = str(value or "").strip()
    if not text:
        text = str(fallback or "").strip()
    text = _strip_tag_query_prefix(text).strip()
    text = text.rstrip(":").strip()
    return text


def _ensure_regex_end_anchor(pattern: str) -> str:
    """Guarantee a single trailing regex end-anchor for QID tag queries."""
    text = pattern.rstrip()
    if text.endswith("$"):
        return text
    return f"{text}$"


def _normalize_bool(value: Any, fallback: bool = False) -> bool:
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
    return bool(value) if value is not None else fallback


def get_config() -> Dict[str, Any]:
    """
    Load config from Anki, merge with defaults, normalize fields.

    Returns
    -------
    dict with at least:
      - UW_STEP/UW_COMLEX (bool)
      - QID_parent_tag (str, raw parent expression)
      - TAG_PREFIX (str, raw parent expression)
      - MISSED_tag (raw tag text)
    """
    try:
        root = _addon_root_key()
        user = mw.addonManager.getConfig(root) or {}
    except Exception:
        user = {}
    if not isinstance(user, dict):
        user = {}

    section_cfg = user.get(CONFIG_SECTION_FIND_QIDS, {})
    if isinstance(section_cfg, dict):
        # Nested section wins over legacy top-level keys when both are present.
        source = {**user, **section_cfg}
    else:
        source = dict(user)

    raw_missed_tag = source.get(CONFIG_KEY_MISSED_TAG)
    if raw_missed_tag is None:
        raw_missed_tag = source.get(LEGACY_CONFIG_KEY_MISSED_FILTER)
    if raw_missed_tag is None:
        raw_missed_tag = source.get(LEGACY_CONFIG_KEY_MISSED_FILTER_TAG)

    cfg = dict(_DEFAULTS)
    cfg[CONFIG_KEY_UW_STEP] = _normalize_bool(
        source.get(CONFIG_KEY_UW_STEP, _DEFAULTS[CONFIG_KEY_UW_STEP]),
        fallback=DEFAULT_UW_STEP,
    )
    cfg[CONFIG_KEY_UW_COMLEX] = _normalize_bool(
        source.get(CONFIG_KEY_UW_COMLEX, _DEFAULTS[CONFIG_KEY_UW_COMLEX]),
        fallback=DEFAULT_UW_COMLEX,
    )
    cfg[CONFIG_KEY_QID_PARENT_TAG] = normalize_parent_tag_expr(
        source.get(CONFIG_KEY_QID_PARENT_TAG, _DEFAULTS[CONFIG_KEY_QID_PARENT_TAG]),
        fallback=DEFAULT_QID_PARENT_TAG,
    )
    cfg[CONFIG_KEY_TAG_PREFIX] = normalize_parent_tag_expr(
        source.get(CONFIG_KEY_TAG_PREFIX, _DEFAULTS[CONFIG_KEY_TAG_PREFIX]),
        fallback=DEFAULT_TAG_PREFIX,
    )
    cfg[CONFIG_KEY_MISSED_TAG] = _normalize_missed_tag(raw_missed_tag)
    cfg[CONFIG_KEY_DEFAULT_MISSED_ONLY] = _normalize_bool(
        source.get(
            CONFIG_KEY_DEFAULT_MISSED_ONLY,
            _DEFAULTS[CONFIG_KEY_DEFAULT_MISSED_ONLY],
        ),
        fallback=DEFAULT_MISSED_ONLY,
    )

    return cfg


def norm_tag_prefix(prefix: Optional[str]) -> str:
    """Return normalized parent expression with a single trailing '::'."""
    parent = normalize_parent_tag_expr(prefix or "")
    return f"{parent}::" if parent else ""


# ======================================================================
# Parsing & validation
# ======================================================================
def parse_qids_anydelim(raw: str) -> List[str]:
    """
    Split on any non-digit; keep only digit tokens; dedupe preserving order.
    Accepts commas, spaces, tabs, new lines, mixed junk.

    Examples
    --------
    "123, 456  789\n0001"  -> ["123", "456", "789", "0001"]
    """
    if not raw:
        return []
    tokens = re.split(r"\D+", raw)
    out, seen = [], set()
    for t in tokens:
        if not t:
            continue
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def parse_qids_from_csv(raw: str) -> List[int]:
    """
    Strict comma-separated form used by the legacy Tools-menu dialog.
    Returns a list of ints. Invalid tokens cause a ValueError.
    """
    if not raw:
        return []
    items = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece.isdigit():
            raise ValueError(f"Invalid QID: {piece!r}")
        items.append(int(piece))
    return items


def check_integrity(ids_str: str) -> bool:
    """
    Back-compat validator for the legacy Tools-menu path.
    Accepts only digits separated by commas (spaces tolerated around commas).
    """
    try:
        _ = parse_qids_from_csv(ids_str)
        return True
    except Exception:
        return False


# ======================================================================
# Tag & query building
# ======================================================================
def _parent_to_qid_query(parent_tag_expr: str, qid_text: str, regex: bool) -> str:
    parent = normalize_parent_tag_expr(parent_tag_expr)
    if regex:
        regex_body = _ensure_regex_end_anchor(f"{parent}::{qid_text}")
        return f"tag:re:{regex_body}"
    return f"tag:{parent}::{qid_text}"


def qid_to_tag(qid: Union[str, int], prefix: Optional[str] = None, regex: bool = True) -> str:
    """
    Build a single tag query for Anki Browser.

    Parameters
    ----------
    qid    : str|int    -> the numeric id
    prefix : Optional   -> override TAG_PREFIX fallback only
    regex  : bool       -> if True, returns 'tag:re:<parent>::<qid>$'
                           else       returns 'tag:<parent>::<qid>'
    """
    cfg = get_config()
    qid_text = str(qid).strip()

    # Highest-priority explicit parent override.
    qid_parent_tag = cfg.get(CONFIG_KEY_QID_PARENT_TAG, "")
    if qid_parent_tag:
        return _parent_to_qid_query(str(qid_parent_tag), qid_text, regex=regex)

    # Explicit modes requested in config.
    if cfg[CONFIG_KEY_UW_STEP]:
        return _parent_to_qid_query(STEP_PARENT_TAG, qid_text, regex=regex)
    if cfg[CONFIG_KEY_UW_COMLEX]:
        return _parent_to_qid_query(COMLEX_PARENT_TAG, qid_text, regex=regex)

    # Final fallback path: TAG_PREFIX parent expression.
    fallback_parent = normalize_parent_tag_expr(prefix or cfg[CONFIG_KEY_TAG_PREFIX], fallback=DEFAULT_TAG_PREFIX)
    return _parent_to_qid_query(fallback_parent, qid_text, regex=regex)


def tags_for_qids(qids: Sequence[Union[str, int]], prefix: Optional[str] = None, regex: bool = True) -> List[str]:
    """Vector form of qid_to_tag()."""
    return [qid_to_tag(q, prefix=prefix, regex=regex) for q in qids]


def build_or_query(qids: Sequence[Union[str, int]], prefix: Optional[str] = None) -> str:
    """
    Build an 'OR'-joined query over regex tag terms, matching the current behavior.
    Example: 'tag:re:<parent>::123$ OR tag:re:<parent>::456$'
    """
    parts = tags_for_qids(qids, prefix=prefix, regex=True)
    return " OR ".join(parts)


def build_missed_filter(tag_expr: Optional[str] = None) -> str:
    """
    Return canonical missed-only filter, always built from raw parent tag.
    """
    missed_tag = _normalize_missed_tag(tag_expr if tag_expr is not None else get_config()[CONFIG_KEY_MISSED_TAG])
    return f"tag:re:{missed_tag}"


def add_missed_filter(query: str, missed_on: bool) -> str:
    """Append the missed filter exactly like the current code path does."""
    if not missed_on:
        return query
    return f"({query}) {build_missed_filter()}"


def build_query(qids: Sequence[Union[str, int]], missed_only: bool) -> str:
    """
    High-level wrapper:
      qids → OR query over regex tag terms → optional missed-only tail
    """
    base = build_or_query(qids)
    return add_missed_filter(base, missed_only)


# ======================================================================
# Browser helpers
# ======================================================================
def get_existing_browser() -> Optional[Browser]:
    """Return an open Browser window if one exists, else None."""
    try:
        for w in QApplication.topLevelWidgets():
            if isinstance(w, Browser):
                return w
    except Exception:
        pass
    return None


def ensure_browser() -> Browser:
    """
    Return a Browser, opening one if none exists.
    """
    br = get_existing_browser()
    if br:
        return br
    # Open the standard Anki Browse window then fetch it
    mw.onBrowse()
    br = get_existing_browser()
    if not br:
        # Extremely rare; provide a clear error
        raise RuntimeError("Could not open Anki Browser window.")
    return br


def run_browser_query(browser: Browser, query: str) -> None:
    """
    Run a query in the given Browser, supporting both new and old Anki APIs.
    """
    if not query:
        showWarning("No query to search.")
        return
    try:
        # Preferred on newer Anki
        if hasattr(browser, "search_for") and callable(browser.search_for):
            browser.activateWindow()
            browser.raise_()
            browser.search_for(query)
            return
        # Fallback path for older versions
        se = browser.form.searchEdit.lineEdit()
        browser.activateWindow()
        browser.raise_()
        se.setText(query)
        try:
            browser.onSearchActivated()
        except TypeError:
            browser.onSearchActivated(False)
    except Exception as e:
        showWarning(f"Failed to run search:\n{e}")


# ======================================================================
# Lookup + notifications
# ======================================================================
def _find_note_ids(query: str) -> Optional[list[int]]:
    """
    Find note ids using whichever collection API is available.

    Returns:
      - list[int] when lookup succeeded
      - None when no supported lookup API is callable (unknown state)
    """
    col = getattr(mw, "col", None)
    if col is None:
        return None

    for method_name in COLLECTION_FIND_NOTES_METHODS:
        finder = getattr(col, method_name, None)
        if not callable(finder):
            continue
        try:
            result = finder(query)
        except Exception:
            continue

        if result is None:
            return []
        if isinstance(result, (str, bytes)):
            return []
        if not isinstance(result, Iterable):
            return []

        try:
            return [int(nid) for nid in result]
        except Exception:
            return []

    return None


def find_any_for_qid(qid: Union[str, int]) -> Optional[bool]:
    """
    Return whether a QID has at least one matching note/card.

    Returns:
      - True/False when lookup APIs are available
      - None when lookup API support is unknown/unavailable

    Uses the same search syntax the Browser uses for consistency.
    """
    try:
        query = qid_to_tag(qid, regex=True)  # 'tag:re:<parent>::<qid>$'
        note_ids = _find_note_ids(query)
        if note_ids is None:
            return None
        return len(note_ids) > 0
    except Exception:
        return None


def notify_if_missing(qids: Sequence[Union[str, int]]) -> None:
    """
    Silent unless at least one QID has no associated notes/cards.
    Uses a non-blocking tooltip so it never interrupts your flow.
    """
    missing: list[str] = []
    has_unknown_lookup = False
    for qid in qids:
        has_any = find_any_for_qid(qid)
        if has_any is False:
            missing.append(str(qid))
        elif has_any is None:
            has_unknown_lookup = True

    if has_unknown_lookup and SUPPRESS_MISSING_TOOLTIP_ON_UNKNOWN_LOOKUP:
        return

    if missing:
        tooltip(f"No cards found for QIDs: {', '.join(missing)}", period=5000, parent=mw)


# ======================================================================
# Top-level action used by both menu paths
# ======================================================================
def execute_search(qids: Sequence[Union[str, int]], missed_only: bool) -> None:
    """
    Full pipeline:
      - notify if any QIDs missing
      - ensure a Browser exists
      - build the final query (OR chain, optional missed-only)
      - run it
    """
    notify_if_missing(qids)
    query = build_query(qids, missed_only)
    br = ensure_browser()
    run_browser_query(br, query)
