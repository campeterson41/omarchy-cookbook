# Heavy agent jobs make the desktop unresponsive

## Problem

Several agent sessions can start builds or browser tests at once, exhausting CPU, memory, or disk headroom.

## Why it happens

Independent sessions do not share a build slot or system-pressure admission policy. Stock activity widgets show usage but do not coordinate jobs.

## Fix

Install [files/guard.py](files/guard.py) as `~/.local/share/resource-guard/guard.py`, [files/resource-guard](files/resource-guard) as executable `~/.local/bin/resource-guard`, and [files/resource-guard.service](files/resource-guard.service) as `~/.config/systemd/user/resource-guard.service`. Back up existing versions first.

```bash
systemctl --user daemon-reload
systemctl --user enable --now resource-guard.service
~/.local/bin/resource-guard status
~/.local/bin/resource-guard run -- make -j2
```

This uses an advisory lock, systemd scope weights, nice/ionice, and MemoryHigh reclaim pressure without a MemoryMax kill limit. CPU pressure is sustained for 15 seconds before changing admission; low free memory, memory stalls, and critically low disk space defer immediately. Exit 75 means deferred: retry later or offload. Explicit worker limits may still be needed for individual tools. The published `hook` subcommand is optional; this recipe does not install hooks or change agent permissions.

## Apply and check

Use `resource-guard run -- true` for a harmless admission test and `resource-guard status --json` for readings. While a bounded fixture runs, verify a second guarded job waits. Observe actual builds before relying on thresholds. Do not change thresholds to evade pressure.

## Undo

First let guarded jobs finish. Disable and stop only the service you installed: `systemctl --user disable --now resource-guard.service`. Restore backed-up files or remove the installed service, wrapper and directory, then run `systemctl --user daemon-reload`. Remove any optional hooks you installed separately. Do not disable another user’s existing monitor.

## Notes

Linux systems with a systemd user manager and /proc telemetry. This is cooperative scheduling, not a hard resource sandbox. Installation itself runs as your user; the conservative root label covers privileged commands that can be passed to the general-purpose wrapper. Commands launched without the wrapper remain outside the shared slot. Thresholds are chosen for one older laptop and may need deliberate tuning elsewhere.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/heavy-agent-jobs-make-the-desktop-unresponsive",
  "title": "Heavy agent jobs make the desktop unresponsive",
  "summary": "Share one telemetry collector and run heavy jobs in a low-priority serialized scope.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Linux systems with a systemd user manager and /proc telemetry.",
  "requires": [{"command": "python3"}, {"command": "systemd-run"}, {"command": "ionice"}],
  "touches": ["~/.local/share/resource-guard/guard.py", "~/.local/bin/resource-guard", "~/.config/systemd/user/resource-guard.service"],
  "root": true,
  "network": false,
  "installs": [],
  "runs": ["resource-guard.service"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
