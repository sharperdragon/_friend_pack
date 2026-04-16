from __future__ import annotations

from fnmatch import fnmatch
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
    "Thumbs.db",
    "Install_Friend_Pack.command",
    "_browser_menu_debug.log",
    "build_ankiweb_package.py",
    "meta.json",
    "pyrightconfig.json",
}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}
EXCLUDED_GLOB_PATTERNS = {
    "*.log",
}


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


def build_archive() -> Path:
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

    return archive_path


if __name__ == "__main__":
    output = build_archive()
    print(f"Created: {output}")
