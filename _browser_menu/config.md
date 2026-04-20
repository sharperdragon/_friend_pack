# Find QIDs

Use this module to search notes by QID tag suffix.
`<browser_menu.top_menu_title> -> QID search settings` opens a compact form with:

- `UWorld version`
- `Missed questions tag`
- `QID parent tag`

## Default Config (`_friend_pack/config.json`)

| Key | Type | Purpose |
| --- | --- | --- |
| `QID_parent_tag` | `string` | Primary parent tag for QID searches. If non-empty, query is `tag:re:{QID_parent_tag}::{qid}$`. |
| `UW_STEP` | `boolean` | If `true`, each QID query is `tag:re:#UWORLD::STEP::{qid}$`. |
| `UW_COMLEX` | `boolean` | If `true`, each QID query is `tag:re:#UWORLD::COMLEX::{qid}$`. |
| `MISSED_tag` | `string` | Raw parent missed tag used when "missed only" is enabled. |
| `default_missed_only` | `boolean` | Default checkbox state for missed-only searches. |

Built-in fallback parent (not configurable): `\\bUWorld::\\w+::`

QID search precedence:

1. `QID_parent_tag` (if non-empty)
2. `UW_STEP` (if true)
3. `UW_COMLEX` (if true)
4. built-in fallback (`tag:re:\\bUWorld::\\w+::{qid}$`)

If both mode toggles are `true` and `QID_parent_tag` is empty, `UW_STEP` takes priority.

Normalization for `QID_parent_tag`:

- Optional `tag:` / `tag:re:` prefixes are accepted and stripped.
- Trailing `:` / `::` are accepted and normalized.
- Query builder always emits exactly one `::{qid}` separator.

## Defaults

```json
{
  "QID_parent_tag": "",
  "UW_STEP": false,
  "UW_COMLEX": false,
  "MISSED_tag": "##Missed-Qs",
  "default_missed_only": false
}
```
