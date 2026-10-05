# Quick notes are missing from the bar

## Problem

Capturing or consulting a short note takes switching to a separate app.

## Why it happens

OmaNano is a third-party shell plugin, not a stock bar item.

## Fix

The author uses [Agata’s OmaNano](https://github.com/agata/omanano), version 0.1.4. Review its source and current compatibility, then install through the Omarchy plugin command:

```bash
omarchy plugin add https://github.com/agata/omanano --enable
omarchy bar put io.github.agata.omanano --section right
```

This recipe links the upstream plugin; it does not republish its code or any notes.

## Apply and check

Open the widget, create a disposable note, edit it and verify it persists. Test Ctrl+Enter to detach a note and Escape to close the panel. The actual notes live under `~/.local/share/omanano/notes/`.

## Undo

Run `omarchy plugin remove io.github.agata.omanano`. Your notes are preserved by removal; delete them only after a deliberate backup/review.

## Notes

Omarchy shell with third-party plugins. Installation downloads code; review before using it. Ordinary notes remain local Markdown files. Upstream updates may differ from the tested version.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/quick-notes-are-missing-from-the-bar",
  "title": "Quick notes are missing from the bar",
  "summary": "Install the OmaNano local Markdown notes widget.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2", "omanano": "0.1.4"},
  "applies_to": "Omarchy shell with third-party plugins.",
  "requires": [],
  "touches": ["~/.config/omarchy/plugins/io.github.agata.omanano/", "~/.config/omarchy/shell.json", "~/.local/share/omanano/"],
  "root": false,
  "network": true,
  "installs": ["io.github.agata.omanano"],
  "runs": ["OmaNano widget while the shell runs"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
