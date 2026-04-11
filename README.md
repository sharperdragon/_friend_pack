# _friend_pack

`_friend_pack` is a local Anki add-on folder that bundles two custom modules in one package:

- `_browser_menu`: adds custom actions inside the Browser menu.
- `_change_notes_shua`: adds context-menu actions for tagging selected notes.

## What To Do With This Folder

Put this folder directly inside Anki's `addons21` directory.

Important:

- Keep the folder name exactly `_friend_pack`.
- Do not nest it as `_friend_pack/_friend_pack`.

## Install Steps

1. Close Anki.
2. If on macOS, double-click `Install_Friend_Pack.command` (inside this folder).
3. Start Anki again.

## Share As A Download (One-Click Install)

For friends on macOS:

1. Share a zip that includes this `_friend_pack` folder as-is.
2. They unzip into Downloads.
3. They open the unzipped `_friend_pack` folder.
4. They double-click `Install_Friend_Pack.command`.
5. The installer copies `_friend_pack` into Anki's `addons21` folder automatically.

Manual fallback (all platforms):

- Copy `_friend_pack` directly into `addons21`.

Typical `addons21` paths:

- macOS: `~/Library/Application Support/Anki2/addons21`
- Windows: `%APPDATA%\Anki2\addons21`
- Linux: `~/.local/share/Anki2/addons21`

After install, the final folder should look like:

- `.../addons21/_friend_pack/__init__.py`

## First-Run Check

After restarting Anki:

1. Open `Tools`.
2. Click `Friend Pack Config`.
3. Open the Browser and verify custom menu actions appear.
4. Right-click selected notes in Browser to verify tagging actions appear.

## Configuration

Use `Tools -> Friend Pack Config` to edit top-level settings.

Files at the root:

- `config.json`: default config schema.
- `config.md`: key reference shown in config window.
- `config_manager.py`: loads/merges/saves config.
- `config_window.py`: config UI and menu registration.

## Updating This Add-on

To update from a newer `_friend_pack`:

1. Close Anki.
2. Run `Install_Friend_Pack.command` from the new download (macOS), or replace folder contents manually.
3. Reopen Anki.

Your profile-level overrides saved by Anki are preserved unless you clear them.

## Troubleshooting

- If `Friend Pack Config` is missing: restart Anki and confirm folder location/name.
- If actions do not appear: ensure notes are selected where required.
- If config save fails: verify `config.json` contains valid JSON.
- If install seems ignored: check for accidental nested folder structure.
