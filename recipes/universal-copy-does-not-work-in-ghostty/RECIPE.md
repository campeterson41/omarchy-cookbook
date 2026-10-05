# Universal copy does not work reliably in Ghostty

## Problem

Super+C does not copy the selected terminal text reliably on this setup.

## Why it happens

The stock clipboard helper sends Ctrl+Insert to tagged terminals. Ghostty also supports Ctrl+Shift+C.

## Fix

Put this override in `~/.config/hypr/bindings.lua`:

```lua
hl.unbind("SUPER + C")
o.bind("SUPER + C", "Universal copy", function()
  local window = hl.get_active_window()
  local terminal = false
  if window then
    for _, tag in ipairs(window.tags or {}) do
      if tag:gsub("%*$", "") == "terminal" then
        terminal = true
        break
      end
    end
  end

  local mods = terminal and "CTRL + SHIFT" or "CTRL"
  hl.dispatch(hl.dsp.send_key_state({ mods = mods, key = "C", state = "down" }))
  hl.timer(function()
    hl.dispatch(hl.dsp.send_key_state({ mods = mods, key = "C", state = "up" }))
  end, { timeout = 50, type = "oneshot" })
end)
```

## Apply and check

Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty. Select text in Ghostty, press Super+C, and paste into a scratch editor. Repeat in a browser. Confirm terminal applications still receive their normal Ctrl+C directly.

## Undo

Remove the added binding and its `hl.unbind` line, then run `hyprctl reload` and `hyprctl configerrors`. This restores the stock binding.

## Notes

Terminals tagged by Omarchy, including Ghostty. Untagged terminals need a tag or a more specific match. The timer releases the synthetic key after 50 ms.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/universal-copy-does-not-work-in-ghostty",
  "title": "Universal copy does not work reliably in Ghostty",
  "summary": "Send Ctrl+Shift+C to tagged terminals and Ctrl+C elsewhere.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2", "ghostty": "1.3.1"},
  "applies_to": "Terminals tagged by Omarchy, including Ghostty.",
  "requires": [],
  "touches": ["~/.config/hypr/bindings.lua"],
  "root": false,
  "network": false,
  "installs": [],
  "runs": ["one-shot 50 ms key-release timer"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
