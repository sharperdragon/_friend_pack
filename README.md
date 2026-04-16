# Friend Pack

Friend Pack is a bundled Anki add-on that provides two related workflow tools in a single package:

- **custom Browser menu actions** for question-bank ID searching
- **custom right-click note-tagging actions** for selected notes in the Browser

It is intended for users who organize their Anki workflow around **structured tags**, especially users who work with question-bank-derived note sets and want faster ways to search by QID or apply study-state tags without repetitive manual editing.

Rather than being a general-purpose add-on for every Anki user, Friend Pack is best understood as a **tag-driven workflow utility**. It is most useful when your notes already follow a reasonably consistent tagging system, or when you are willing to customize the default configuration to fit your own structure.

---

## What This Add-on Does

Friend Pack combines two primary features into one add-on to maximize efficiency and studying:

### 1. Browser Menu Tools

Friend Pack adds a custom section to the **Anki Browser menu**.  
These tools are designed to help you search notes by question-bank IDs or related tag patterns.

This is useful when your notes contain tags derived from sources such as:

- UWorld
- NBME
- Amboss
- other Q-bank or resource-specific tagging systems

Instead of manually building tag searches in the Browser every time, the add-on provides menu actions that can run those searches more quickly.

### 2. Right-Click Tagging Tools for Selected Notes

Friend Pack also adds **context-menu actions** when you right-click selected notes in the Browser.

These actions let you apply predefined tags to one or more selected notes. Depending on your configuration, this can support workflows such as:

- tagging missed questions
- tagging repeated misses
- tagging notes for later review
- tagging notes as key information
- tagging notes based on custom personal study categories

The goal is to reduce repetitive manual tagging and make it easier to keep your notes organized during question review.

---

## Who It Is For

Friend Pack is most appropriate for users who already think about their Anki workflow in terms of **tag structure**, not just decks or filtered decks.

It is especially useful for:

- users who organize Anki notes or cards using custom tag workflows
- users who search question-bank IDs in the Browser
- users who want faster right-click actions for note tagging
- users who maintain a consistent naming pattern for tags
- users who are comfortable editing add-on settings to match their own workflow

This add-on may be a good fit if you regularly do things like:

- search for notes linked to a specific question ID
- tag notes as missed after reviewing question blocks
- add custom review-state tags to selected notes
- rely on tag hierarchies to organize study material

This add-on may **not** be a good fit if:

- you do not use tags heavily
- your workflow depends mostly on decks alone
- you want a plug-and-play add-on with no configuration
- your note tags are highly inconsistent and you do not want to adjust them

---

## Main Features

### Browser Menu Features

- Adds a custom top-level menu in the Anki Browser
- Supports question-bank ID style searching
- Can be configured to use different tag roots or tag patterns
- Includes settings related to QID search behavior

### Note Tagging Features

- Adds right-click tagging actions for selected notes in the Browser
- Supports predefined tag actions instead of manual tag typing
- Can be configured for custom label/tag combinations
- Supports workflows built around missed-question tagging and custom review tags

### Configuration Features

- Includes a built-in configuration window
- Ships with default settings in `config.json`
- Stores user-specific overrides through Anki’s config system
- Allows adaptation to different tag structures without directly rewriting module logic

---

## Installation

Friend Pack can be installed either as a local add-on folder or as a packaged `.ankiaddon` file.

---

### Option 1: Local Folder Install

Use this method if you are manually managing the add-on source folder yourself.

#### Steps

1. Close Anki completely.
2. Copy the `_friend_pack` folder directly into your Anki `addons21` folder.
3. Reopen Anki.

The final folder structure should look like this:

```text
.../addons21/_friend_pack/__init__.py