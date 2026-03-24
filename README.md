# Agent Code & Workflows (Guide for AI)

This repository contains the standardized "Brain" for our AI Agents (Rules, Skills, Workflows).
It is designed to be **IDE-Agnostic** and now ships with one unified installer entrypoint per platform: `install.bat` for Windows and `install.sh` for Unix-like shells.

## ✨ Features
- **Unified Rule Source:** Edit rules in one place, sync everywhere.
- **Smart Path Patching:** Automatically rewrites absolute paths in markdown files to match the target IDE's environment (e.g., changes `C:\Users...` to `.cursor/workflows/...`).
- **Multi-IDE Support:** 
    - **Cursor:** Installs as `.cursorrules`.
    - **VS Code Copilot:** Installs as `copilot-instructions.md`.
    - **Codex:** Installs into `AGENTS.md`, `.agents/skills`, and `.codex/agents`.
    - **Claude / OpenCode / Antigravity:** Installs skills and agents into their native home-directory paths.

## 📂 Structure
- `core/GEMINI.md`: Core Rules, Principles, and Checklists.
- `skills/`: Specialized Agent Skills (e.g., `brainstorm`, `research`, `shadow_clone`).
- `workflows/`: Standard Operating Procedures (e.g., `general-workflow`, `testcase-workflow`).
- `subagents/`: Specialist personas that can be ported into Codex custom agents.
- `install.bat` / `install.sh`: Unified installer entrypoints.
- `install_agent_env.py`: The backend used by the installer entrypoints.
- `setup_agent_env.py`: Classic IDE installer backend.
- `setup_codex_env.py`: Codex installer backend.

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

4. **Optional flags:**
   ```bash
   ./install.sh --project-root /path/to/project
   ./install.sh --codex-scope repo
   ./install.sh --targets codex,claude
   ./install.sh --target codex
   ```
   Use `--project-root` when this installer repository is separate from the project you want to configure.
   Windows:
   ```bat
   install.bat --project-root C:\path\to\project
   install.bat --codex-scope repo
   install.bat --targets codex,claude
   install.bat --target codex
   ```

5. **Target selection with `--targets`:**
   - supported values: `cursor`, `vscode`, `claude`, `opencode`, `antigravity`, `codex`
   - use `all` or omit the flag to install everything
   - `--target codex` is accepted as a shortcut for a single target
   - example:
   ```bash
   ./install.sh --targets codex
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

7. **Reload your IDE / Codex session.** Your AI Agent is now fully updated with the latest protocols!

## Codex Notes
- Codex skills must live in a directory with `SKILL.md`, so the installer repackages the repository's single-file skills and workflows into Codex skill folders.
- Codex custom agents use `.toml` files, so the installer converts the markdown files in `subagents/` into `.codex/agents/*.toml`.
- `continuous-learning-v2` is skipped by default because it is currently written around Claude/OpenCode/Antigravity-specific hooks and paths.
