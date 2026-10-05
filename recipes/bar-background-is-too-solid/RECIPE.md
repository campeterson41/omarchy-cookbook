# Bar background is too solid

## Problem

The stock solid bar hides the background behind it.

## Why it happens

Stock shell.json sets bar.transparent to false.

## Fix

Change only `bar.transparent` in `~/.config/omarchy/shell.json` to `true`. Do not replace the bar layout.

## Apply and check

The shell hot-reloads. Check readability over both light and dark windows/backgrounds.

## Undo

Set `bar.transparent` back to its prior value (stock: false).

## Notes

Omarchy shell bar. Transparency can reduce contrast.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/bar-background-is-too-solid",
  "title": "Bar background is too solid",
  "summary": "Enable the shell’s transparent bar preference.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Omarchy shell bar.",
  "requires": [],
  "touches": ["~/.config/omarchy/shell.json"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
