---
name: instinct-import
description: Import instincts from a file or URL.
command: /instinct-import
implementation: python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" import <file-or-url>
---

# Instinct Import

Use the CLI import command to merge inherited instincts into the current runtime home.

## Example
```bash
python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" import ./team-instincts.yaml
```
