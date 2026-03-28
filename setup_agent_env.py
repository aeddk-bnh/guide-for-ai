import argparse
from collections import defaultdict
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
VALID_CATEGORIES = {"core", "workflows", "skills", "subagents", "hooks"}
VSCODE_COMPAT_SURFACES = {"claude_md", "agents_md", "claude_skills", "agents_skills"}

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
    parser.add_argument(
        "--skip-map",
        help=(
            "Optional per-target categories to skip. Format: "
            "`target:category1,category2;target:category3` with categories from "
            "core,workflows,skills,subagents,hooks."
        ),
    )
    parser.add_argument(
        "--vscode-disable-compat",
        default="",
        help=(
            "Comma-separated VS Code compatibility surfaces to disable in settings. "
            "Supported values: claude_md,agents_md,claude_skills,agents_skills."
        ),
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


def parse_skip_map(raw_skip_map):
    skip_map = defaultdict(set)
    if not raw_skip_map:
        return skip_map

    for chunk in raw_skip_map.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise SystemExit(
                "--skip-map entries must use the format `target:category1,category2`"
            )
        target_name, raw_categories = chunk.split(":", 1)
        target = target_name.strip().lower()
        if target not in ALL_CLASSIC_TARGETS:
            valid_targets = ",".join(ALL_CLASSIC_TARGETS)
            raise SystemExit(
                f"Unknown target '{target}' in --skip-map. Supported values: "
                f"{valid_targets}"
            )

        categories = [entry.strip().lower() for entry in raw_categories.split(",") if entry.strip()]
        if not categories:
            raise SystemExit(f"--skip-map entry for '{target}' must list at least one category")

        unknown = [category for category in categories if category not in VALID_CATEGORIES]
        if unknown:
            valid_categories = ",".join(sorted(VALID_CATEGORIES))
            unknown_list = ",".join(unknown)
            raise SystemExit(
                f"Unknown categories in --skip-map for '{target}': {unknown_list}. "
                f"Supported values: {valid_categories}"
            )

        skip_map[target].update(categories)

    return skip_map


def parse_vscode_disable_compat(raw_value):
    if not raw_value:
        return set()

    disabled = {entry.strip().lower() for entry in raw_value.split(",") if entry.strip()}
    unknown = disabled - VSCODE_COMPAT_SURFACES
    if unknown:
        valid_values = ",".join(sorted(VSCODE_COMPAT_SURFACES))
        unknown_list = ",".join(sorted(unknown))
        raise SystemExit(
            f"Unknown compatibility surfaces in --vscode-disable-compat: "
            f"{unknown_list}. Supported values: {valid_values}"
        )

    return disabled


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


def resolve_vscode_settings_path(vscode_settings, project_root=None):
    if vscode_settings:
        return Path(vscode_settings).expanduser().resolve()

    if project_root is not None:
        return project_root / ".vscode" / "settings.json"

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
        resolve_vscode_settings_path(
            vscode_settings,
            project_root=project_root if vscode_scope == "repo" else None,
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
            "settings_path": vscode_settings_path,
            "disabled_compat": set(),
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


def ensure_vscode_skill_frontmatter(content, skill_name, source_label):
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n?", content, re.DOTALL)
    if match:
        frontmatter_lines = match.group(1).splitlines()
        body = content[match.end():].lstrip("\n")
    else:
        frontmatter_lines = []
        body = content.lstrip("\n")

    normalized_lines = []
    has_name = False
    has_description = False

    for line in frontmatter_lines:
        if re.match(r"^\s*name\s*:", line):
            normalized_lines.append(f"name: {skill_name}")
            has_name = True
            continue
        if re.match(r"^\s*description\s*:", line):
            normalized_lines.append(line)
            has_description = True
            continue
        if line.strip():
            normalized_lines.append(line)

    if not has_name:
        normalized_lines.insert(0, f"name: {skill_name}")

    if not has_description:
        raise SystemExit(
            f"VS Code skill source is missing required frontmatter field "
            f"'description': {source_label}"
        )

    return "---\n" + "\n".join(normalized_lines) + "\n---\n\n" + body


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
        content = ensure_vscode_skill_frontmatter(
            content,
            src_file.stem,
            str(src_file),
        )
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
        skill_file = target_dir / "SKILL.md"
        skill_content = adapt_vscode_markdown(skill_file.read_text(encoding="utf-8"))
        skill_content = ensure_vscode_skill_frontmatter(
            skill_content,
            src_dir.name,
            str(src_dir / "SKILL.md"),
        )
        skill_file.write_text(skill_content, encoding="utf-8")


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


def build_vscode_continuous_learning_hook_entry(root, scope):
    skill_path = (root / "skills" / CONTINUOUS_LEARNING_SKILL / "hooks" / "observe.py").resolve()
    runtime_home_path = (
        (root.parent / ".continuous-learning-v2").resolve()
        if scope == "repo"
        else (root / CONTINUOUS_LEARNING_SKILL).resolve()
    )

    windows_command = f'python "{skill_path}"'
    posix_command = f'python3 "{skill_path.as_posix()}"'

    hook_entry = {
        "type": "command",
        "command": posix_command,
        "windows": windows_command,
        "linux": posix_command,
        "osx": posix_command,
        "env": {
            "CONTINUOUS_LEARNING_HOME": str(runtime_home_path),
            "CONTINUOUS_LEARNING_SKILL_DIR": str(skill_path.parent.parent),
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


def update_vscode_location_setting(settings, key, location, enabled):
    locations = settings.setdefault(key, {})
    locations[location] = enabled


def patch_vscode_settings(config, install_native_hooks):
    disabled_compat = config.get("disabled_compat", set())
    settings_path = config["settings_path"]

    if not disabled_compat and not (install_native_hooks and config["scope"] == "user"):
        return settings_path

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    if settings_path.exists():
        settings = load_jsonc_file(settings_path)
    else:
        settings = {}

    if "claude_md" in disabled_compat:
        settings["chat.useClaudeMdFile"] = False

    if "agents_md" in disabled_compat:
        settings["chat.useAgentsMdFile"] = False

    if "claude_skills" in disabled_compat:
        update_vscode_location_setting(
            settings,
            "chat.agentSkillsLocations",
            ".claude/skills",
            False,
        )
        update_vscode_location_setting(
            settings,
            "chat.agentSkillsLocations",
            "~/.claude/skills",
            False,
        )

    if "agents_skills" in disabled_compat:
        update_vscode_location_setting(
            settings,
            "chat.agentSkillsLocations",
            ".agents/skills",
            False,
        )
        update_vscode_location_setting(
            settings,
            "chat.agentSkillsLocations",
            "~/.agents/skills",
            False,
        )

    if install_native_hooks and config["scope"] == "user":
        update_vscode_location_setting(
            settings,
            "chat.hookFilesLocations",
            resolve_vscode_hook_location(config["root"], config["scope"]),
            True,
        )

    settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
    return settings_path


def install_vscode_hooks(config):
    hook_entry = build_vscode_continuous_learning_hook_entry(
        config["root"],
        config["scope"],
    )

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

    return hook_path


def install_vscode_resources(config, skipped_categories):
    root = config["root"]
    skills_dir = root / "skills"
    agents_dir = root / "agents"

    if "core" not in skipped_categories:
        install_vscode_core(config)
    else:
        print("  [~] Category 'core' skipped")

    if "workflows" not in skipped_categories:
        install_vscode_flat_skills(SOURCE_DIR / "workflows", skills_dir)
        print(f"  [v] Category 'workflows' installed to {skills_dir}")
    else:
        print("  [~] Category 'workflows' skipped")

    if "skills" not in skipped_categories:
        install_vscode_flat_skills(SOURCE_DIR / "skills", skills_dir)
        install_vscode_skill_directories(SOURCE_DIR / "skills", skills_dir)
        print(f"  [v] Category 'skills' installed to {skills_dir}")
    else:
        print("  [~] Category 'skills' skipped")

    if "subagents" not in skipped_categories:
        install_vscode_agents(agents_dir)
        print(f"  [v] Category 'subagents' installed to {agents_dir}")
    else:
        print("  [~] Category 'subagents' skipped")

    if "hooks" not in skipped_categories:
        hook_output = install_vscode_hooks(config)
        print(f"  [v] Category 'hooks' installed to {hook_output.parent}")
    else:
        print("  [~] Category 'hooks' skipped")

    settings_path = patch_vscode_settings(
        config,
        install_native_hooks=("hooks" not in skipped_categories),
    )
    if config.get("disabled_compat") or ("hooks" not in skipped_categories and config["scope"] == "user"):
        print(f"  [v] VS Code settings updated at {settings_path}")


def setup_resources(
    project_root,
    selected_targets,
    vscode_scope,
    vscode_home,
    vscode_settings,
    skip_map,
    vscode_disabled_compat,
):
    print("--- STARTING DEEP AGENT SETUP (RECURSIVE REWRITE) ---")
    
    if not SOURCE_DIR.exists():
        print(f"[!] Source {SOURCE_DIR} missing.")
        return

    targets = build_targets(project_root, vscode_scope, vscode_home, vscode_settings)
    targets["VSCode_Copilot"]["disabled_compat"] = set(vscode_disabled_compat)

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
        skipped_categories = skip_map.get(TARGET_NAME_MAP[ide], set())

        if ide == "VSCode_Copilot":
            install_vscode_resources(config, skipped_categories)
            continue
        
        for category in categories:
            if category in skipped_categories:
                print(f"  [~] Category '{category}' skipped")
                continue
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
    skip_map = parse_skip_map(args.skip_map)
    vscode_disabled_compat = parse_vscode_disable_compat(args.vscode_disable_compat)
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
        skip_map,
        vscode_disabled_compat,
    )
