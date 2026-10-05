# Mixed-DPI monitors overlap or change position

## Problem

A 2x laptop screen beside 1x external screens can leave unexpected gaps or overlaps.

## Why it happens

The stock monitor template uses automatic positioning and scaling. Hyprland positions outputs using their scaled logical sizes.

## Fix

In `~/.config/hypr/monitors.lua`, use actual output names from `hyprctl monitors all`. This generalized example matches a 2880x1800 laptop at 2x followed by 1600x900 and 1920x1080 screens at 1x:

```lua
hl.monitor({ output = "eDP-1", mode = "2880x1800@60", position = "0x0", scale = 2 })
hl.monitor({ output = "HDMI-A-1", mode = "1600x900@60", position = "1440x0", scale = 1 })
hl.monitor({ output = "DP-1", mode = "1920x1080@60", position = "3040x0", scale = 1 })
```

The output names and refresh rates are placeholders: choose supported modes. For docks whose connectors change, match a unique display description locally; do not publish its serial number.

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. Confirm the reported positions and scales with `hyprctl monitors -j`; move the pointer between screens and check window sizes.

## Undo

Remove only the explicit monitor rules, restore the previous user rules and reload; keep the stock fallback monitor rule.

## Notes

Mixed-DPI setups with at least two monitors. The 60 Hz example is rounded; the author’s actual outputs use supported fractional refresh rates. No display identifiers are included.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/mixed-dpi-monitors-overlap-or-change-position",
  "title": "Mixed-DPI monitors overlap or change position",
  "summary": "Set each output’s mode, scale, and position in logical pixels.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Mixed-DPI setups with at least two monitors.",
  "requires": [{"monitors": 2}],
  "touches": ["~/.config/hypr/monitors.lua"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
