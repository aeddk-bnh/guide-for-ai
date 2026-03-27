---
name: instinct-export
description: Export instincts for sharing.
command: /instinct-export
implementation: python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" export --output instincts.yaml
---

# Instinct Export

Use the CLI export command to write shareable instincts from the current runtime home.

## Example
```bash
python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" export --output instincts.yaml
```
