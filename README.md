# Cam's Omarchy cookbook

Customizations for [Omarchy](https://omarchy.org/), one problem per recipe. Each recipe explains the change, prerequisites, checks and undo steps. These write-ups come from Cam’s existing setup; machine identifiers and work-specific details have been generalized.

Tested setup: Omarchy 4.0.4-1 with Hyprland 0.56.2. Some recipes need older graphics hardware, multiple monitors, or additional tools. Read each recipe’s requirements before applying it. Application and driver updates can change behavior.

To follow this cookbook, ask your agent to set up [omarchy-kitchen](https://github.com/duff/omarchy-kitchen) and follow `campeterson41/omarchy-cookbook`.

## Keyboard and editing

- [Apple keyboard has no Print Screen key](recipes/apple-keyboard-has-no-screenshot-key/RECIPE.md): Use Super+Shift+S for the stock screenshot and annotation flow.
- [Super+Backspace does not delete the current line](recipes/super-backspace-does-not-delete-a-line/RECIPE.md): Send Home, Shift+End, and Backspace as one compositor sequence.
- [Universal copy does not work reliably in Ghostty](recipes/universal-copy-does-not-work-in-ghostty/RECIPE.md): Send Ctrl+Shift+C to tagged terminals and Ctrl+C elsewhere.
- [Volume keys feel slow when held](recipes/volume-keys-feel-slow-when-held/RECIPE.md): Change PipeWire volume immediately and update the OSD in a shared background worker.
- [Apple function row sends media keys instead of F keys](recipes/apple-function-row-sends-media-keys/RECIPE.md): Set hid_apple fnmode=2 so function keys are primary.

## Displays and older hardware

- [Nouveau pointer disappears on the laptop screen](recipes/nouveau-pointer-disappears-on-laptop-screen/RECIPE.md): Use software cursors and keep the pointer visible during typing and idle.
- [Older GPU desktop animations stutter](recipes/older-gpu-desktop-animations-stutter/RECIPE.md): Disable animations and enable adaptive render scheduling.
- [Mixed-DPI monitors overlap or change position](recipes/mixed-dpi-monitors-overlap-or-change-position/RECIPE.md): Set each output’s mode, scale, and position in logical pixels.

## Bar and everyday comfort

- [Bar clock is not in 12-hour format](recipes/bar-clock-is-not-in-12-hour-format/RECIPE.md): Show the weekday and 12-hour time with AM/PM.
- [Battery percentage is missing from the bar](recipes/battery-percentage-is-missing-from-the-bar/RECIPE.md): Enable showPercentage on the existing power widget.
- [Screensaver and lock start too soon](recipes/screensaver-and-lock-start-too-soon/RECIPE.md): Wait 450 seconds for the screensaver and 600 seconds to lock.
- [Bar background is too solid](recipes/bar-background-is-too-solid/RECIPE.md): Enable the shell’s transparent bar preference.
- [Quick notes are missing from the bar](recipes/quick-notes-are-missing-from-the-bar/RECIPE.md): Install the OmaNano local Markdown notes widget.

## Audio

- [Dock audio takes over the laptop speakers](recipes/dock-audio-takes-over-laptop-speakers/RECIPE.md): Give the chosen ALSA output a higher WirePlumber session priority.
- [Bluetooth speaker needs manual A2DP recovery](recipes/bluetooth-speaker-needs-manual-a2dp-recovery/RECIPE.md): Request automatic A2DP playback and capture profile connection.

## Agents and resource monitoring

- [Heavy agent jobs make the desktop unresponsive](recipes/heavy-agent-jobs-make-the-desktop-unresponsive/RECIPE.md): Share one telemetry collector and run heavy jobs in a low-priority serialized scope.
- [Bar does not show computer headroom](recipes/bar-does-not-show-computer-headroom/RECIPE.md): Display shared CPU, memory, swap, disk, and largest-app readings in a shell panel.

## Dictation

- [Dictation waits too long after key release](recipes/dictation-waits-too-long-after-key-release/RECIPE.md): Keep Moonshine and Vosk resident and bound the finalization wait after F9 release.
- [Dictated text types slowly even with zero configured delay](recipes/dictated-text-types-slowly/RECIPE.md): Remove wtype’s two fixed 2 ms sleeps while retaining compositor roundtrips.

## Launchers

- [Dashboard group opens on a busy workspace](recipes/dashboard-group-opens-on-a-busy-workspace/RECIPE.md): Wait for chosen local services, then open one browser window on an empty workspace.
- [Bar has no button for a custom workspace launcher](recipes/bar-has-no-button-for-a-custom-workspace/RECIPE.md): Add a small user-owned shell widget that runs a local launcher.
- [Browser profile launcher opens the wrong account](recipes/browser-profile-launcher-opens-the-wrong-account/RECIPE.md): Give a separately restored Chromium profile its own desktop launcher.
