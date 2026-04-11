#!/bin/bash
set -euo pipefail

# User-tunable values
ADDON_FOLDER_NAME="_friend_pack"
ANKI_ADDONS_DIR="$HOME/Library/Application Support/Anki2/addons21"
CREATE_BACKUP_IF_PRESENT="true"
OPEN_ANKI_AFTER_INSTALL="false"
SHOW_SUCCESS_DIALOG="true"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Resolve source folder:
# 1) script placed inside _friend_pack
# 2) script placed beside _friend_pack
if [[ "$(basename "$SCRIPT_DIR")" == "$ADDON_FOLDER_NAME" && -f "$SCRIPT_DIR/__init__.py" ]]; then
    SOURCE_DIR="$SCRIPT_DIR"
elif [[ -d "$SCRIPT_DIR/$ADDON_FOLDER_NAME" && -f "$SCRIPT_DIR/$ADDON_FOLDER_NAME/__init__.py" ]]; then
    SOURCE_DIR="$SCRIPT_DIR/$ADDON_FOLDER_NAME"
else
    echo "Could not find '$ADDON_FOLDER_NAME' next to this installer."
    echo "Keep the installer inside, or next to, the addon folder and try again."
    read -r -p "Press Enter to close..."
    exit 1
fi

TARGET_DIR="$ANKI_ADDONS_DIR/$ADDON_FOLDER_NAME"
TIMESTAMP="$(date +"%Y%m%d-%H%M%S")"
BACKUP_DIR="${TARGET_DIR}.backup.${TIMESTAMP}"

mkdir -p "$ANKI_ADDONS_DIR"

if [[ -d "$TARGET_DIR" ]]; then
    if [[ "$CREATE_BACKUP_IF_PRESENT" == "true" ]]; then
        mv "$TARGET_DIR" "$BACKUP_DIR"
    else
        rm -rf "$TARGET_DIR"
    fi
fi

cp -R "$SOURCE_DIR" "$TARGET_DIR"

echo "Installed to:"
echo "$TARGET_DIR"
if [[ -d "$BACKUP_DIR" ]]; then
    echo
    echo "Backup created:"
    echo "$BACKUP_DIR"
fi

if [[ "$SHOW_SUCCESS_DIALOG" == "true" ]]; then
    /usr/bin/osascript <<OSA
display dialog "Friend Pack installed successfully." & return & return & "Path: $TARGET_DIR" buttons {"OK"} default button "OK"
OSA
fi

if [[ "$OPEN_ANKI_AFTER_INSTALL" == "true" ]]; then
    open -a "Anki" || true
fi

read -r -p "Press Enter to close..."
