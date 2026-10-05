# Super+Backspace does not delete the current line

## Problem

A familiar line-deletion shortcut instead toggles transparency.

## Why it happens

The stock utilities binding assigns Super+Backspace to window transparency.

## Fix

Copy [files/omarchy-delete-current-line](files/omarchy-delete-current-line) to `~/.local/bin/omarchy-delete-current-line`, make it executable, then add:

```lua
hl.unbind("SUPER + BACKSPACE")
o.bind("SUPER + BACKSPACE", "Delete current line", "omarchy-delete-current-line")
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. In a disposable multiline text field, place the cursor in the middle of a line and press Super+Backspace. Check that the line contents disappear without changing transparency.

## Undo

Remove the override and helper, then reload Hyprland. Restore any pre-existing helper from your backup.

## Notes

Text fields and editors with conventional Home/End navigation. This removes the contents, not necessarily the newline. Editors with smart Home or wrapped lines may select only part of a line; test before using it on important text.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/super-backspace-does-not-delete-a-line",
  "title": "Super+Backspace does not delete the current line",
  "summary": "Send Home, Shift+End, and Backspace as one compositor sequence.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Text fields and editors with conventional Home/End navigation.",
  "requires": [],
  "touches": ["~/.config/hypr/bindings.lua", "~/.local/bin/omarchy-delete-current-line"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
