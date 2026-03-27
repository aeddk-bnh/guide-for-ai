---
name: continuous-learning-v2
description: Instinct-based learning system that records tool-use observations through hooks, stores them as local runtime data, and helps evolve repeated patterns into instincts, skills, commands, or agents.
version: 2.1.0
---

# Continuous Learning v2

## Goal
Turn repeated coding behavior into reusable local knowledge.

The system has three parts:
- hooks append normalized tool events to `observations.jsonl`
- scripts inspect those observations and manage instincts
- an optional observer agent reviews patterns and drafts new instincts

## Runtime Roots
Use these variables to make the skill portable across environments:
- `CONTINUOUS_LEARNING_HOME`: runtime directory for observations, instincts, and evolved artifacts
- `CONTINUOUS_LEARNING_SKILL_DIR`: installed skill directory

If no override is provided, scripts fall back to `~/.claude/homunculus` for backward compatibility.

## VS Code Support
The VS Code installer should provide:
- user scope:
  - `~/.copilot/skills/continuous-learning-v2`
  - `~/.copilot/agents/continuous-learning-observer.agent.md`
  - `~/.copilot/hooks/continuous-learning-v2.json`
  - `chat.hookFilesLocations` patched in VS Code user settings
  - runtime home: `~/.copilot/continuous-learning-v2`
- repo scope:
  - `.github/skills/continuous-learning-v2`
  - `.github/agents/continuous-learning-observer.agent.md`
  - `.github/hooks/continuous-learning-v2.json`
  - runtime home: `.github/.continuous-learning-v2`

The installed hook file should set `CONTINUOUS_LEARNING_HOME` and `CONTINUOUS_LEARNING_SKILL_DIR` automatically. The installer should also register the user hook directory in `chat.hookFilesLocations`.

## Quick Start
### VS Code user scope
```bash
python ~/.copilot/skills/continuous-learning-v2/scripts/instinct-cli.py --home ~/.copilot/continuous-learning-v2 status
python ~/.copilot/skills/continuous-learning-v2/scripts/instinct-cli.py --home ~/.copilot/continuous-learning-v2 evolve
```

### VS Code repo scope
```bash
python .github/skills/continuous-learning-v2/scripts/instinct-cli.py --home .github/.continuous-learning-v2 status
python .github/skills/continuous-learning-v2/scripts/instinct-cli.py --home .github/.continuous-learning-v2 evolve
```

### Claude-compatible fallback
```bash
python ~/.claude/skills/continuous-learning-v2/scripts/instinct-cli.py status
```

## What the Hook Records
Each hook invocation appends one normalized event to `observations.jsonl`:
- timestamp
- event type such as `tool_start` or `tool_complete`
- tool name
- session id when available
- compact input or output payloads

## Main Workflows
### 1. Observe
- Install the hook config for your environment.
- Let sessions accumulate observations.
- Disable temporarily by creating `<runtime-home>/disabled`.

### 2. Inspect instincts
- Run `status` to view current instincts.
- Run `export` to share local instincts.
- Run `import` to merge inherited instincts.

### 3. Evolve patterns
- Run `evolve` after enough observations exist.
- Review suggested clusters before turning them into higher-level structures.

### 4. Review with the observer agent
- Use the `continuous-learning-observer` custom agent when you want AI help drafting or refining instincts.
- The agent should read `observations.jsonl`, inspect existing instincts, and write conservative updates to `instincts/personal/`.

## Runtime Layout
```text
<CONTINUOUS_LEARNING_HOME>/
  observations.jsonl
  observations.archive/
  disabled
  instincts/
    personal/
    inherited/
  evolved/
    skills/
    commands/
    agents/
```

## Files in this Skill
- `hooks/observe.py`: portable hook entrypoint for VS Code and Claude-style hook payloads
- `hooks/observe.sh`: shell wrapper for existing Claude-style installs
- `scripts/instinct-cli.py`: manage status, import, export, and evolve
- `agents/observer.md`: source instructions for the observer custom agent
- `commands/`: reference docs for the CLI actions

## Rules
- Keep all learned data local unless the user explicitly exports it.
- Never store full code snippets in instincts when pattern summaries are enough.
- Prefer conservative instinct creation: repeated evidence beats single-session guesses.
- Treat imported instincts as inherited suggestions, not hard rules.
