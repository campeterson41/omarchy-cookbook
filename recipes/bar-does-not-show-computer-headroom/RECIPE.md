# Bar does not show computer headroom

## Problem

A busy desktop gives little warning before another job consumes its remaining headroom.

## Why it happens

Stock bar widgets do not display this custom resource-guard telemetry.

## Fix

This depends on the separate heavy-agent-jobs-make-the-desktop-unresponsive recipe and its already-running resource-guard collector. Copy [files/manifest.json](files/manifest.json), [files/ResourceStatus.qml](files/ResourceStatus.qml), and [files/metrics.py](files/metrics.py) into `~/.config/omarchy/plugins/cam.resources/`. Add `{ "id": "cam.resources" }` to the bar’s right layout in `~/.config/omarchy/shell.json`, preserving other widgets. The widget reads one shared state file every three seconds; it does not start a second system sampler.

## Apply and check

Confirm the panel shows CPU, memory, swap and disk percentages and the collector’s admission state. Stop only a disposable test collector to confirm stale readings show an unavailable message, then restore it. On your live system just inspect status; do not interrupt existing work.

## Undo

Remove cam.resources from the bar layout and remove only its plugin directory. Leave the collector in place if any other workflow uses it. Restore earlier files if this plugin already existed.

## Notes

Omarchy Quickshell shell with resource-guard installed. The popup shows local process names; these are not transmitted anywhere. Multiple bar instances read the same collector. No public copy of process data is included.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/bar-does-not-show-computer-headroom",
  "title": "Bar does not show computer headroom",
  "summary": "Display shared CPU, memory, swap, disk, and largest-app readings in a shell panel.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Omarchy Quickshell shell with resource-guard installed.",
  "requires": [{"command": "resource-guard"}, {"command": "python3"}],
  "touches": ["~/.config/omarchy/shell.json", "~/.config/omarchy/plugins/cam.resources/manifest.json", "~/.config/omarchy/plugins/cam.resources/ResourceStatus.qml", "~/.config/omarchy/plugins/cam.resources/metrics.py"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": ["cam.resources widget reader while the shell is running"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
