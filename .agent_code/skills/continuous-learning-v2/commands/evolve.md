---
name: evolve
description: Analyze instincts and suggest higher-level structures.
command: /evolve
implementation: python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" evolve
---

# Evolve

Use the CLI evolve command to analyze repeated instincts and suggest evolved skills, commands, or agents.

## Example
```bash
python3 "$CONTINUOUS_LEARNING_SKILL_DIR/scripts/instinct-cli.py" --home "$CONTINUOUS_LEARNING_HOME" evolve --generate
```
