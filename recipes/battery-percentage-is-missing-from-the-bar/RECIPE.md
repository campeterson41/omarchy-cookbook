# Battery percentage is missing from the bar

## Problem

The battery icon does not tell you the exact charge at a glance.

## Why it happens

The stock power widget is present but its layout entry does not enable showPercentage.

## Fix

Edit the existing omarchy.power item in `~/.config/omarchy/shell.json`:

```json
{ "id": "omarchy.power", "showPercentage": true }
```

## Apply and check

The shell hot-reloads. Check the percentage against the power panel. Keep other bar entries intact.

## Undo

Remove only showPercentage or set it to false.

## Notes

Laptops with a battery.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/battery-percentage-is-missing-from-the-bar",
  "title": "Battery percentage is missing from the bar",
  "summary": "Enable showPercentage on the existing power widget.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Laptops with a battery..",
  "requires": [{"laptop": true}],
  "touches": ["~/.config/omarchy/shell.json"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
