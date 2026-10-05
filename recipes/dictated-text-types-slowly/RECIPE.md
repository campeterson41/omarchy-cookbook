# Dictated text types slowly even with zero configured delay

## Problem

Long transcripts take visibly longer to type than to recognize.

## Why it happens

The tested wtype source sleeps twice for each key stroke even at its default zero inter-character delay. In this version `-d 0` is rejected, so simply setting it is not the solution.

## Fix

Use a private build of [atx/wtype](https://github.com/atx/wtype) at commit `d71be3a7b3f93b534a2823fd68cabd7ac2a02359`. [files/no-fixed-sleeps.patch](files/no-fixed-sleeps.patch) changes only those sleeps. [files/LICENSE.wtype](files/LICENSE.wtype) is the upstream MIT notice. Review the source and patch before building; never replace the packaged wtype binary.

```bash
git clone https://github.com/atx/wtype.git ~/.local/share/f9-wtype-source
cd ~/.local/share/f9-wtype-source
git checkout d71be3a7b3f93b534a2823fd68cabd7ac2a02359
# Copy files/no-fixed-sleeps.patch into this checkout first.
git apply --check no-fixed-sleeps.patch
git apply no-fixed-sleeps.patch
meson setup build
ninja -C build -j2
mkdir -p ~/.local/share/f9-streaming
install -m755 build/wtype ~/.local/share/f9-streaming/f9-wtype
```

The build needs a compiler, meson, ninja, Wayland client development files and xkbcommon. Keep resource-sensitive builds guarded if you use resource-guard. Call this binary without `-d 0`.

## Apply and check

In a disposable focused editor, type a known paragraph using the local binary and check character order, punctuation, Unicode and timing. The author’s test produced 1,219 characters in about 315 ms; this is a single-machine observation, not a performance guarantee.

## Undo

Restore your dictation command to packaged wtype and remove only the private build and installed f9-wtype. Leave the packaged executable untouched. If used by the separate streaming recipe, disable that recipe or change its output implementation before removing its binary.

## Notes

Wayland compositors supporting the virtual-keyboard protocol. Removing fixed sleeps can expose timing issues in some applications; keep the packaged binary available for comparison.

## History

- Created by [@campeterson41](https://github.com/campeterson41) on 2026-10-05, from an existing local customization.

## Recipe data

```json
{
  "id": "campeterson41/dictated-text-types-slowly",
  "title": "Dictated text types slowly even with zero configured delay",
  "summary": "Remove wtype’s two fixed 2 ms sleeps while retaining compositor roundtrips.",
  "version": 1,
  "tested_on": {"omarchy": "4.0.4", "hyprland": "0.56.2"},
  "applies_to": "Wayland compositors supporting the virtual-keyboard protocol.",
  "requires": [{"command": "meson"}, {"command": "ninja"}, {"command": "git"}],
  "touches": ["~/.local/share/f9-wtype-source/", "~/.local/share/f9-streaming/f9-wtype"],
  "root": false,
  "network": true,
  "installs": ["private f9-wtype build"],
  "runs": [],
  "agent_config": false,
  "history": [{"who": "campeterson41", "did": "created", "date": "2026-10-05"}]
}
```
