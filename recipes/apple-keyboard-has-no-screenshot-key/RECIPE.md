# Apple keyboard has no Print Screen key

## Problem

An Apple keyboard has no dedicated Print Screen key.

## Why it happens

Stock `/usr/share/omarchy/default/hypr/bindings/utilities.lua` uses Print Screen for screenshots; applications.lua assigns Super+Shift+S to Google Maps.

## Fix

In `~/.config/hypr/bindings.lua`, replace the Google Maps shortcut:

```lua
hl.unbind("SUPER + SHIFT + S")
o.bind("SUPER + SHIFT + S", "Screenshot", "omarchy-capture-screenshot")
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. Press Super+Shift+S, select a harmless area, and confirm annotation opens.

## Undo

Remove the added binding and its `hl.unbind` line, then run `hyprctl reload` and `hyprctl configerrors`. This restores the stock binding.

## Notes

Apple keyboards, or any keyboard without Print Screen.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/apple-keyboard-has-no-screenshot-key",
  "title": "Apple keyboard has no Print Screen key",
  "summary": "Use Super+Shift+S for the stock screenshot and annotation flow.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Apple keyboards, or any keyboard without Print Screen..",
  "requires": [],
  "touches": ["~/.config/hypr/bindings.lua"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
