# Codebase Map

## Snapshot
- Purpose: Install shared agent content from `.agent_code/` into multiple target tools.
- Primary stack: Python installer scripts plus shell/batch wrappers.
- Main runtimes: Python 3, Windows batch, POSIX shell.
- Entry points: `install.bat`, `install.sh`, `install_agent_env.py`.

## Top-Level Layout
- `.agent_code/`: canonical source content and support scripts.
- `install_agent_env.py`: unified target selection and dedupe logic.
- `setup_agent_env.py`: classic target installer backend.
- `setup_codex_env.py`: Codex backend.
- `setup_gemini_env.py`: Gemini CLI backend.
- `README.md`: user-facing install docs.

## Module Map
| Module | Role | Key files | Edit here when | Depends on | Used by |
| --- | --- | --- | --- | --- | --- |
| Unified installer | Parses flags, computes dedupe, orchestrates backends | `install_agent_env.py` | Adding targets, scopes, shared-surface policy | `.agent_code`, backend scripts | `install.bat`, `install.sh` |
| Classic backend | Installs Cursor, VS Code, Claude, Antigravity assets | `setup_agent_env.py` | Changing classic target paths or VS Code hook/settings behavior | `.agent_code`, `manage_agent_config.py` | Unified installer |
| Codex backend | Repackages core, skills, workflows, subagents for Codex | `setup_codex_env.py` | Changing Codex output layout or TOML conversion | `.agent_code` | Unified installer |
| Gemini backend | Repackages content into Gemini CLI commands | `setup_gemini_env.py` | Changing Gemini command mapping or TOML output | `.agent_code` | Unified installer |
| Source content | Canonical prompts, skills, workflows, subagents | `.agent_code/core`, `.agent_code/skills`, `.agent_code/workflows`, `.agent_code/subagents` | Updating agent behavior/content | none | All installers |

## Interaction Map
- Flow: wrappers -> unified installer -> target backend(s) -> target-specific output paths.
- Dedupe: unified installer computes overlap policy before invoking backends.
- Content adaptation: backends preserve source text where possible and only adapt format/path/tool-surface requirements.
- Current walkthrough confirms the repo behaves like a content-porting pipeline: source markdown/prompts in `.agent_code/` are transformed into each target tool's expected file layout.

## Change Guide
- If adding a new target: update unified target parsing, add a backend or target branch, update README, and test standalone plus mixed installs.
- If changing overlap behavior: edit dedupe planning in `install_agent_env.py` and corresponding backend switches.
- If changing prompt content: edit `.agent_code/` first, then keep installer adaptations minimal.

## Validation Guide
- Main checks: `python -m py_compile` on installer backends and smoke installs into temp directories.
- Regression attention: scope defaults, shared discovery surfaces, and recursive folder skills such as `continuous-learning-v2`.

## Cross-Cutting Concerns
- Config and env: multiple tools use home-directory defaults and per-project overrides.
- Testing: smoke tests rely on temp homes/project roots; avoid mutating real user config unless explicitly intended.
- Hotspots: dedupe logic, shared surfaces like `AGENTS.md` / `.agents/skills`, and target docs drift.

## Unknowns
- Some third-party tool docs are inconsistent about global agent paths; runtime verification may be needed before locking behavior.
- If this repo later adds Claude Code-specific UX helpers, prefer the documented `statusLine` surface for session metadata instead of hook-based rendering.
- Practical setup note from live validation: on this Windows environment, `jq` was unavailable in Git Bash, so a portable Python-backed `statusLine` parser is more reliable than a jq-based shell script.
- Installer extension pattern now applies to Claude target by default: `install_agent_env.py` ships a maintained status line asset from `.agent_code/claude/` and merges a `statusLine` block into `~/.claude/settings.json` whenever the `claude` target is selected.
- A new `token_saver.py` script has been added to `.agent_code/claude/` to manage token usage in Claude Code via `PreCompact` and `PreToolUse` hooks, integrated directly into `install_agent_env.py`.
