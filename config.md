# Friend Pack Guide

### Quick Overview
Friend Pack has four main setting areas:

**1) Missed Tags**  
Controls the browser right-click submenu for tagging missed questions, repeated misses,
guessed-correct questions, and similar review states.

**2) Find QIDs**  
Searches for notes tagged with question IDs from popular Q-banks.

**3) Custom Tags***  
Preset tag actions that appear in the right-click menu for selected notes.

<div style="margin:0;padding:0;line-height:70%">
<span style="font-size: 75%">*Custom Tags is a bonus section for easily adding your own tags to notes.</span>
</div>

**4) Browser Menu**  
Controls the title of the top-level Friend Pack menu in the Anki Browser.

---

## Quick Reference

### Missed Tags

***General Key Definitions***

| Key | Function | Default |
|---|---|---|
| `menu_label` | Menu text shown in the Browser right-click menu | `Missed Tags ❌` |
| `primary_missed_tag` | Main root tag used for missed-question tagging.<br>For best results, this should match `find_QIDs > MISSED_tag` | `##Missed-Qs` |
| `include_day_segment` | Controls whether missed-date tags include the day or only year/month | `True` |
| `tag_segment` | Child tag segment added under `primary_missed_tag` for an action | Various |
| `absolute_tags` | Full tag or tags added directly for actions that are **not** being tagged under `primary_missed_tag` | Various |
| `child_of_primary_missed` | Controls whether the action builds its tags under `primary_missed_tag` | Usually `True` |
| `add_missed_date_context` | Controls whether the action includes missed-date context | Usually `True` |
| `prompt > kind` | Prompt type used by an action | Usually `none` |
| `prompt > number_style` | Number-entry style used by an action prompt | Usually `number_only` |
| `prompt > range_block_size` | Range group size used for organizing numbered tags | `25` |

Default action-wide fallback values come from `action_defaults`. Those defaults are used unless an individual action overrides them.

---

#### ***Prompt Section***

Use `prompt` when an action needs extra input before tagging.


- `kind: none`  
  No extra prompt is shown.

- `kind: number`  
  Prompts for a number, usually for question-bank blocks or IDs.

- `kind: form`  
  Prompts using a form-style selection or entry flow.

- `number_style: range_then_number`  
  Organizes numbers by range first, then exact number.

- `number_style: number_only`  
  Uses only the exact number without a range grouping.

---

#### ***Default Action Behavior***

The standard actions all use the same general keys above:

- `base`
- `uworld`
- `multi_missed`
- `nbme`
- `amboss`
- `correct_guess`

Their shipped defaults are:

| Action | Key Setting | Default |
|---|---|---|
| `base` | `menu_label` | `♦️ Base` |
| `base` | `child_of_primary_missed` | `False` |
| `base` | `absolute_tags` | `["##Missed-Qs"]` |
| `base` | `add_missed_date_context` | `False` |
| `uworld` | `menu_label` | `🗺️ UWorld` |
| `uworld` | `tag_segment` | `UW_Tests` |
| `uworld` | `prompt > kind` | `number` |
| `uworld` | `prompt > number_style` | `range_then_number` |
| `uworld` | `prompt > range_block_size` | `25` |
| `multi_missed` | `menu_label` | `2x Missed 📌` |
| `multi_missed` | `tag_segment` | `2x` |
| `nbme` | `menu_label` | `🧠 NBME` |
| `nbme` | `tag_segment` | `NBME` |
| `nbme` | `prompt > kind` | `form` |
| `nbme` | `prompt > number_style` | `number_only` |
| `amboss` | `menu_label` | `🦠 Amboss` |
| `amboss` | `tag_segment` | `Amboss` |
| `amboss` | `prompt > kind` | `number` |
| `amboss` | `prompt > number_style` | `number_only` |
| `correct_guess` | `menu_label` | `Guessed Correct 🎫` |
| `correct_guess` | `child_of_primary_missed` | `False` |
| `correct_guess` | `absolute_tags` | `["#Custom::correct_marked"]` |

---

#### ***Other Section***

`other` is for custom extra sources or workflows, such as Kaplan or TrueLearn.

| Key | Function | Default |
|---|---|---|
| `actions > other > submenu_label` | Label for the **Other** submenu when enabled | `Other` |
| `actions > other > submenu_bool` | Controls whether **Other** actions appear inside their own submenu | `True` |
| `actions > other > tagging > child_of_primary_missed` | Controls whether Other actions are placed under the main missed root tag | `True` |
| `actions > other > tagging > tag_segment_group` | Controls whether Other actions use a shared group tag segment | `True` |
| `actions > other > tagging > add_missed_date_context` | Controls whether Other actions include missed-date context | `False` |
| `actions > other > tagging > group_segment` | Shared group segment used for Other actions | `Other` |

The items under `actions > other > actions > ...` use the same higher-level action keys:
- `menu_label`
- `tag_segment`
- optional `prompt`

**Default shipped examples:**
- `Kaplan 🟣`
- `True-learn 🌀`

---

### Find QIDs

| Key | Function | Default |
|---|---|---|
| `QID_parent_tag` | Main parent tag Friend Pack searches first for QID tags | `""` |
| `UW_STEP` | Set **true** if QID tags follow the built-in UWorld STEP pattern | `False` |
| `UW_COMLEX` | Set **true** if QID tags follow the built-in UWorld COMLEX pattern | `False` |
| `MISSED_tag` | Primary tag used to limit QID searches to missed-question notes.<br>For best results, it should match `add_missed_tags > primary_missed_tag` | `##Missed-Qs` |
| `default_missed_only` | `True`: automatically filters by `MISSED_tag` when running a QID search in missed-only mode by default | `False` |

**Practical note:**  
If `QID_parent_tag` is filled in, Friend Pack tries that first.  
If it is blank, Friend Pack falls back to built-in search behavior based on the other QID settings.

---

### Custom Tags

| Key | Function | Default |
|---|---|---|
| `submenu_label` | Name of the **Custom Tags** submenu shown in the Browser right-click menu | `Custom Tags` |
| `presets > menu_label` | Text shown for one preset menu item | User-defined |
| `presets > tags` | Tag or tags added when the menu action is clicked | User-defined |

<br>

**Default Examples:**
Add to adds the array of items under `tags`. Only examples, addition added for refernence
```
    "presets": [
      {
        "menu_label": "📝 Needs Review",
        "tags": ["#Custom::Review"]
      },
      {
        "menu_label": "Imaging 🩻",
        "tags": ["#Imaging", "#Custom::other"]
      },
      ...
      {
        "menu_label": "label-N",
        "tags": [
          "#Custom::other",
          "TAG_N::example",
          "#Custom::Review:Tag-n"
          ]
      **}**
    ]
  }
```
- The "📝 Needs Review" action adds only the tag named "#Custom::Review".
- The "Imaging 🩻" action adds the tags "#Imaging" and the tag "#Custom::other"
- The action "label-N" adds the tags "#Custom::other" and the tag "TAG_N"

Tags created:
```
#Custom
├── Review
│   └── Tag-n
└── other
TAG_N
└── example
```


---

### Browser Menu

`top_menu_title`: Title of the top-level Friend Pack menu in the Anki Browser. Default is `Custom`

---

### Examples

**Current default behavior:**

Pressing **Missed Tags ❌** gives you actions for:
- `♦️ Base`
- `🗺️ UWorld`
- `2x Missed 📌`
- `🧠 NBME`
- `🦠 Amboss`
- `Guessed Correct 🎫`
- `Other` submenu

**Examples of resulting tags:**

- Pressing **♦️ Base** adds:  
  `##Missed-Qs`

- Pressing **🗺️ UWorld** and entering a number builds a child tag under:  
  `##Missed-Qs::UW_Tests::...`

- Pressing **2x Missed 📌** builds a child tag under:  
  `##Missed-Qs::2x::...`

- Pressing **🧠 NBME** builds a child tag under:  
  `##Missed-Qs::NBME::...`

- Pressing **🦠 Amboss** builds a child tag under:  
  `##Missed-Qs::Amboss::...`

- Pressing **Guessed Correct 🎫** adds:  
  `#Custom::correct_marked`

- Pressing **Other → Kaplan 🟣** builds a child tag under:  
  `##Missed-Qs::Other::Kaplan`

- Pressing **Other → True-learn 🌀** builds a child tag under:  
  `##Missed-Qs::Other::True-learn`