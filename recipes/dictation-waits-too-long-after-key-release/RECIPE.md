# Dictation waits too long after key release

## Problem

Reloading a speech model for each utterance or waiting indefinitely for final recognition makes push-to-talk feel slow.

## Why it happens

Stock Omarchy uses Voxtype; this customization uses a separate local streaming backend with lightweight socket clients.

## Fix

This is an advanced alternative backend, not a Voxtype configuration tweak. Install [files/streaming_daemon.py](files/streaming_daemon.py) and [files/control_client.py](files/control_client.py) into `~/.local/share/f9-streaming/`. The daemon uses local Moonshine small-streaming English and Vosk small English models. Create a venv in the same directory and install the versions tested below. Download the models using the [Moonshine model guide](https://moonshine-voice.readthedocs.io/en/latest/models/) and the [Vosk model list](https://alphacephei.com/vosk/models), review licensing, and point `--model` at the unpacked Moonshine model. Place the Vosk model at `~/.local/share/f9-streaming/vosk-model-small-en-us-0.15/`.

```bash
python3 -m venv ~/.local/share/f9-streaming/venv
~/.local/share/f9-streaming/venv/bin/pip install moonshine-voice==0.1.5 vosk==0.3.45 numpy==2.5.3
```

Use the local wtype variant described in the separate dictated-text-types-slowly recipe, installing it as `~/.local/share/f9-streaming/f9-wtype`. You also need `parec`, `wl-copy`, `notify-send`, and the optional Voxtype OSD binary. If the Voxtype OSD executable is absent, keep `--no-osd` in the service’s ExecStart command. Copy [files/f9-streaming.service](files/f9-streaming.service) to `~/.config/systemd/user/` and set its `--model` argument to your local model directory. Copy [files/f9-dictation](files/f9-dictation) to executable `~/.local/bin/f9-dictation`.

```bash
systemctl --user daemon-reload
systemctl --user start f9-streaming.service
```

Add to `~/.config/hypr/bindings.lua`:

```lua
hl.unbind("F9")
hl.unbind("SUPER + CTRL + X")
o.bind("F9", "Start dictation", "f9-dictation start")
o.bind("F9", "Stop dictation", "f9-dictation stop", { release = true })
o.bind("SUPER + CTRL + X", "Toggle dictation", "f9-dictation toggle")
```

Avoid a conflicting Voxtype binding/backend. Models remain resident after the first use, but the service is not enabled at login by these steps. The microphone records only while started. Stop uses a 1.35-second recognition budget, preferring a final Moonshine result, then a final Vosk result, then a partial. Output types into the currently focused field; typing failure copies text to the clipboard.

## Apply and check

First validate model loading with `f9-dictation status`. For the initial test add `--output-file` pointing at a disposable text file and `--no-osd` to the service command, then restart only this new service: this avoids typing into a live app. Test short and long utterances, cancellation and release latency; inspect `~/.local/state/f9-streaming/last-result.json`, which contains timings/counts but no transcript. Restore normal output only after those checks, then test in a scratch field. Back up the affected user file before editing. Reload with `hyprctl reload`, then run `hyprctl configerrors`; it should be empty.

## Undo

Remove the F9 and toggle overrides; restore any prior bindings. Stop the service and disable it if you separately enabled it. Remove only the installed unit, wrapper, Python files, venv and model folders, preserving any existing setup you backed up; run `systemctl --user daemon-reload`. Remove the timing state if desired. Uninstall optional tools only if nothing else uses them.

## Notes

English local dictation on Wayland. Speech recognition is imperfect and memory intensive. Bounded finalization can emit an unfinished transcript. The author’s older laptop uses this backend, but each new machine needs model/latency validation. Downloads occur during setup; recording stays local. The daemon does not preserve transcript text, except a deliberately configured output file or clipboard fallback.

The original F9 bindings match modifiers exactly. Holding Shift, Ctrl, Alt, or Super when releasing F9 can prevent the stop binding from matching. If this happens, adapt both bindings with `ignore_mods = true` after checking your Hyprland version; the backend commands remain unchanged. The 120-second safety limit is a fallback, not a substitute for a working release binding.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/dictation-waits-too-long-after-key-release",
  "title": "Dictation waits too long after key release",
  "summary": "Keep Moonshine and Vosk resident and bound the finalization wait after F9 release.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2", "moonshine-voice": "0.1.5", "vosk": "0.3.45"},
  "applies_to": "English local dictation on Wayland.",
  "requires": [{"command": "python3"}, {"command": "parec"}, {"command": "wl-copy"}, {"command": "notify-send"}],
  "touches": ["~/.local/share/f9-streaming/", "~/.local/bin/f9-dictation", "~/.config/systemd/user/f9-streaming.service", "~/.config/hypr/bindings.lua", "~/.local/state/f9-streaming/last-result.json", "/run/user/<uid>/f9-streaming/", "/run/user/<uid>/f9-dictation.lock"],
  "root": false,
  "network": true,
  "installs": ["venv/moonshine-voice==0.1.5", "venv/vosk==0.3.45", "venv/numpy==2.5.3", "Moonshine and Vosk local models", "custom f9-wtype (separate recipe)"],
  "runs": ["f9-streaming.service"],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
