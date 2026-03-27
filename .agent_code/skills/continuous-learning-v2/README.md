# Continuous Learning v2

Continuous Learning v2 is a portable skill for collecting session observations and turning repeated patterns into reusable instincts.

## Portable Conventions
Use these variables when wiring the skill into a host environment:
- `CONTINUOUS_LEARNING_HOME`: runtime directory for observations and instincts
- `CONTINUOUS_LEARNING_SKILL_DIR`: installed skill directory

The Python CLI and portable hook entrypoint honor these values.

## VS Code Mapping
Recommended VS Code install shape:
- user scope:
  - `~/.copilot/skills/continuous-learning-v2`
  - `~/.copilot/agents/continuous-learning-observer.agent.md`
  - `~/.copilot/hooks/continuous-learning-v2.json`
  - `chat.hookFilesLocations` patched in VS Code user settings
  - `~/.copilot/continuous-learning-v2`
- repo scope:
  - `.github/skills/continuous-learning-v2`
  - `.github/agents/continuous-learning-observer.agent.md`
  - `.github/hooks/continuous-learning-v2.json`
  - `.github/.continuous-learning-v2`

## Claude-Compatible Fallback
If no portable home is set, the scripts still fall back to `~/.claude/homunculus`.

## Useful Commands
```bash
python <skill-dir>/scripts/instinct-cli.py --home <runtime-home> status
python <skill-dir>/scripts/instinct-cli.py --home <runtime-home> import ./team-instincts.yaml
python <skill-dir>/scripts/instinct-cli.py --home <runtime-home> export --output instincts.yaml
python <skill-dir>/scripts/instinct-cli.py --home <runtime-home> evolve
```

## Notes
- `hooks/observe.py` is the preferred hook entrypoint for new installs.
- `hooks/observe.sh` remains as a compatibility wrapper for shell-based installs.
- `commands/` contains reference docs for the CLI operations.
- `agents/observer.md` is the source document for the observer custom agent.
