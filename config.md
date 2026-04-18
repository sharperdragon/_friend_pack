# Friend Pack Config Guide

This guide explains the settings available in **Friend Pack** in plain English.

You do **not** need to understand Python or config file structure to use these
settings. Most users only need to change a few labels or tag names to match
their own workflow.

Use **Tools → Friend Pack Config** to edit these settings.

---

## Quick Overview

Friend Pack has four main setting areas:

### 1. Custom Tags

Controls the preset tag actions that appear in the right-click menu for
selected notes.

### 2. Missed Tags

Controls the submenu for tagging missed questions, repeated misses,
guessed-correct questions, and similar review states.

### 3. Browser Menu

Controls the title of the custom Friend Pack menu in the Anki Browser.

### 4. Find QIDs

Controls how Friend Pack searches for question-bank IDs in the Browser.

---

## `add_custom_tags`

This section controls the **Custom Tags** submenu that appears when you right-click
selected notes in the Browser.

Use this when you want quick preset tag actions instead of typing tags manually
every time.

### `submenu_label`

This is the name shown in the right-click menu.

Example:

- `Custom Tags`

If you change this, the menu title changes, but the underlying tag behavior
stays the same.

### `presets`

These are your saved custom tagging actions.

Each preset has two parts:

#### `label`

This is the text you see in the menu.

Examples:

- `Needs Review`
- `Imaging`
- `Rewatch Lecture`

#### `tags`

These are the tags that will be added when you click that preset.

Examples:

- `#Custom::Review`
- `#Custom::Imaging`
- `#Custom::Rewatch`

**Example:**

If you create a preset like this:

- label: `Needs Review`
- tags: `#Custom::Review`

then right-clicking selected notes and choosing **Needs Review** will add the tag:

- `#Custom::Review`

**When to edit this section:**

Edit this section if you want to:

- rename the Custom Tags submenu
- add new preset tag actions
- remove presets you do not use
- change which tags get added by each preset

---

## `add_missed_tags`

This section controls the **Missed Tags** submenu and the tag-building behavior
used for missed-question workflows.

This is the most important section for users who organize notes based on missed
questions, question-bank source, repeat misses, or custom review states.

### Standardized Structure

`add_missed_tags` now supports a standardized top-level + action model:

- Top-level:
  - `menu_label`
  - `date`
  - `primary_missed_tag`
  - `actions`
- Per action (inside `actions.*`):
  - `label`
  - `child_of_primary_missed` (boolean)
  - `add_missed_date_context` (boolean)
  - `tag_segment` (for child tags) or `absolute_tags` (for non-child tags)
  - optional `prompt` object:
    - `kind` (`none`, `number`, or `form`)
    - `number_style` (`range_then_number` or `number_only`)
    - `range_block_size` (integer)
    - `input_items` (array of strings; used by `kind: form`)
- Special shape for `actions.other`:
  - `submenu_bool`, `submenu_label`
  - `tagging` object (`child_of_primary_missed`, `add_missed_date_context`, `tag_segment_group`, `group_segment`)
  - `actions` array (`menu_label`, `tag_segment`, optional `prompt`)

`primary_missed_tag` is the canonical root used for missed-date tags and for any
action with `child_of_primary_missed: true`.

Legacy keys (`tags`, `base_tags`, `base_tag`, `tag_base`, `tag_segments`) are still
accepted for backward compatibility for non-`other` actions, and
`defaults.menu_label` is still accepted as a fallback for older configs.

`actions.other.resources/tag_suffix` is deprecated and no longer supported.

---

### `menu_label`

This controls the name of the **Missed Tags** submenu in the right-click menu.

Example:

- `Missed Tags ❌`

Change this if you want the menu title to say something else, such as:

- `Question Review Tags`
- `Missed Question Tags`

---

### `date`

#### `include_day_segment`

This controls how detailed the automatic missed-question date tags are.

**If `true`:**

The tag includes the **year, month, and day**.

Example:

- `##Missed-Qs::2026::04_April::16`

**If `false`:**

The tag includes only the **year and month**.

Example:

- `##Missed-Qs::2026::04_April`

**When to edit this section:**

Use `true` if you want very specific tracking by day.

Use `false` if you want cleaner, broader monthly grouping.

---

### `actions`

This area controls the individual actions shown inside the **Missed Tags** submenu.

Each action can have different settings depending on what it does.

---

### `base`

This is the most basic missed-question tagging action.

#### `label`

The text shown in the menu.

Example:

- `♦️Base`

#### `absolute_tags`

The base missed-question tags that get added.

Example:

- `##Missed-Qs`

Use this as your main missed-question root if you want a simple top-level tag added.

---

### `uworld`

This controls the UWorld-specific missed-tag action.

Use this if your notes are organized around UWorld question blocks or UWorld-derived
tags.

#### `label`

The menu text shown for this action.

Example:

- `🛃UWorld`

#### `tag_segment`

Child segment under `primary_missed_tag`.

Example:

- `UW_Tests`

#### `prompt`

Controls prompt behavior for this action.

Example:

- `kind: number`
- `number_style: range_then_number`
- `range_block_size: 25`

---

### `nbme`

This controls the NBME-specific missed-tag action.

Use this if you want to organize missed notes by NBME form or related NBME tags.

#### `label`

The menu text shown for this action.

Example:

- `🧠 NBME`

#### `tag_segment`

Child segment under `primary_missed_tag`.

Example:

- `NBME`

#### `prompt`

Controls prompt behavior for this action.

Example:

- `kind: form` (default NBME behavior)
- `input_items: ["Form"]`
- `number_style: number_only`
- `range_block_size: 25`

---

### `amboss`

This controls the Amboss-specific missed-tag action.

Use this if your notes or missed-question workflow includes Amboss-derived tags.

#### `label`

The menu text shown for this action.

Example:

- `🦠 Amboss`

#### `tag_segment`

Child segment under `primary_missed_tag`.

Example:

- `Amboss`

#### `prompt`

Controls prompt behavior for this action.

Example:

- `kind: number`
- `number_style: number_only`
- `range_block_size: 25`

Amboss is always its own dedicated action (not part of `other.actions`).

---

### `multi_missed`

This controls the action for marking notes that were missed more than once.

#### `label`

The menu text shown for this action.

Example:

- `2x Missed 📌`

#### `tag_segment`

The tag segment used to mark repeat misses.

Example:

- `2x`

This is useful if you want to flag notes that need extra review because they have
been missed repeatedly.

### `correct_guess`

This controls the action for marking notes you got right, but only by guessing.

#### `label`

The menu text shown for this action.

Example:

- `Guessed Correct 🎫`

#### `absolute_tags`

The tags added by this action.

Example:

- `#Custom::correct_marked`

This can be useful if you want to revisit notes that were technically correct but
not confidently known.

---

### `other`

This controls a configurable set of **Other** actions.

#### `submenu_bool`

If `true`, Other actions are grouped into a submenu.

If `false`, Other actions are shown directly in the Missed Tags menu.

#### `submenu_label`

Label used when `submenu_bool` is `true`.

Example:

- `Other`

#### `tagging`

Global tagging behavior for all `other.actions`.

Keys:

- `child_of_primary_missed` (boolean)
- `add_missed_date_context` (boolean, global-only)
- `tag_segment_group` (boolean)
- `group_segment` (string)

`other.actions[].add_missed_date_context` is not supported.

Tag path behavior:

- If `child_of_primary_missed=true` and `tag_segment_group=true`:
  `{primary_missed_tag}::{group_segment}::{actions[].tag_segment}`
- If `child_of_primary_missed=false` and `tag_segment_group=true`:
  `{group_segment}::{actions[].tag_segment}`
- If `child_of_primary_missed=true` and `tag_segment_group=false`:
  `{primary_missed_tag}::{actions[].tag_segment}`
- If `child_of_primary_missed=false` and `tag_segment_group=false`:
  `{actions[].tag_segment}`

#### `actions`

Array of action items.

Each item supports:

- `menu_label` (string)
- `tag_segment` (string)
- optional `prompt` object:
  - `kind` (`none`, `number`, `form`)
  - `number_style` (`range_then_number`, `number_only`)
  - `range_block_size` (integer)
  - `input_items` (array of strings; used by `kind: form`)

Example:

```json
"other": {
  "submenu_bool": true,
  "submenu_label": "Other",
  "tagging": {
    "child_of_primary_missed": true,
    "add_missed_date_context": false,
    "tag_segment_group": true,
    "group_segment": "Other"
  },
  "actions": [
    {
      "menu_label": "Kaplan",
      "tag_segment": "Kaplan",
      "prompt": { "kind": "none" }
    },
    {
      "menu_label": "True-learn",
      "tag_segment": "True-learn",
      "prompt": { "kind": "none" }
    }
  ]
}
```

---

### Bank Actions (Fixed)

Bank visibility is fixed in code (not configurable).
Friend Pack always enables the built-in bank actions:

- `UWORLD`
- `NBME`
- `AMBOSS`

---

## `browser_menu`

This section controls the top-level Friend Pack menu in the **Anki Browser**.

### `top_menu_title`

This is the title shown in the Browser menu bar.

Example:

- `Custom`

If you change this to something else, that new name will appear in the Browser.

Examples:

- `Friend Pack`
- `QID Tools`
- `Study Search`

**Important note:**

This setting only changes the menu title.

The built-in Browser menu actions themselves are still provided by the add-on, such as:

- `Search all`
- `Search 1-by-1`
- `QID search settings`

---

## `find_QIDs`

This section controls how Friend Pack searches for question IDs in the Browser.

This is most useful if your notes are tagged with question-bank IDs and you want
fast QID-based search tools.

---

### `QID_parent_tag`

Use this if your QID tags live under one main parent tag.

If this is filled in, Friend Pack will try to search using that parent tag first.

Example:

- `#UWorld`
- `#QBank`
- `#UWORLD::STEP`

Use this when your QID tags are organized neatly under one consistent parent path.

---

### `UW_STEP`

This tells Friend Pack to use the built-in UWorld STEP tag path.

**If `true`:**

Friend Pack searches using the STEP-style UWorld path.

**If `false`:**

It does not use that built-in path unless another setting directs it.

Use this if your UWorld tags follow the add-on’s expected STEP format.

---

### `UW_COMLEX`

This tells Friend Pack to use the built-in UWorld COMLEX tag path.

**If `true`:**

Friend Pack searches using the COMLEX-style UWorld path.

**If `false`:**

It does not use that built-in path unless another setting directs it.

Use this if your UWorld tags follow a COMLEX-based structure.

---

### `TAG_PREFIX`

This is the advanced fallback pattern used if the earlier QID settings are not being used.

Example:

- `\\bUWorld::\\w+::`

This is mainly for users who already understand how their QID tags are structured
and need a more custom search pattern.

#### Practical advice

If your QID searches already work using `QID_parent_tag`, `UW_STEP`, or
`UW_COMLEX`, you may not need to change this.

Only edit this if:

- your QID tags use a different pattern
- the simpler options do not match your setup
- you understand the format you need

---

### `MISSED_tag`

This is the parent missed-question tag used when a QID search is limited to missed
items only.

Example:

- `##Missed-Qs`

If your missed-question tags use a different root, change this to match your actual
tag structure.

---

### `default_missed_only`

Controls whether the **missed only** option starts checked by default in QID search
dialogs.

**If `true`:**

QID searches start in missed-only mode unless you change it.

**If `false`:**

QID searches include all matching notes unless you manually restrict to missed only.

Use `true` if you almost always care about missed-question review.

Use `false` if you usually want the full set of matches.

---

**Search priority:**

Friend Pack checks QID settings in this order:

1. `QID_parent_tag`
2. `UW_STEP`
3. `UW_COMLEX`
4. `TAG_PREFIX`

That means if `QID_parent_tag` is filled in, it takes priority over the other options.

If both `UW_STEP` and `UW_COMLEX` are turned on and no `QID_parent_tag` is set,
Friend Pack gives priority to `UW_STEP`.

---

## Most Common Settings to Edit

If you are not sure where to start, these are the settings most users are most likely
to change:

- **Menu names**
  - `add_custom_tags.submenu_label`
  - `add_missed_tags.menu_label`
  - `browser_menu.top_menu_title`

- **Custom preset tags**
  - `add_custom_tags.presets`

- **Missed-question tag roots**
  - `add_missed_tags.actions.base.absolute_tags`
  - `add_missed_tags.actions.uworld.tag_segment`
  - `add_missed_tags.actions.nbme.tag_segment`
  - `add_missed_tags.actions.amboss.tag_segment`
  - `find_QIDs.MISSED_tag`

- **QID search settings**
  - `find_QIDs.QID_parent_tag`
  - `find_QIDs.UW_STEP`
  - `find_QIDs.UW_COMLEX`
  - `find_QIDs.TAG_PREFIX`

---

## Practical Tips

- **Keep labels readable**

  Labels are what you see in Anki menus. Keep them short and clear.

- **Match tags to your real workflow**

  If your actual tag structure does not match the default config, update the tag
  values before relying on the add-on.

- **Change one section at a time**

  If you make many config changes at once and something stops working, it becomes
  harder to tell which change caused the problem.

- **Be careful with advanced QID settings**

  If you are unsure how your QID tags are structured, start with simpler settings
  like `QID_parent_tag` before changing `TAG_PREFIX`.

---

## Final Note

The shipped defaults are designed for a structured tag-based study workflow.
They are meant to be a solid starting point, not a universal standard.

If your tags already follow a similar system, you may only need small changes.
If your setup is very different, expect to customize the config before Friend Pack
fits your workflow well.
