# Agent Code & Workflows (Guide for AI)

This repository contains the standardized "Brain" for our AI Agents (Rules, Skills, Workflows).
It is designed to be **IDE-Agnostic** and now ships with one unified installer entrypoint per platform: `install.bat` for Windows and `install.sh` for Unix-like shells.

## ✨ Features
- **Unified Rule Source:** Edit rules in one place, sync everywhere.
- **Smart Path Patching:** Automatically rewrites absolute paths in markdown files to match the target IDE's environment (e.g., changes `C:\Users...` to `.cursor/workflows/...`).
- **Multi-IDE Support:** 
    - **Cursor:** Installs as `.cursorrules`.
    - **VS Code Copilot:** Installs globally by default into `~/.copilot/instructions`, `~/.copilot/skills`, `~/.copilot/agents`, and `~/.copilot/hooks`, and patches `chat.hookFilesLocations` in VS Code user settings, or into `.github/*` with repo scope.
    - **Codex:** Installs into `AGENTS.md`, `.agents/skills`, and `.codex/agents`.
    - **Gemini CLI:** Installs into `GEMINI.md` and `.gemini/commands` or `~/.gemini/commands`.
    - **Claude / OpenCode / Antigravity:** Installs skills and agents into their native paths, including `.opencode/...` project paths for OpenCode.

## 📂 Structure
- `core/GEMINI.md`: Core Rules, Principles, and Checklists.
- `skills/`: Specialized Agent Skills (e.g., `brainstorm`, `research`, `shadow_clone`).
- `workflows/`: Standard Operating Procedures (e.g., `general-workflow`, `testcase-workflow`).
- `subagents/`: Specialist personas that can be ported into Codex custom agents.
- `install.bat` / `install.sh`: Unified installer entrypoints.
- `install_agent_env.py`: The backend used by the installer entrypoints.
- `setup_agent_env.py`: Classic IDE installer backend.
- `setup_codex_env.py`: Codex installer backend.
- `setup_gemini_env.py`: Gemini CLI installer backend.

## 🚀 How to Use (Install)
1. **Clone this repo** to your local machine:
   ```bash
   git clone https://github.com/aeddk-bnh/guide-for-ai.git agent_code
   cd agent_code
   ```

2. **Run the unified installer:**
   ```bash
   ./install.sh
   ```
   On Windows use:
   ```bat
   install.bat
   ```

3. **What the unified installer does by default:**
   - installs classic assets for Cursor, VS Code Copilot, Claude, and Antigravity
   - installs full recursive skills and agents for Claude, OpenCode, and Antigravity
   - installs Codex assets into global user paths by default:
     - `~/.codex/AGENTS.md`
     - `~/.agents/skills`
     - `~/.codex/agents`
   - installs Gemini CLI assets into global user paths by default:
     - `~/.gemini/GEMINI.md`
     - `~/.gemini/commands`

4. **Optional flags:**
   ```bash
   ./install.sh --project-root /path/to/project
   ./install.sh --vscode-scope repo
   ./install.sh --vscode-settings /path/to/settings.json
   ./install.sh --opencode-scope repo
   ./install.sh --codex-scope repo
   ./install.sh --targets codex,claude
   ./install.sh --target codex
   ./install.sh --target gemini
   ./install.sh --target gemini --gemini-scope repo
   ```
   Use `--project-root` when this installer repository is separate from the project you want to configure.
   Windows:
   ```bat
   install.bat --project-root C:\path\to\project
   install.bat --vscode-scope repo
   install.bat --vscode-settings C:\path\to\settings.json
   install.bat --opencode-scope repo
   install.bat --codex-scope repo
   install.bat --targets codex,claude
   install.bat --target codex
   install.bat --target gemini
   install.bat --target gemini --gemini-scope repo
   ```

5. **Target selection with `--targets`:**
   - supported values: `cursor`, `vscode`, `claude`, `opencode`, `antigravity`, `codex`, `gemini`
   - use `all` or omit the flag to install everything
   - `--target codex` is accepted as a shortcut for a single target
   - `--target gemini` is accepted as a shortcut for a single target
   - example:
   ```bash
   ./install.sh --targets codex
   ./install.sh --targets gemini
   ./install.sh --targets cursor,vscode
   ./install.sh --targets claude,opencode,antigravity
   ```

6. **Codex global vs local:**
   - `--target codex` installs only Codex assets
   - default Codex install mode is global user scope
   - `--codex-scope repo` writes into the current repository:
     - `AGENTS.md`
     - `.agents/skills`
     - `.codex/agents`
   - `--codex-scope user` writes into your user profile instead:
     - `~/.codex/AGENTS.md`
     - `~/.agents/skills`
     - `~/.codex/agents`

7. **OpenCode global vs local:**
   - `--target opencode` installs only OpenCode assets
   - default OpenCode install mode is global user scope
   - `--opencode-scope repo` writes into the current repository:
     - `AGENTS.md`
     - `.opencode/skills/<skill>/SKILL.md`
     - `.opencode/agents/*.md`
   - `--opencode-scope user` writes into your user profile instead:
     - `~/.config/opencode/AGENTS.md`
     - `~/.config/opencode/skills/<skill>/SKILL.md`
     - `~/.config/opencode/agents/*.md`

8. **Gemini CLI global vs local:**
   - `--target gemini` installs only Gemini CLI assets
   - default Gemini CLI install mode is global user scope
   - `--gemini-scope repo` writes into the current repository:
     - `GEMINI.md`
     - `.gemini/commands`
   - `--gemini-scope user` writes into your user profile instead:
     - `~/.gemini/GEMINI.md`
     - `~/.gemini/commands`

9. **Reload your IDE / CLI session.** Your AI Agent is now fully updated with the latest protocols!

## Codex Notes
- Codex skills must live in a directory with `SKILL.md`, so the installer repackages the repository's single-file skills and workflows into Codex skill folders.
- Codex custom agents use `.toml` files, so the installer converts the markdown files in `subagents/` into `.codex/agents/*.toml`.
- `continuous-learning-v2` is still skipped by default for Codex because this repo does not yet provide a Codex-native hook/runtime port for it.

## OpenCode Notes
- OpenCode docs support both user-global config under `~/.config/opencode/...` and project-local config under `.opencode/...`.
- OpenCode instruction files live in `~/.config/opencode/AGENTS.md` for global scope and `AGENTS.md` at the project root for local scope.
- OpenCode skills use the folder layout `skills/<name>/SKILL.md`, so the installer repackages top-level markdown skills into that shape.
- OpenCode does not have a first-class `workflows/` directory, so workflow markdown files are repackaged as skills too.
- OpenCode agents are installed as markdown files in `agents/`.

## VS Code Copilot Notes
- Default VS Code install mode is global user scope.
- `--target vscode` writes to:
  - `~/.copilot/instructions/guide-for-ai.instructions.md`
  - `~/.copilot/skills/<name>/SKILL.md`
  - `~/.copilot/agents/*.agent.md`
  - `~/.copilot/hooks/continuous-learning-v2.json`
  - `chat.hookFilesLocations` patched in VS Code user settings
- `--target vscode --vscode-scope repo` writes to:
  - `.github/copilot-instructions.md`
  - `.github/skills/<name>/SKILL.md`
  - `.github/agents/*.agent.md`
  - `.github/hooks/continuous-learning-v2.json`
- This installer repackages both top-level `skills/*.md` and `workflows/*.md` into VS Code skills.
- This installer converts markdown files in `subagents/` into VS Code custom agent files with the `.agent.md` extension.
- For `continuous-learning-v2`, the installer also copies the full recursive skill directory and installs a VS Code hook file plus a `continuous-learning-observer` custom agent.
- If you use VS Code Insiders or a non-default profile settings file, pass `--vscode-settings` so the installer patches the right `settings.json`.

## Gemini CLI Notes
- Gemini CLI docs use `GEMINI.md` files for hierarchical context and `.gemini/commands/*.toml` for reusable custom commands.
- This installer maps `skills`, `workflows`, and `subagents` into namespaced Gemini CLI custom commands:
  - `skills/*` -> `/skills:*`
  - `workflows/*` -> `/workflows:*`
  - `subagents/*` -> `/agents:*`
- `continuous-learning-v2` is skipped because Gemini CLI docs expose custom commands and context files as the documented extension surface, not hook-based skills.
