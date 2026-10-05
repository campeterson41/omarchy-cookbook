# Dashboard group opens on a busy workspace

## Problem

Opening a group of local dashboards can reuse a busy browser window or open before its services are ready.

## Why it happens

Ordinary browser launch helpers may focus an existing window. Tunnels and services can need time to become ready.

## Fix

Copy [files/dashboard-workspace](files/dashboard-workspace) to executable `~/.local/bin/dashboard-workspace`. Edit its example ports and matching user-service names for services you already control. The supplied script uses only loopback URLs; no tunnel host, remote account or credentials are published.

The script uses a lock, waits for HTTP responses, picks the lowest empty workspace not visible on another monitor, launches a dedicated Chromium window, then moves that newly observed window to the chosen workspace. It assumes one new Chromium launch at a time.

## Apply and check

Review configured ports/services first, then run `dashboard-workspace`. Confirm the dedicated window has the requested tabs, unrelated windows remain in place, and unreachable services produce a notification. Test with services you can safely start; never start arbitrary example units.

## Undo

Remove only the launcher and any optional keybinding or bar button you added. Services are managed separately: restore only service-start changes you made for this recipe. Close the test browser window manually; the script does not kill other browser sessions.

## Notes

Hyprland with Chromium and existing local dashboard services. Port numbers are examples, not actual remote destinations. The script can start your selected user services on demand; it does not create them. HTTP checks indicate reachability, not application health. Concurrent independent Chromium launches can confuse new-window detection.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/dashboard-group-opens-on-a-busy-workspace",
  "title": "Dashboard group opens on a busy workspace",
  "summary": "Wait for chosen local services, then open one browser window on an empty workspace.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Hyprland with Chromium and existing local dashboard services.",
  "requires": [{"command": "chromium"}, {"command": "hyprctl"}, {"command": "python3"}, {"command": "jq"}, {"command": "curl"}, {"command": "flock"}],
  "touches": ["~/.local/bin/dashboard-workspace", "/run/user/<uid>/dashboard-workspace-<uid>.lock"],
  "root": false,
  "network": true,
  "installs": [],
  "runs": ["pre-existing dashboard user services started on demand", "transient browser user unit"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
