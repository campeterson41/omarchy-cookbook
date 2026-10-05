# Apple function row sends media keys instead of F keys

## Problem

The custom F-key shortcuts are hard to use when the keyboard sends media events by default.

## Why it happens

The Linux hid_apple driver decides whether the function row emits F keys or media events.

## Fix

Back up `/etc/modprobe.d/hid_apple.conf`. Add or update only the fnmode option:

```conf
options hid_apple fnmode=2
```

This is a system setting; writing it requires administrator permission. Preserve any other driver options.

## Apply and check

After a normal reboot, confirm unmodified F9/F11/F12 trigger your chosen function-key bindings and Fn accesses the alternate function. Inspect `/sys/module/hid_apple/parameters/fnmode` if the module is present.

## Undo

Restore the original option or remove only this option and reboot. If your machine loads this configuration from an initramfs, rebuild it using the system’s supported tool before rebooting.

## Notes

Apple keyboards handled by hid_apple. This affects every keyboard using that module, not just one device.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/apple-function-row-sends-media-keys",
  "title": "Apple function row sends media keys instead of F keys",
  "summary": "Set hid_apple fnmode=2 so function keys are primary.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Apple keyboards handled by hid_apple.",
  "requires": [{"command": "modinfo"}],
  "touches": ["/etc/modprobe.d/hid_apple.conf"],
  "root": true,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
