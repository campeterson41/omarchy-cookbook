# Nouveau pointer disappears on the laptop screen

## Problem

On an older Nouveau-driven laptop panel, the pointer can disappear while the rest of the desktop remains visible.

## Why it happens

Hardware cursor planes use a different display path. A software cursor avoids that path; separate hide settings can also make a working pointer invisible.

## Fix

In `~/.config/hypr/looknfeel.lua` add:

```lua
hl.config({ cursor = {
  no_hardware_cursors = 1,
  use_cpu_buffer = 1,
  hide_on_key_press = false,
  inactive_timeout = 0,
} })
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. Move the pointer across each display, type in a scratch field, leave it idle, and confirm it stays visible. Compare responsiveness with the original setting.

## Undo

Remove only this cursor block, restore any previous cursor overrides, and reload Hyprland.

## Notes

Older GPUs using Nouveau with a disappearing pointer. This is a workaround observed on one setup, not a universal GPU fix. CPU buffers may cost extra CPU or reduce cursor smoothness.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/nouveau-pointer-disappears-on-laptop-screen",
  "title": "Nouveau pointer disappears on the laptop screen",
  "summary": "Use software cursors and keep the pointer visible during typing and idle.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Older GPUs using Nouveau with a disappearing pointer.",
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
