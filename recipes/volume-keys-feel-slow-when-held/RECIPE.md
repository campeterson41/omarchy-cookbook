# Volume keys feel slow when held

## Problem

Holding the volume key feels sluggish when displaying the overlay takes longer than changing volume.

## Why it happens

Stock media bindings call the shell audio path. Waiting for UI work on every repeat delays input.

## Fix

Copy [files/omarchy-responsive-volume](files/omarchy-responsive-volume) to `~/.local/bin/omarchy-responsive-volume` and make it executable. Add these bindings, first unbinding any conflicting keys:

```lua
o.bind("F8", "Play/pause", "omarchy-shell media playPause", { locked = true })
o.bind("F10", "Mute", "omarchy-responsive-volume mute", { locked = true })
o.bind("F11", "Volume down", "omarchy-responsive-volume down", { locked = true, repeating = true })
o.bind("F12", "Volume up", "omarchy-responsive-volume up", { locked = true, repeating = true })
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. At a safe initial volume, hold F11 and confirm volume changes promptly with `wpctl get-volume @DEFAULT_AUDIO_SINK@`. Test mute and play/pause. Volume is capped at 100%.

## Undo

Remove the four bindings and helper; restore any earlier key assignments and reload Hyprland.

## Notes

Keyboards exposing F8/F10/F11/F12. These keys replace application function keys and work while locked. The OSD worker is short lived, not a persistent service.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/volume-keys-feel-slow-when-held",
  "title": "Volume keys feel slow when held",
  "summary": "Change PipeWire volume immediately and update the OSD in a shared background worker.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Keyboards exposing F8/F10/F11/F12.",
  "requires": [{"command": "wpctl"}, {"command": "omarchy-osd"}, {"command": "flock"}],
  "touches": ["~/.local/bin/omarchy-responsive-volume", "~/.config/hypr/bindings.lua", "/run/user/<uid>/omarchy-responsive-volume.lock"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
