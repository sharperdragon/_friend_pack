from __future__ import annotations

from fnmatch import fnmatch
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


# =========================
# User-tunable constants
# =========================
ADDON_ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ADDON_ROOT / "dist"
OUTPUT_FILENAME = "_friend_pack.ankiaddon"
OVERWRITE_EXISTING_OUTPUT = True

EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".idea",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    ".venv",
    "dist",
    "build",
    "typings",
}
EXCLUDED_FILE_NAMES = {
    ".DS_Store",
    ".gitignore",
    "Thumbs.db",
    "Install_Friend_Pack.command",
    "_browser_menu_debug.log",
    "build_ankiweb_package.py",
    "meta.json",
    "planned_update_config.json",
    "pyrightconfig.json",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_GLOB_PATTERNS = {
    "*.log",
}
BANNED_ARCHIVE_ENTRIES = frozenset(
    {
        "meta.json",
        "planned_update_config.json",
    }
)
# Minimum root-level files expected before packaging.
REQUIRED_ROOT_FILES = (
    "__init__.py",
    "config.json",
)
REQUIRED_CONFIG_FILENAME = "config.json"
REQUIRED_CONFIG_OBJECT_SECTIONS = (
    "add_custom_tags",
    "add_missed_tags",
    "browser_menu",
    "find_QIDs",
)


def _is_excluded(rel_path: Path) -> bool:
    parts = rel_path.parts
    if any(part in EXCLUDED_DIR_NAMES for part in parts):
        return True

    name = rel_path.name
    if name in EXCLUDED_FILE_NAMES:
        return True

    if rel_path.suffix in EXCLUDED_SUFFIXES:
        return True

    return any(fnmatch(name, pattern) for pattern in EXCLUDED_GLOB_PATTERNS)


def _iter_release_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if _is_excluded(rel):
            continue
        files.append(path)
    return sorted(files)


def _assert_archive_has_no_banned_entries(archive_path: Path) -> None:
    with ZipFile(archive_path, "r") as archive:
        names = set(archive.namelist())
    banned_found = sorted(names.intersection(BANNED_ARCHIVE_ENTRIES))
    if banned_found:
        raise RuntimeError(
            "Release archive contains banned entries: "
            + ", ".join(banned_found)
        )


def _assert_required_root_files(root: Path) -> None:
    """Ensure required root-level files exist before packaging."""
    missing = sorted(
        name
        for name in REQUIRED_ROOT_FILES
        if not (root / name).exists() or not (root / name).is_file()
    )
    if missing:
        raise RuntimeError("Missing required root file(s): " + ", ".join(missing))


def _assert_config_json_is_valid(root: Path) -> None:
    config_path = root / REQUIRED_CONFIG_FILENAME
    if not config_path.exists() or not config_path.is_file():
        raise RuntimeError(f"Missing required config file: {REQUIRED_CONFIG_FILENAME}")
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Invalid {REQUIRED_CONFIG_FILENAME}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"Invalid {REQUIRED_CONFIG_FILENAME}: top-level JSON must be an object.")
    for section in REQUIRED_CONFIG_OBJECT_SECTIONS:
        section_value = data.get(section)
        if not isinstance(section_value, dict):
            raise RuntimeError(
                f"Invalid {REQUIRED_CONFIG_FILENAME}: `{section}` must be a JSON object."
            )


def build_archive() -> Path:
    _assert_required_root_files(ADDON_ROOT)
    _assert_config_json_is_valid(ADDON_ROOT)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = OUTPUT_DIR / OUTPUT_FILENAME

    if archive_path.exists():
        if OVERWRITE_EXISTING_OUTPUT:
            archive_path.unlink()
        else:
            raise FileExistsError(f"Output already exists: {archive_path}")

    files = _iter_release_files(ADDON_ROOT)
    if not files:
        raise RuntimeError("No files matched release rules.")

    with ZipFile(archive_path, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            rel = path.relative_to(ADDON_ROOT)
            archive.write(path, arcname=rel.as_posix())

    _assert_archive_has_no_banned_entries(archive_path)
    return archive_path


if __name__ == "__main__":
    output = build_archive()
    print(f"Created: {output}")
