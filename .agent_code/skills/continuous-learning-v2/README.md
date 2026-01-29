# Continuous Learning v2 - Multi-Platform Setup

This skill requires manual configuration of file paths depending on your target environment (Claude Code, OpenCode, or Antigravity).

## Setup Instructions

1. **Install the skill** using the installation scripts in the parent directory (`../`).
2. **Manually update paths** in the following files after installation:
   - `SKILL.md` (in the target environment's settings file)
   - `config.json` (in the skill's directory after installation)

### Path Mappings

| Environment | Root Path |
|-------------|-----------|
| Claude Code | `~/.claude/` |
| OpenCode | `~/.config/opencode/` |
| Antigravity | `%USERPROFILE%\.gemini\antigravity\` |

### Example

If installing for OpenCode, replace all instances of `~/.claude/` with `~/.config/opencode/`.

For Antigravity on Windows, replace `~/.claude/` with `%USERPROFILE%\.gemini\antigravity\` and forward slashes `/` with backslashes `\`.

### Configuration Files

- `config.template.json` is provided as a reference with comments indicating where paths need to be customized.