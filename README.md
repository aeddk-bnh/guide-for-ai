# Agent Code & Workflows (Guide for AI)

This repository contains the standardized "Brain" for our AI Agents (Rules, Skills, Workflows).
It is designed to be **IDE-Agnostic** (works with Cursor, VS Code Copilot, Antigravity).

## ✨ Features
- **Unified Rule Source:** Edit rules in one place, sync everywhere.
- **Smart Path Patching:** Automatically rewrites absolute paths in markdown files to match the target IDE's environment (e.g., changes `C:\Users...` to `.cursor/workflows/...`).
- **Multi-IDE Support:** 
    - **Cursor:** Installs as `.cursorrules`.
    - **VS Code Copilot:** Installs as `copilot-instructions.md`.
    - **Antigravity:** Installs to `~/.gemini/antigravity`.

## 📂 Structure
- `core/GEMINI.md`: Core Rules, Principles, and Checklists.
- `skills/`: Specialized Agent Skills (e.g., `brainstorm`, `research`, `shadow_clone`).
- `workflows/`: Standard Operating Procedures (e.g., `general-workflow`, `testcase-workflow`).
- `setup_agent_env.py`: The magic script that syncs everything.

## 🚀 How to Use (Install)
1. **Clone this repo** to your local machine:
   ```bash
   git clone https://github.com/aeddk-bnh/guide-for-ai.git agent_code
   cd agent_code
   ```

2. **Run the Setup Script:**
   ```bash
   python setup_agent_env.py
   ```
   *Note: Edit the `TARGETS` configuration in the script if you need to customize install paths.*

3. **Reload your IDE.** Your AI Agent is now fully updated with the latest protocols!
