# Dock audio takes over the laptop speakers

## Problem

Connecting a dock or USB audio device can switch playback away from the preferred built-in speakers.

## Why it happens

WirePlumber chooses available default nodes using policy priorities and remembered preferences.

## Fix

Find your speaker node with `wpctl status -n`. Create `~/.config/wireplumber/wireplumber.conf.d/60-preferred-speakers.conf`, replacing the placeholder with your actual node name:

```conf
monitor.alsa.rules = [
  {
    matches = [ { node.name = "YOUR_SPEAKER_NODE" } ]
    actions = { update-props = { priority.session = 1400 } }
  }
]
```

## Apply and check

Restart with `systemctl --user restart wireplumber` when you are not on a call or recording. Reconnect the dock and confirm playback goes to the expected output. A previously pinned default may need resetting in the audio panel.

## Undo

Remove only this custom rule and restart WirePlumber; reselect the earlier default if it was explicitly set.

## Notes

PipeWire/WirePlumber systems with multiple outputs. A remembered manual default can take precedence. This changes output selection, not microphone selection.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/dock-audio-takes-over-laptop-speakers",
  "title": "Dock audio takes over the laptop speakers",
  "summary": "Give the chosen ALSA output a higher WirePlumber session priority.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2", "wireplumber": "0.5.17"},
  "applies_to": "PipeWire/WirePlumber systems with multiple outputs.",
  "requires": [{"command": "wpctl"}],
  "touches": ["~/.config/wireplumber/wireplumber.conf.d/60-preferred-speakers.conf"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
