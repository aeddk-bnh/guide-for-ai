import argparse
import json
import os
import platform
import re
import shutil
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
CONTINUOUS_LEARNING_SKILL = "continuous-learning-v2"

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
    parser.add_argument(
        "--vscode-settings",
        help="Optional override for the VS Code user settings.json path used when patching chat.hookFilesLocations.",
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


def strip_jsonc_comments(text):
    result = []
    in_string = False
    escape = False
    in_single_line_comment = False
    in_multi_line_comment = False
    quote_char = ""
    index = 0

    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_single_line_comment:
            if char == "\n":
                in_single_line_comment = False
                result.append(char)
            index += 1
            continue

        if in_multi_line_comment:
            if char == "*" and next_char == "/":
                in_multi_line_comment = False
                index += 2
            else:
                index += 1
            continue

        if in_string:
            result.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                in_string = False
            index += 1
            continue

        if char in {'"', "'"}:
            in_string = True
            quote_char = char
            result.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            in_single_line_comment = True
            index += 2
            continue

        if char == "/" and next_char == "*":
            in_multi_line_comment = True
            index += 2
            continue

        result.append(char)
        index += 1

    return "".join(result)


def strip_trailing_commas(text):
    result = []
    in_string = False
    escape = False
    quote_char = ""
    index = 0

    while index < len(text):
        char = text[index]

        if in_string:
            result.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote_char:
                in_string = False
            index += 1
            continue

        if char in {'"', "'"}:
            in_string = True
            quote_char = char
            result.append(char)
            index += 1
            continue

        if char == ",":
            lookahead = index + 1
            while lookahead < len(text) and text[lookahead].isspace():
                lookahead += 1
            if lookahead < len(text) and text[lookahead] in "}]":
                index += 1
                continue

        result.append(char)
        index += 1

    return "".join(result)


def load_jsonc_file(path):
    raw = path.read_text(encoding="utf-8")
    cleaned = strip_trailing_commas(strip_jsonc_comments(raw))
    return json.loads(cleaned)


def resolve_vscode_settings_path(vscode_settings):
    if vscode_settings:
        return Path(vscode_settings).expanduser().resolve()

    if os.name == "nt":
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "Code" / "User" / "settings.json"

    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Code" / "User" / "settings.json"

    return Path.home() / ".config" / "Code" / "User" / "settings.json"


def build_targets(project_root, vscode_scope, vscode_home, vscode_settings):
    vscode_root = (
        project_root / ".github"
        if vscode_scope == "repo"
        else (
            Path(vscode_home).expanduser().resolve()
            if vscode_home
            else USER_HOME / ".copilot"
        )
    )
    vscode_settings_path = (
        None if vscode_scope == "repo" else resolve_vscode_settings_path(vscode_settings)
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
            "settings_path": vscode_settings_path,
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


def adapt_vscode_markdown(content, add_user_frontmatter=False):
    updated = content.replace(
        VSCODE_WORKFLOW_LINE,
        VSCODE_WORKFLOW_REPLACEMENT,
    )
    if add_user_frontmatter:
        updated = VSCODE_USER_INSTRUCTIONS_FRONTMATTER + updated
    return updated


def install_vscode_core(config):
    root = config["root"]
    scope = config["scope"]
    core_file = SOURCE_DIR / "core" / "GEMINI.md"
    dest_dir = root if scope == "repo" else root / "instructions"
    dest_dir.mkdir(parents=True, exist_ok=True)
    final_dest = (
        root / "copilot-instructions.md"
        if scope == "repo"
        else dest_dir / "guide-for-ai.instructions.md"
    )
    content = core_file.read_text(encoding="utf-8")
    content = adapt_vscode_markdown(content, add_user_frontmatter=(scope == "user"))
    final_dest.write_text(content, encoding="utf-8")
    print(f"  [v] Category 'core' installed to {dest_dir}")


def install_vscode_flat_skills(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src_file in sorted(source_dir.glob("*.md")):
        skill_dir = dest_dir / src_file.stem
        skill_dir.mkdir(parents=True, exist_ok=True)
        content = adapt_vscode_markdown(src_file.read_text(encoding="utf-8"))
        (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")


def install_vscode_skill_directories(source_dir, dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src_dir in sorted(source_dir.iterdir()):
        if not src_dir.is_dir():
            continue
        if not (src_dir / "SKILL.md").exists():
            continue

        target_dir = dest_dir / src_dir.name
        shutil.copytree(src_dir, target_dir, dirs_exist_ok=True)


def install_vscode_agents(dest_dir):
    dest_dir.mkdir(parents=True, exist_ok=True)

    for src_file in sorted((SOURCE_DIR / "subagents").glob("*.md")):
        content = src_file.read_text(encoding="utf-8")
        (dest_dir / f"{src_file.stem}.agent.md").write_text(content, encoding="utf-8")

    observer_source = (
        SOURCE_DIR / "skills" / CONTINUOUS_LEARNING_SKILL / "agents" / "observer.md"
    )
    if observer_source.exists():
        observer_dest = dest_dir / "continuous-learning-observer.agent.md"
        observer_dest.write_text(
            observer_source.read_text(encoding="utf-8"),
            encoding="utf-8",
        )


def build_vscode_continuous_learning_hook_entry(scope):
    if scope == "repo":
        skill_dir = ".github/skills/continuous-learning-v2"
        runtime_home = ".github/.continuous-learning-v2"
        windows_command = "python .github\\skills\\continuous-learning-v2\\hooks\\observe.py"
        posix_command = "python3 .github/skills/continuous-learning-v2/hooks/observe.py"
    else:
        skill_dir = "~/.copilot/skills/continuous-learning-v2"
        runtime_home = "~/.copilot/continuous-learning-v2"
        windows_command = (
            "python %USERPROFILE%\\.copilot\\skills\\continuous-learning-v2\\hooks\\observe.py"
        )
        posix_command = "python3 ~/.copilot/skills/continuous-learning-v2/hooks/observe.py"

    hook_entry = {
        "type": "command",
        "command": posix_command,
        "windows": windows_command,
        "linux": posix_command,
        "osx": posix_command,
        "env": {
            "CONTINUOUS_LEARNING_HOME": runtime_home,
            "CONTINUOUS_LEARNING_SKILL_DIR": skill_dir,
        },
    }

    return hook_entry


def resolve_vscode_hook_location(root, scope):
    if scope == "repo":
        return None

    actual_home = USER_HOME.resolve()
    root = root.resolve()

    try:
        relative = root.relative_to(actual_home)
        return f"~/{relative.as_posix()}/hooks"
    except ValueError:
        return str((root / "hooks").resolve())


def install_vscode_hooks(config):
    hook_entry = build_vscode_continuous_learning_hook_entry(config["scope"])

    if config["scope"] == "repo":
        hooks_dir = config["root"] / "hooks"
        hooks_dir.mkdir(parents=True, exist_ok=True)
        hook_path = hooks_dir / "continuous-learning-v2.json"
        hook_config = {
            "hooks": {
                "PreToolUse": [hook_entry],
                "PostToolUse": [hook_entry],
            }
        }
        hook_path.write_text(json.dumps(hook_config, indent=2) + "\n", encoding="utf-8")
        return hook_path

    hooks_dir = config["root"] / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_path = hooks_dir / "continuous-learning-v2.json"
    hook_config = {
        "hooks": {
            "PreToolUse": [hook_entry],
            "PostToolUse": [hook_entry],
        }
    }
    hook_path.write_text(json.dumps(hook_config, indent=2) + "\n", encoding="utf-8")

    settings_path = config["settings_path"]
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        settings = load_jsonc_file(settings_path)
    else:
        settings = {}

    hook_locations = settings.setdefault("chat.hookFilesLocations", {})
    hook_locations[resolve_vscode_hook_location(config["root"], config["scope"])] = True

    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return hook_path


def install_vscode_resources(config):
    root = config["root"]
    skills_dir = root / "skills"
    agents_dir = root / "agents"

    install_vscode_core(config)
    install_vscode_flat_skills(SOURCE_DIR / "workflows", skills_dir)
    install_vscode_flat_skills(SOURCE_DIR / "skills", skills_dir)
    install_vscode_skill_directories(SOURCE_DIR / "skills", skills_dir)
    print(f"  [v] Category 'workflows' installed to {skills_dir}")
    print(f"  [v] Category 'skills' installed to {skills_dir}")

    install_vscode_agents(agents_dir)
    print(f"  [v] Category 'subagents' installed to {agents_dir}")

    hook_output = install_vscode_hooks(config)
    print(f"  [v] Category 'hooks' installed to {hook_output.parent}")


def setup_resources(project_root, selected_targets, vscode_scope, vscode_home, vscode_settings):
    print("--- STARTING DEEP AGENT SETUP (RECURSIVE REWRITE) ---")
    
    if not SOURCE_DIR.exists():
        print(f"[!] Source {SOURCE_DIR} missing.")
        return

    targets = build_targets(project_root, vscode_scope, vscode_home, vscode_settings)

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

        if ide == "VSCode_Copilot":
            install_vscode_resources(config)
            continue
        
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
        args.vscode_settings,
    )
