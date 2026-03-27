import argparse
import os
import re
from pathlib import Path

# --- CONFIGURATION ---
# Determine script location to find resources reliably
SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = SCRIPT_DIR / ".agent_code" # Resources are in .agent_code subfolder

# --- IDE TARGET PATHS ---
USER_HOME = Path(os.path.expanduser("~"))

# Define Replacements: (Old String, New String)
ORIGINAL_REF_PATH = r"c:\Users\ASUS\.gemini\antigravity\global_workflows\general-workflow.md"
VSCODE_WORKFLOW_LINE = (
    "**0.8 Workflow:** Strictly load and follow "
    "@`C:\\Users\\ASUS\\.gemini\\antigravity\\global_workflows\\general-workflow.md`."
)
VSCODE_WORKFLOW_REPLACEMENT = (
    "**0.8 Workflow:** Use the installed `general-workflow` skill whenever "
    "the standard sequential workflow is needed."
)
VSCODE_USER_INSTRUCTIONS_FRONTMATTER = "---\napplyTo: \"**\"\n---\n\n"

# The absolute path we want to get rid of
ABSOLUTE_PATH_PREFIX = r"c:\Users\ASUS\.gemini\antigravity"
ABSOLUTE_PATH_PREFIX_FWD = "c:/Users/ASUS/.gemini/antigravity"
ALL_CLASSIC_TARGETS = ("cursor", "vscode", "claude", "antigravity")
TARGET_NAME_MAP = {
    "Cursor": "cursor",
    "VSCode_Copilot": "vscode",
    "Claude": "claude",
    "Antigravity": "antigravity",
}

def parse_args():
    parser = argparse.ArgumentParser(
        description="Install classic IDE assets from guide-for-ai."
    )
    parser.add_argument(
        "--project-root",
        help=(
            "Target project root for Cursor and VS Code Copilot installs. Defaults "
            "to this repository root."
        ),
    )
    parser.add_argument(
        "--targets",
        default="all",
        help=(
            "Comma-separated classic targets. Supported values: "
            "cursor,vscode,claude,antigravity,all"
        ),
    )
    parser.add_argument(
        "--vscode-scope",
        choices=("repo", "user"),
        default="user",
        help="Scope to use when installing VS Code Copilot assets. Defaults to global user scope.",
    )
    parser.add_argument(
        "--vscode-home",
        help="Optional override for the VS Code Copilot user home path used by `--vscode-scope user`.",
    )
    return parser.parse_args()


def parse_targets(raw_targets):
    entries = [entry.strip().lower() for entry in raw_targets.split(",") if entry.strip()]
    if not entries:
        raise SystemExit("--targets requires at least one target")

    normalized = []
    for entry in entries:
        if entry == "all":
            return list(ALL_CLASSIC_TARGETS)
        if entry == "vscode-copilot":
            entry = "vscode"
        if entry not in ALL_CLASSIC_TARGETS:
            valid = ",".join((*ALL_CLASSIC_TARGETS, "all"))
            raise SystemExit(f"Unknown classic target '{entry}'. Supported values: {valid}")
        if entry not in normalized:
            normalized.append(entry)

    return normalized


def build_targets(project_root, vscode_scope, vscode_home):
    vscode_root = (
        project_root / ".github"
        if vscode_scope == "repo"
        else (
            Path(vscode_home).expanduser().resolve()
            if vscode_home
            else USER_HOME / ".copilot"
        )
    )

    return {
        "Antigravity": {
            "root": USER_HOME / ".gemini",
            "mapping_rules": {
                "core": "",
                "workflows": "antigravity/global_workflows",
                "skills": "antigravity/skills"
            },
            "path_replacement": None
        },
        "Cursor": {
            "root": project_root,
            "mapping_rules": {
                "core": ".",
                "workflows": ".cursor/workflows",
                "skills": ".cursor/skills"
            },
            "path_replacement": ".cursor"
        },
        "VSCode_Copilot": {
            "root": vscode_root,
            "mapping_rules": {
                "core": "." if vscode_scope == "repo" else "instructions",
                "workflows": "skills",
                "skills": "skills",
                "subagents": "agents",
            },
            "path_replacement": None,
            "scope": vscode_scope,
        },
        "Claude": {
            "root": USER_HOME / ".claude",
            "mapping_rules": {
                "core": ".",
                "workflows": "workflows",
                "skills": "skills"
            },
            "path_replacement": None
        }
    }


def setup_resources(project_root, selected_targets, vscode_scope, vscode_home):
    print("--- STARTING DEEP AGENT SETUP (RECURSIVE REWRITE) ---")
    
    if not SOURCE_DIR.exists():
        print(f"[!] Source {SOURCE_DIR} missing.")
        return

    targets = build_targets(project_root, vscode_scope, vscode_home)

    # 1. PREPARE RESOURCES (Scan all files)
    # We will copy category by category
    categories = ["core", "workflows", "skills", "subagents"]

    # 2. DISTRIBUTE
    for ide, config in targets.items():
        if TARGET_NAME_MAP[ide] not in selected_targets:
            continue
        print(f"\nProcessing {ide}...")
        root = config["root"]
        replacement_base = config["path_replacement"]
        
        for category in categories:
            src_category_dir = SOURCE_DIR / category
            if not src_category_dir.exists(): continue

            dest_rel_path = config["mapping_rules"].get(category)
            if dest_rel_path is None: continue

            dest_dir = root / dest_rel_path
            
            # --- COPY LOGIC ---
            # We iterate files in source category
            for src_file in src_category_dir.glob("*.md"):
                final_dest = dest_dir / src_file.name

                # Special Renaming for Core Rules
                if category == "core" and src_file.name == "GEMINI.md":
                    if ide == "Cursor": final_dest = root / ".cursorrules"
                    elif ide == "VSCode_Copilot":
                        if config["scope"] == "repo":
                            final_dest = root / "copilot-instructions.md"
                        else:
                            final_dest = dest_dir / "guide-for-ai.instructions.md"
                    elif ide == "Claude": final_dest = root / "CLAUDE.md"
                
                # Special Folder Logic for Skills (Antigravity only)
                if ide == "Antigravity" and category == "skills":
                    skill_folder = dest_dir / src_file.stem
                    skill_folder.mkdir(parents=True, exist_ok=True)
                    final_dest = skill_folder / "SKILL.md"
                elif ide == "VSCode_Copilot" and category in {"workflows", "skills"}:
                    skill_folder = dest_dir / src_file.stem
                    skill_folder.mkdir(parents=True, exist_ok=True)
                    final_dest = skill_folder / "SKILL.md"
                elif ide == "VSCode_Copilot" and category == "subagents":
                    final_dest = dest_dir / f"{src_file.stem}.agent.md"

                try:
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Read content
                    content = src_file.read_text(encoding='utf-8')
                    
                    # --- DEEP REWRITE LOGIC ---
                    if ide == "VSCode_Copilot":
                        content = content.replace(
                            VSCODE_WORKFLOW_LINE,
                            VSCODE_WORKFLOW_REPLACEMENT,
                        )
                        if category == "core" and config["scope"] == "user":
                            content = VSCODE_USER_INSTRUCTIONS_FRONTMATTER + content
                    elif replacement_base:
                        # Use Regex for Case-Insensitive Replacement
                        pattern = re.escape(ABSOLUTE_PATH_PREFIX)
                        
                        # Generic Replacement (Cursor, Antigravity likely doesn't hit this as it's None)
                        content = re.sub(pattern, replacement_base, content, flags=re.IGNORECASE)
                        
                        # Cleanup 'global_workflows' -> 'workflows' (Renaming/Flattening)
                        content = content.replace(r"\global_workflows", r"\workflows")
                        content = content.replace(r"/global_workflows", r"/workflows")
                        
                        pattern_fwd = re.escape(ABSOLUTE_PATH_PREFIX_FWD)
                        content = re.sub(pattern_fwd, replacement_base, content, flags=re.IGNORECASE)
                        
                    # Write content
                    final_dest.write_text(content, encoding='utf-8')
                    # print(f"  [v] Installed: {final_dest}") 
                except Exception as e:
                    print(f"  [x] Error processing {src_file.name}: {e}")

            print(f"  [v] Category '{category}' installed to {dest_dir}")

    print("\n--- SETUP COMPLETE ---")

if __name__ == "__main__":
    args = parse_args()
    selected_targets = parse_targets(args.targets)
    project_root = (
        Path(args.project_root).expanduser().resolve()
        if args.project_root
        else SCRIPT_DIR
    )
    setup_resources(
        project_root,
        selected_targets,
        args.vscode_scope,
        args.vscode_home,
    )
