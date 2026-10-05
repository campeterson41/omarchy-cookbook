# Bar clock is not in 12-hour format

## Problem

The default 24-hour display differs from the preferred clock format.

## Why it happens

Stock `config/omarchy/shell.json` gives omarchy.clock the format `dddd HH:mm`.

## Fix

Edit only the existing omarchy.clock item in `~/.config/omarchy/shell.json`; preserve the rest of the layout:

```json
{ "id": "omarchy.clock", "format": "dddd h:mm AP", "formatAlt": "d MMMM 'W'ww yyyy", "verticalFormat": "h\n—\nmm AP" }
```

## Apply and check

The shell hot-reloads the file. Check that the weekday, hour and AM/PM appear; check alternate formatting by using the clock’s normal alternate action.

## Undo

Restore the clock item’s previous format fields; stock uses `dddd HH:mm` and `HH\n—\nmm` vertically.

## Notes

Omarchy shell clock widget.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/bar-clock-is-not-in-12-hour-format",
  "title": "Bar clock is not in 12-hour format",
  "summary": "Show the weekday and 12-hour time with AM/PM.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Omarchy shell clock widget..",
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
