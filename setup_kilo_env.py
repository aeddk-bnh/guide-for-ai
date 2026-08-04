import argparse
import json
import os
import re
import shutil
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = SCRIPT_DIR / ".agent_code"
CORE_FILE = SOURCE_DIR / "core" / "GEMINI.md"
SKILLS_DIR = SOURCE_DIR / "skills"
WORKFLOWS_DIR = SOURCE_DIR / "workflows"
SUBAGENTS_DIR = SOURCE_DIR / "subagents"

SKIPPED_FOLDER_SKILLS = {
    "continuous-learning-v2": (
        "Skipped by default because it depends on Claude/OpenCode/Antigravity "
        "hooks and filesystem conventions that are not documented as Kilo-native "
        "skill behavior."
    ),
}
KNOWN_KILO_TOOLS = ("read", "write", "edit", "glob", "grep", "bash", "task", "webfetch")
MANAGED_SHARED_SKILL_SUFFIXES = (".agents/skills", ".claude/skills", ".opencode/skills")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install guide-for-ai assets into Kilo Code paths."
    )
    parser.add_argument(
        "--scope",
        choices=("repo", "user"),
        default="user",
        help=(
            "Install into project-local Kilo paths (`AGENTS.md`, `.kilo/skills`, "
            "`.kilo/commands`, `.kilo/agents`) or user-level paths "
            "(`~/.config/kilo`, `~/.kilo/skills`). Defaults to user-level paths."
        ),
    )
    parser.add_argument(
        "--repo-dir",
        help="Project root for `--scope repo`. Defaults to this repository root.",
    )
    parser.add_argument(
        "--kilo-config-home",
        help="Override the Kilo config directory used by `--scope user`.",
    )
    parser.add_argument(
        "--kilo-skills-home",
        help="Override the user-level Kilo skills home used by `--scope user`.",
    )
    parser.add_argument(
        "--shared-skill-paths",
        default="",
        help=(
            "Optional comma-separated extra skill roots to add to `skills.paths` "
            "in `kilo.jsonc`."
        ),
    )
    parser.add_argument(
        "--include-experimental",
        action="store_true",
        help="Also install folder skills that are skipped by default for Kilo.",
    )
    parser.add_argument(
        "--skip-instructions",
        action="store_true",
        help="Skip installing AGENTS.md.",
    )
    parser.add_argument(
        "--skip-skills",
        action="store_true",
        help="Skip installing Kilo skills.",
    )
    parser.add_argument(
        "--skip-commands",
        action="store_true",
        help="Skip installing Kilo slash commands.",
    )
    parser.add_argument(
        "--skip-agents",
        action="store_true",
        help="Skip installing Kilo custom agents.",
    )
    return parser.parse_args()


def parse_frontmatter(text):
    normalized = text.replace("\r\n", "\n")
    match = re.match(r"^---\n(.*?)\n---\n?(.*)$", normalized, flags=re.DOTALL)
    if not match:
        return {}, normalized

    metadata = {}
    current_list_key = None

    for raw_line in match.group(1).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        key_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", stripped)
        if key_match:
            key = key_match.group(1)
            value = key_match.group(2).strip()
            if value:
                metadata[key] = value.strip("\"'")
                current_list_key = None
            else:
                metadata[key] = []
                current_list_key = key
            continue

        if current_list_key and stripped.startswith("- "):
            metadata[current_list_key].append(stripped[2:].strip().strip("\"'"))

    return metadata, match.group(2)


def yaml_quote(value):
    escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def normalize_text(text):
    return text.replace("\r\n", "\n").strip() + "\n"


def sanitize_skill_name(name):
    normalized = str(name).strip().lower().replace("_", "-")
    normalized = re.sub(r"[^a-z0-9-]", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-") or "unnamed-skill"


def sanitize_agent_name(name):
    normalized = str(name).strip().lower().replace("_", "-")
    normalized = re.sub(r"[^a-z0-9-]", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-") or "unnamed-agent"


def require_description(metadata, source_path):
    description = str(metadata.get("description", "")).strip()
    if not description:
        raise SystemExit(
            f"Kilo install requires frontmatter field 'description' in source file: "
            f"{source_path}"
        )
    return description


def adapt_content_for_kilo(text):
    content = text.replace("\r\n", "\n")

    exact_line = (
        "**0.8 Workflow:** Strictly load and follow "
        "@`C:\\Users\\ASUS\\.gemini\\antigravity\\global_workflows\\general-workflow.md`."
    )
    content = content.replace(
        exact_line,
        "**0.8 Workflow:** Use the installed `/general-workflow` command whenever "
        "the standard sequential workflow is needed.",
    )

    replacements = {
        r"\bsearch_web\b": "websearch",
        r"\bread_url_content\b": "webfetch",
        r"\bbrowser_subagent\b": "browser_action",
        r"\buser_rules\b": "current AGENTS.md context",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    return normalize_text(content)


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


def ensure_list(value):
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def parse_csv_paths(raw_value):
    return [Path(entry).expanduser() for entry in raw_value.split(",") if entry.strip()]


def format_config_path(path, repo_root=None):
    resolved = path.expanduser().resolve()
    home = Path.home().resolve()

    if repo_root is not None:
        repo_root = repo_root.resolve()
        try:
            return resolved.relative_to(repo_root).as_posix()
        except ValueError:
            pass

    try:
        return "~/" + resolved.relative_to(home).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_config_entry(entry, repo_root=None):
    text = str(entry).strip()
    if not text:
        return None

    if text.startswith("~/"):
        return (Path.home() / text[2:]).resolve()
    if Path(text).is_absolute():
        return Path(text).expanduser().resolve()
    if repo_root is not None:
        return (repo_root / text).resolve()
    return None


def has_managed_shared_skill_suffix(value):
    normalized = str(value).replace("\\", "/").lower().rstrip("/")
    return any(normalized.endswith(suffix) for suffix in MANAGED_SHARED_SKILL_SUFFIXES)


def update_kilo_config(config_path, shared_skill_paths, scope, repo_root=None):
    config_path.parent.mkdir(parents=True, exist_ok=True)
    if config_path.exists():
        config = load_jsonc_file(config_path)
    else:
        config = {"$schema": "https://app.kilo.ai/config.json"}

    if not isinstance(config, dict):
        raise SystemExit(f"Kilo config file must contain an object: {config_path}")

    skills = config.get("skills")
    if skills is None:
        skills = {}
        config["skills"] = skills
    elif not isinstance(skills, dict):
        raise SystemExit(f"Kilo config 'skills' must be an object: {config_path}")

    existing_paths = ensure_list(skills.get("paths"))
    retained_paths = []

    for entry in existing_paths:
        if has_managed_shared_skill_suffix(entry):
            continue
        resolved = resolve_config_entry(entry, repo_root=repo_root if scope == "repo" else None)
        if resolved is not None and has_managed_shared_skill_suffix(resolved.as_posix()):
            continue
        retained_paths.append(entry)

    for shared_path in shared_skill_paths:
        formatted = format_config_path(
            shared_path,
            repo_root=repo_root if scope == "repo" else None,
        )
        if formatted not in retained_paths:
            retained_paths.append(formatted)

    if retained_paths:
        skills["paths"] = retained_paths
    else:
        skills.pop("paths", None)

    if not skills:
        config.pop("skills", None)

    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def write_text_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_folder_skill(src_dir, dest_dir):
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    for markdown_file in dest_dir.rglob("*.md"):
        markdown_file.write_text(
            adapt_content_for_kilo(markdown_file.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def render_skill_markdown(name, description, body):
    return "\n".join(
        [
            "---",
            f"name: {yaml_quote(name)}",
            f"description: {yaml_quote(description)}",
            "---",
            "",
            adapt_content_for_kilo(body).rstrip(),
            "",
        ]
    )


def install_markdown_skills(skill_root):
    installed = []

    for src_file in sorted(SKILLS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(src_file.read_text(encoding="utf-8"))
        skill_name = sanitize_skill_name(metadata.get("name", src_file.stem))
        description = require_description(metadata, src_file)
        destination = skill_root / skill_name / "SKILL.md"
        write_text_file(destination, render_skill_markdown(skill_name, description, body))
        installed.append(destination.parent)

    return installed


def install_folder_skills(skill_root, include_experimental):
    installed = []
    skipped = []

    for src_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        if src_dir.name in SKIPPED_FOLDER_SKILLS and not include_experimental:
            skipped.append((src_dir.name, SKIPPED_FOLDER_SKILLS[src_dir.name]))
            continue

        destination = skill_root / sanitize_skill_name(src_dir.name)
        copy_folder_skill(src_dir, destination)
        installed.append(destination)

    return installed, skipped


def install_workflow_commands(commands_root):
    installed = []

    for src_file in sorted(WORKFLOWS_DIR.glob("*.md")):
        destination = commands_root / f"{sanitize_skill_name(src_file.stem)}.md"
        write_text_file(
            destination,
            adapt_content_for_kilo(src_file.read_text(encoding="utf-8")),
        )
        installed.append(destination)

    return installed


def normalize_tool_name(tool_name):
    normalized = str(tool_name).strip().lower()
    mapping = {
        "read": "read",
        "write": "write",
        "edit": "edit",
        "glob": "glob",
        "grep": "grep",
        "bash": "bash",
        "task": "task",
        "webfetch": "webfetch",
    }
    return mapping.get(normalized)


def build_kilo_permissions(allowed_tools, disallowed_tools):
    normalized_allowed = [
        tool for tool in (normalize_tool_name(entry) for entry in allowed_tools) if tool
    ]
    normalized_disallowed = [
        tool for tool in (normalize_tool_name(entry) for entry in disallowed_tools) if tool
    ]

    permissions = {}
    if normalized_allowed:
        permissions = {tool: "deny" for tool in KNOWN_KILO_TOOLS}
        for tool in normalized_allowed:
            permissions[tool] = "allow"

    for tool in normalized_disallowed:
        permissions[tool] = "deny"

    return permissions


def render_agent_markdown(description, body, permissions):
    lines = [
        "---",
        f"description: {yaml_quote(description)}",
        "mode: subagent",
    ]

    if permissions:
        lines.append("permission:")
        for tool_name in KNOWN_KILO_TOOLS:
            if tool_name in permissions:
                lines.append(f"  {tool_name}: {permissions[tool_name]}")

    lines.extend(
        [
            "---",
            "",
            adapt_content_for_kilo(body).rstrip(),
            "",
        ]
    )
    return "\n".join(lines)


def install_agents(agents_root):
    installed = []

    for src_file in sorted(SUBAGENTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(src_file.read_text(encoding="utf-8"))
        agent_name = sanitize_agent_name(metadata.get("name", src_file.stem))
        description = require_description(metadata, src_file)
        allowed_tools = metadata.get("tools", [])
        disallowed_tools = metadata.get("disallowedTools", [])

        if not isinstance(allowed_tools, list):
            allowed_tools = [allowed_tools]
        if not isinstance(disallowed_tools, list):
            disallowed_tools = [disallowed_tools]

        permissions = build_kilo_permissions(allowed_tools, disallowed_tools)
        destination = agents_root / f"{agent_name}.md"
        write_text_file(
            destination,
            render_agent_markdown(description, body, permissions),
        )
        installed.append(destination)

    return installed


def resolve_targets(args):
    if args.scope == "repo":
        repo_root = Path(args.repo_dir).expanduser().resolve() if args.repo_dir else SCRIPT_DIR
        kilo_root = repo_root / ".kilo"
        return {
            "scope": "repo",
            "repo_root": repo_root,
            "instruction_file": repo_root / "AGENTS.md",
            "config_file": kilo_root / "kilo.jsonc",
            "skills_root": kilo_root / "skills",
            "commands_root": kilo_root / "commands",
            "agents_root": kilo_root / "agents",
        }

    config_home = (
        Path(args.kilo_config_home).expanduser().resolve()
        if args.kilo_config_home
        else (Path.home() / ".config" / "kilo").resolve()
    )
    skills_home = (
        Path(args.kilo_skills_home).expanduser().resolve()
        if args.kilo_skills_home
        else (Path.home() / ".kilo").resolve()
    )

    return {
        "scope": "user",
        "repo_root": None,
        "instruction_file": config_home / "AGENTS.md",
        "config_file": config_home / "kilo.jsonc",
        "skills_root": skills_home / "skills",
        "commands_root": config_home / "commands",
        "agents_root": config_home / "agents",
    }


def main():
    args = parse_args()

    if not SOURCE_DIR.exists():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    targets = resolve_targets(args)
    shared_skill_paths = [path.resolve() for path in parse_csv_paths(args.shared_skill_paths)]
    update_kilo_config(
        targets["config_file"],
        shared_skill_paths,
        targets["scope"],
        repo_root=targets["repo_root"],
    )

    installed_markdown_skills = []
    installed_folder_skills = []
    installed_commands = []
    installed_agents = []
    skipped_skills = []

    if not args.skip_instructions:
        write_text_file(
            targets["instruction_file"],
            adapt_content_for_kilo(CORE_FILE.read_text(encoding="utf-8")),
        )

    if not args.skip_skills:
        targets["skills_root"].mkdir(parents=True, exist_ok=True)
        installed_markdown_skills = install_markdown_skills(targets["skills_root"])
        installed_folder_skills, skipped_skills = install_folder_skills(
            targets["skills_root"],
            args.include_experimental,
        )
    else:
        for src_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
            if src_dir.name in SKIPPED_FOLDER_SKILLS:
                skipped_skills.append((src_dir.name, SKIPPED_FOLDER_SKILLS[src_dir.name]))

    if not args.skip_commands:
        targets["commands_root"].mkdir(parents=True, exist_ok=True)
        installed_commands = install_workflow_commands(targets["commands_root"])

    if not args.skip_agents:
        targets["agents_root"].mkdir(parents=True, exist_ok=True)
        installed_agents = install_agents(targets["agents_root"])

    print("--- KILO INSTALL COMPLETE ---")
    print(f"Scope: {targets['scope']}")
    print(f"Instruction file: {targets['instruction_file']}")
    print(f"Config file: {targets['config_file']}")
    print(f"Skills root: {targets['skills_root']}")
    print(f"Commands root: {targets['commands_root']}")
    print(f"Agents root: {targets['agents_root']}")
    print(
        "Installed assets: "
        f"{len(installed_markdown_skills)} markdown skills, "
        f"{len(installed_folder_skills)} folder skills, "
        f"{len(installed_commands)} commands, "
        f"{len(installed_agents)} agents"
    )

    if shared_skill_paths:
        print("Shared skill paths configured in kilo.jsonc:")
        for shared_path in shared_skill_paths:
            print(f"  - {shared_path}")

    if skipped_skills:
        print("Skipped assets:")
        for skill_name, reason in skipped_skills:
            print(f"  - {skill_name}: {reason}")


if __name__ == "__main__":
    main()
