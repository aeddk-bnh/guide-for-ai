# Context

## Repo Purpose
- This repo is the source-of-truth for agent instructions, skills, workflows, and installer logic that ports them into multiple AI coding tools.

## Current Architecture
- `install.bat` and `install.sh` are the user entrypoints.
- `install_agent_env.py` is the unified installer and dedupe planner.
- `setup_agent_env.py` handles classic targets: Cursor, VS Code, Claude, Antigravity.
- `setup_codex_env.py` handles Codex-specific output.
- `setup_gemini_env.py` handles Gemini CLI-specific output.
- `.agent_code/` is the canonical content source.

## Working Decisions
- Installer output should preserve source content as much as possible; only format, path, and target-surface adaptations are allowed.
- Dedupe is artifact-aware and defaults to `auto` in the unified installer.

## Current Task
- Repository walkthrough requested on 2026-04-10 to explain installer architecture, target backends, and content flow.

## Latest Review
- Confirmed the repo is an installer/distribution project for shared AI-agent instructions rather than an application runtime.
- Main execution path is `install.bat` / `install.sh` -> `install_agent_env.py` -> target-specific backends.
- Canonical source content lives under `.agent_code/`; backend scripts mainly adapt that content into each tool's native format and destination paths.
- External Claude Code research on 2026-04-10: persistent session metadata display is officially supported via `statusLine`, not via lifecycle hooks.
- Configured a global Claude Code 3-line status line at `~/.claude/statusline.sh` and wired `~/.claude/settings.json` to use it with a 5-second refresh interval.
- Updated the global status line so line 1 appends git branch info, with a detached-HEAD fallback based on short commit SHA.
- Tuned status line appearance for a cleaner balanced look: shortened paths render as `.../parent/repo` and non-critical metadata uses fewer colors.
- Added an opt-in installer path for Claude Code status lines via `--claude-statusline`; smoke tests confirmed it installs `~/.claude/statusline.sh`, patches `~/.claude/settings.json`, and leaves default Claude installs unchanged.
- Hardened the optional Claude status line installer for portability by using an absolute configured script path, TMPDIR-aware caching, GNU/BSD `stat` fallback, and tolerant `chmod` handling.
- Claude target no longer requires `--claude-statusline`; status line is now installed automatically whenever the `claude` target is selected.
- Research on Claude Code Vietnamese input issues found no official hook-based fix for IME composition; hooks only run at lifecycle/submit boundaries, not per-keystroke, so terminal or IDE-level workarounds are more realistic than hook automation.
- Claude Code hook research highlights the most useful practical events as `PreToolUse`, `PostToolUse`, `PermissionRequest`, `SessionStart`, `Stop`, `Notification`, `ConfigChange`, and `CwdChanged`/`FileChanged`; hook scope should be chosen deliberately between global personal config and project-shared guardrails.
- Added a `token_saver.py` script in `.agent_code/claude/` that handles token optimization using Claude Code's `PreCompact` (to inject strict compaction rules) and `PreToolUse` (to block massive outputs like unrestricted `cat` or `ls -R`).
- Updated `install_agent_env.py` to seamlessly copy `token_saver.py` and register the `PreCompact` and `PreToolUse` hooks in `~/.claude/settings.json` upon Claude target installation.
