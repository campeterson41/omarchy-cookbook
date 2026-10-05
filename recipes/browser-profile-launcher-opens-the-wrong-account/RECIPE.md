# Browser profile launcher opens the wrong account

## Problem

A restored browser profile is easy to confuse with the default profile, causing the wrong account or bookmarks to appear.

## Why it happens

Chromium chooses its default user-data directory unless the launcher supplies a separate one.

## Fix

Create `~/.local/share/applications/chromium-secondary.desktop` with a distinct Name and an absolute path to your own existing separate user-data directory. The placeholder below must be replaced locally; desktop Exec does not expand `~` or shell variables:

```desktop
[Desktop Entry]
Type=Application
Name=Chromium (Secondary Profile)
Comment=Open a separate browser profile
Exec=/usr/bin/chromium --user-data-dir=/ABSOLUTE/PATH/TO/SEPARATE/PROFILE %U
Icon=chromium
Terminal=false
Categories=Network;WebBrowser;
```

Use your own account in the actual absolute path, but never publish the profile or its path. Keep the profile separate from Chromium’s default directory. This write-up contains no cookies, account names, history or browser data.

## Apply and check

Open the launcher from the app menu. Check the expected profile/bookmarks appear and the default launcher still opens the normal profile. Close both profiles before any manual migration or copying.

## Undo

Remove only the secondary desktop launcher. Keep the profile directory until you have backed up and reviewed its contents; removing the launcher does not remove your browser data.

## Notes

Chromium users with an existing separately restored profile. This recipe launches a profile; it does not migrate or upload it. The browser itself makes normal network requests when used.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/browser-profile-launcher-opens-the-wrong-account",
  "title": "Browser profile launcher opens the wrong account",
  "summary": "Give a separately restored Chromium profile its own desktop launcher.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Chromium users with an existing separately restored profile.",
  "requires": [{"command": "chromium"}],
  "touches": ["~/.local/share/applications/chromium-secondary.desktop"],
  "root": false,
  "network": true,
  "installs": [],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
