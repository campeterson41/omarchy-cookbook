# Bar has no button for a custom workspace launcher

## Problem

A frequently used local workflow requires finding its command in a terminal.

## Why it happens

The shell supports user bar widgets, but a custom workflow does not have one by default.

## Fix

Copy [files/manifest.json](files/manifest.json) and [files/BarWidget.qml](files/BarWidget.qml) to `~/.config/omarchy/plugins/cam.workspace/`. This example expects the separate dashboard-workspace launcher recipe. Add `{ "id": "cam.workspace" }` to the desired bar section in `~/.config/omarchy/shell.json`, preserving existing entries. The manifest id, QML moduleName and layout id must agree.

## Apply and check

The shell hot-reloads user plugins. Confirm the button and tooltip appear; left-click to open the launcher. Inspect `omarchy-shell` logs if it does not load.

## Undo

Remove the cam.workspace layout entry and only that user plugin directory. Remove the launcher separately if you no longer use it.

## Notes

Omarchy Quickshell user plugins. This is generalized from an existing workspace button. Its action can start the services declared by its launcher dependency.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/bar-has-no-button-for-a-custom-workspace",
  "title": "Bar has no button for a custom workspace launcher",
  "summary": "Add a small user-owned shell widget that runs a local launcher.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Omarchy Quickshell user plugins.",
  "requires": [{"command": "dashboard-workspace"}],
  "touches": ["~/.config/omarchy/plugins/cam.workspace/", "~/.config/omarchy/shell.json"],
  "root": false,
  "network": true,
  "installs": [],
  "runs": ["services started by dashboard-workspace (separate recipe)"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
