# Older GPU desktop animations stutter

## Problem

Window movement and transitions can feel heavy on an older GPU and multiple displays.

## Why it happens

Stock looknfeel enables animations. Additional frames increase compositor work on limited graphics hardware.

## Fix

In `~/.config/hypr/looknfeel.lua` add:

```lua
hl.config({
  animations = { enabled = false },
  render = { new_render_scheduling = true },
})
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. Open and move windows on each screen; confirm transitions are immediate and check for flicker. These settings exist in the author’s running setup, but no isolated performance gain is claimed.

## Undo

Remove only these overrides and reload. This restores the stock animation preference and the renderer’s default scheduling.

## Notes

Older GPUs, especially Nouveau setups with multiple displays. Test the two changes separately if you need to identify which helps; adaptive scheduling can be driver dependent.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/older-gpu-desktop-animations-stutter",
  "title": "Older GPU desktop animations stutter",
  "summary": "Disable animations and enable adaptive render scheduling.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Older GPUs, especially Nouveau setups with multiple displays.",
  "requires": [],
  "touches": ["~/.config/hypr/looknfeel.lua"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
