# Friend Pack Config

This is the top-level config for `_friend_pack`.

## Top-level Keys

### `add_custom_tags` (object)

Used by `_change_notes/add_custom_tags.py`.

- `submenu_label` (string)
- `presets` (array of objects)

Preset object:

- `label` (string)
- `tags` (array of strings)

### `add_missed_tags` (object)

Used by `_change_notes/add_missed_tags.py`.

- `defaults.menu_label` (string)
- `date.include_day_segment` (boolean)
- `actions` (object)
- `Q_Banks` (array of strings)

`defaults` keys:

- `menu_label` (string): canonical default menu label source.

`date` keys:

- `include_day_segment` (boolean): when `true`, missed date tag becomes
  `##Missed-Qs::YYYY::MM_Month::DD`; when `false`, it remains `##Missed-Qs::YYYY::MM_Month`.

`actions` keys:

- `base` (`label`, `tags`)
- `uworld` (`label`, `base_tags`, `default_tag_prefix`, `test_range_block_size`)
- `nbme` (`label`, `base_tags`, `default_tag_prefix`)
- `amboss` (`label`, `base_tag`, `number_style`, `remove_from_other_menu`)
- `multi_missed` (`label`, `tag_segment`)
- `key_info` (`label`, `tag_base`)
- `correct_guess` (`label`, `tags`)
- `other` (`resources`, `tag_suffix`)

`Q_Banks` behavior:

- Runtime visibility control for bank actions.
- Supported values: `UWORLD`, `NBME`, `AMBOSS`.
- Matching is case-insensitive; unknown values are ignored.

Hardcoded in code (not configurable):

- No-selection and invalid-number messages.
- NBME prompt text (`Enter NBME Form`, `Form #:`).
- NBME tag format (`<nbme_base_tag>::Form_<N>`).

### `browser_menu` (object)

Used by `_browser_menu/loader.py`.

- `top_menu_title` (string)

Browser menu actions are hardcoded in `_browser_menu/loader.py`:

- `Search all`
- `Search 1-by-1`
- `QID search settings` (opens a compact form-based settings window)

### `find_QIDs` (object)

Used by `_browser_menu/helper.py`.

- `QID_parent_tag` (string): primary parent tag for QID searches. If non-empty, query is `tag:re:{QID_parent_tag}::{qid}$`.
- `UW_STEP` (boolean): if true, QID search uses `tag:re:#UWORLD::STEP::{qid}$`.
- `UW_COMLEX` (boolean): if true, QID search uses `tag:re:#UWORLD::COMLEX::{qid}$`.
- `TAG_PREFIX` (string): fallback parent tag used when `QID_parent_tag` is empty and both toggles are false.
- `MISSED_tag` (string): raw parent missed tag used when "missed only" is checked.
- `default_missed_only` (boolean): default checkbox state in Find QIDs dialogs.
- QID precedence: `QID_parent_tag` -> `UW_STEP` -> `UW_COMLEX` -> `TAG_PREFIX`.
- If both toggles are true and `QID_parent_tag` is empty, `UW_STEP` takes priority.
- `QID_parent_tag` and `TAG_PREFIX` accept optional `tag:`/`tag:re:` prefixes and are normalized to exactly one `::{qid}` separator.

## Notes

- Runtime merges this default config with profile overrides written through Anki's addon manager.
- The config window writes the full effective config back to the addon config bucket.
- Root `config.json` is the single source of shipped defaults and canonical schema.
