import argparse
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
        "Skipped by default because it is written for Claude/OpenCode/Antigravity "
        "hooks and paths, which do not have a documented Codex equivalent."
    ),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install guide-for-ai assets into Codex-native paths."
    )
    parser.add_argument(
        "--scope",
        choices=("repo", "user"),
        default="user",
        help=(
            "Install into project-local Codex paths (`AGENTS.md`, `.agents/skills`, "
            "`.codex/agents`) or user-level paths (`~/.codex`, `~/.agents/skills`). "
            "Defaults to user-level paths."
        ),
    )
    parser.add_argument(
        "--repo-dir",
        help=(
            "Project root for `--scope repo`. Defaults to this repository root."
        ),
    )
    parser.add_argument(
        "--codex-home",
        help="Override the Codex home directory used by `--scope user`.",
    )
    parser.add_argument(
        "--skills-home",
        help="Override the user skills directory used by `--scope user`.",
    )
    parser.add_argument(
        "--include-experimental",
        action="store_true",
        help="Also install folder skills that are marked as incompatible with Codex.",
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
        line = raw_line.rstrip()
        stripped = line.strip()
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
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def toml_quote(value):
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def sanitize_name(name):
    normalized = re.sub(r"\s+", "-", name.strip())
    normalized = re.sub(r"[^A-Za-z0-9._-]", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-") or "unnamed"


def normalize_text(text):
    return text.replace("\r\n", "\n").strip() + "\n"


def adapt_content_for_codex(text):
    content = text.replace("\r\n", "\n")

    exact_line = (
        "**0.8 Workflow:** Strictly load and follow "
        "@`C:\\Users\\ASUS\\.gemini\\antigravity\\global_workflows\\general-workflow.md`."
    )
    content = content.replace(
        exact_line,
        "**0.8 Workflow:** Use the installed `general-workflow` skill whenever the "
        "standard sequential workflow is needed.",
    )

    replacements = {
        r"\bsearch_web\b": "web search",
        r"\bread_url_content\b": "documentation or web-page fetch tools",
        r"\bbrowser_subagent\b": "a dedicated subagent with browser/computer-use tools",
        r"\buser_rules\b": "the active instruction stack",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    return normalize_text(content)


def workflow_description(stem, source_description):
    if source_description:
        return (
            f"Use when the task specifically needs the repository's `{stem}` workflow. "
            f"{source_description.rstrip('.')}."
        )
    return (
        f"Use when the task specifically needs the repository's `{stem}` workflow and "
        "its step-by-step operating procedure."
    )


def render_skill_markdown(name, description, body):
    parts = [
        "---",
        f"name: {yaml_quote(name)}",
        f"description: {yaml_quote(description)}",
        "---",
        "",
    ]

    parts.append(adapt_content_for_codex(body).rstrip())
    parts.append("")
    return "\n".join(parts)


def render_agents_md(body):
    return adapt_content_for_codex(body)


def detect_sandbox_mode(allowed_tools):
    normalized = {tool.lower() for tool in allowed_tools}
    if {"write", "edit"} & normalized:
        return "workspace-write"
    return "read-only"


def render_agent_toml(name, description, body, allowed_tools, disallowed_tools):
    sandbox_mode = detect_sandbox_mode(allowed_tools)
    developer_instructions = adapt_content_for_codex(body).rstrip()

    return "\n".join(
        [
            f"name = {toml_quote(name)}",
            f"description = {toml_quote(description)}",
            f"sandbox_mode = {toml_quote(sandbox_mode)}",
            "developer_instructions = '''",
            developer_instructions,
            "'''",
            "",
        ]
    )


def write_text_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def copy_folder_skill(src_dir, dest_dir):
    shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    for markdown_file in dest_dir.rglob("*.md"):
        markdown_file.write_text(
            adapt_content_for_codex(markdown_file.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def install_markdown_skills(skill_root):
    installed = []

    for src_file in sorted(SKILLS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(src_file.read_text(encoding="utf-8"))
        skill_name = sanitize_name(metadata.get("name", src_file.stem))
        description = metadata.get(
            "description",
            f"Use when the task specifically matches the `{skill_name}` skill.",
        )

        dest_dir = skill_root / skill_name
        write_text_file(
            dest_dir / "SKILL.md",
            render_skill_markdown(
                skill_name,
                description,
                body,
            ),
        )
        installed.append(dest_dir)

    return installed


def install_folder_skills(skill_root, include_experimental):
    installed = []
    skipped = []

    for src_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        if src_dir.name in SKIPPED_FOLDER_SKILLS and not include_experimental:
            skipped.append((src_dir.name, SKIPPED_FOLDER_SKILLS[src_dir.name]))
            continue

        dest_dir = skill_root / src_dir.name
        copy_folder_skill(src_dir, dest_dir)
        installed.append(dest_dir)

    return installed, skipped


def install_workflows_as_skills(skill_root):
    installed = []

    for src_file in sorted(WORKFLOWS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(src_file.read_text(encoding="utf-8"))
        skill_name = sanitize_name(src_file.stem)
        description = workflow_description(skill_name, metadata.get("description", ""))
        dest_dir = skill_root / skill_name

        write_text_file(
            dest_dir / "SKILL.md",
            render_skill_markdown(
                skill_name,
                description,
                body,
            ),
        )
        installed.append(dest_dir)

    return installed


def install_subagents(agent_root):
    installed = []

    for src_file in sorted(SUBAGENTS_DIR.glob("*.md")):
        metadata, body = parse_frontmatter(src_file.read_text(encoding="utf-8"))
        agent_name = sanitize_name(src_file.stem.replace("-", "_"))
        description = metadata.get(
            "description",
            f"Custom agent for `{agent_name}`.",
        )
        allowed_tools = metadata.get("tools", [])
        disallowed_tools = metadata.get("disallowedTools", [])

        if not isinstance(allowed_tools, list):
            allowed_tools = [allowed_tools]
        if not isinstance(disallowed_tools, list):
            disallowed_tools = [disallowed_tools]

        write_text_file(
            agent_root / f"{agent_name}.toml",
            render_agent_toml(
                agent_name,
                description,
                body,
                allowed_tools,
                disallowed_tools,
            ),
        )
        installed.append(agent_root / f"{agent_name}.toml")

    return installed


def resolve_targets(args):
    if args.scope == "repo":
        repo_root = Path(args.repo_dir).expanduser().resolve() if args.repo_dir else SCRIPT_DIR
        return {
            "scope": "repo",
            "agents_md": repo_root / "AGENTS.md",
            "skills_root": repo_root / ".agents" / "skills",
            "agents_root": repo_root / ".codex" / "agents",
            "root_label": repo_root,
        }

    codex_home = (
        Path(args.codex_home).expanduser().resolve()
        if args.codex_home
        else Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser().resolve()
    )
    skills_home = (
        Path(args.skills_home).expanduser().resolve()
        if args.skills_home
        else (Path.home() / ".agents" / "skills").resolve()
    )

    return {
        "scope": "user",
        "agents_md": codex_home / "AGENTS.md",
        "skills_root": skills_home,
        "agents_root": codex_home / "agents",
        "root_label": codex_home,
    }


def main():
    args = parse_args()

    if not SOURCE_DIR.exists():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    targets = resolve_targets(args)
    targets["skills_root"].mkdir(parents=True, exist_ok=True)
    targets["agents_root"].mkdir(parents=True, exist_ok=True)

    core_body = CORE_FILE.read_text(encoding="utf-8")
    write_text_file(
        targets["agents_md"],
        render_agents_md(core_body),
    )

    installed_markdown_skills = install_markdown_skills(targets["skills_root"])
    installed_folder_skills, skipped_skills = install_folder_skills(
        targets["skills_root"],
        include_experimental=args.include_experimental,
    )
    installed_workflows = install_workflows_as_skills(targets["skills_root"])
    installed_agents = install_subagents(targets["agents_root"])

    print("--- CODEX INSTALL COMPLETE ---")
    print(f"Scope: {targets['scope']}")
    print(f"Instruction file: {targets['agents_md']}")
    print(f"Skills root: {targets['skills_root']}")
    print(f"Agents root: {targets['agents_root']}")
    print(
        "Installed assets: "
        f"{len(installed_markdown_skills)} markdown skills, "
        f"{len(installed_folder_skills)} folder skills, "
        f"{len(installed_workflows)} workflow skills, "
        f"{len(installed_agents)} custom agents"
    )

    if skipped_skills:
        print("Skipped assets:")
        for skill_name, reason in skipped_skills:
            print(f"  - {skill_name}: {reason}")


if __name__ == "__main__":
    main()
