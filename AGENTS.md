# Omarchy cookbook

This is campeterson41's public cookbook in the omarchy-kitchen format. Load the `omarchy-kitchen` skill before changing anything here:

- `format.md` is the recipe format.
- `publish.md` has the privacy rules.

Recipes are published only after Cam approves each specific fix. Weekly discovery runs on automation-host; reports are private review queues, not approval to apply or publish. Never include private configuration or identify private repositories.

Before every commit, run:

```bash
~/.local/share/omarchy-kitchen/bin/kitchen check .
~/.local/share/omarchy-kitchen/bin/kitchen scan --local --cookbook .
```
