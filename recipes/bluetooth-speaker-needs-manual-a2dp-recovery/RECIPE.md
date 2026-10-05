# Bluetooth speaker needs manual A2DP recovery

## Problem

A Bluetooth speaker or receiver may connect without making its expected audio profile usable.

## Why it happens

Bluetooth pairing and the WirePlumber audio-profile connection policy are separate.

## Fix

Create `~/.config/wireplumber/wireplumber.conf.d/bluetooth-a2dp-autoconnect.conf`:

```conf
monitor.bluez.rules = [
  {
    matches = [ { device.name = "~bluez_card.*" } ]
    actions = { update-props = { bluez5.auto-connect = [ a2dp_sink a2dp_source ] } }
  }
]
```

## Apply and check

Outside a call, run `systemctl --user restart wireplumber`. Reconnect a previously paired device, inspect `wpctl status`, and check playback. Verify input separately if the device offers it.

## Undo

Remove this custom rule, restart WirePlumber, and restore any manually selected profile.

## Notes

PipeWire/WirePlumber Bluetooth audio setups. This applies to all Bluetooth cards; unsupported profiles are not created. A2DP does not guarantee headset microphone support.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/bluetooth-speaker-needs-manual-a2dp-recovery",
  "title": "Bluetooth speaker needs manual A2DP recovery",
  "summary": "Request automatic A2DP playback and capture profile connection.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "PipeWire/WirePlumber Bluetooth audio setups.",
  "requires": [{"command": "wpctl"}],
  "touches": ["~/.config/wireplumber/wireplumber.conf.d/bluetooth-a2dp-autoconnect.conf"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
