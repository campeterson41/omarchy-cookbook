# Screensaver and lock start too soon

## Problem

Stock idle timings interrupt reading or watching material without input.

## Why it happens

The stock shell configuration uses a 150-second screensaver and 300-second lock.

## Fix

Merge this idle object into `~/.config/omarchy/shell.json`, preserving its other keys:

```json
"idle": { "screensaver": 450, "lock": 600 }
```

## Apply and check

The shell hot-reloads. In a controlled session, leave input idle and confirm screensaver after 7.5 minutes and lock after 10 minutes. Manual locking still works.

## Undo

Restore the previous values; stock is screensaver 150 and lock 300.

## Notes

Omarchy shell idle handling. Longer lock time leaves an unattended session accessible longer; choose the timing that suits your workspace.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/screensaver-and-lock-start-too-soon",
  "title": "Screensaver and lock start too soon",
  "summary": "Wait 450 seconds for the screensaver and 600 seconds to lock.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Omarchy shell idle handling.",
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
