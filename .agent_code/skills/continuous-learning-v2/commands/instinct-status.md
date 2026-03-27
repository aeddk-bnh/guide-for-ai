---
name: instinct-status
description: Show learned instincts with their confidence levels.
command: /instinct-status
implementation: python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" status
---

# Instinct Status

Run the CLI status command against the current runtime home.

## Example
```bash
python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" status
```
