import argparse
import json
import re
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib


SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = SCRIPT_DIR / ".agent_code"
CORE_FILE = SOURCE_DIR / "core" / "GEMINI.md"
SKILLS_DIR = SOURCE_DIR / "skills"
WORKFLOWS_DIR = SOURCE_DIR / "workflows"
SUBAGENTS_DIR = SOURCE_DIR / "subagents"

SKIPPED_FOLDER_SKILLS = {
    "continuous-learning-v2": (
        "Skipped because Gemini CLI custom commands are the closest documented "
        "extension point, and this skill depends on Claude/OpenCode/Antigravity "
        "hooks and filesystem conventions."
    ),
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install guide-for-ai assets into Gemini CLI paths."
    )
    parser.add_argument(
        "--scope",
        choices=("repo", "user"),
        default="user",
        help=(
            "Install into project-local Gemini CLI paths (`GEMINI.md`, `.gemini/commands`) "
            "or user-level paths (`~/.gemini/GEMINI.md`, `~/.gemini/commands`). "
            "Defaults to user-level paths."
        ),
    )
    parser.add_argument(
        "--repo-dir",
        help="Project root for `--scope repo`. Defaults to this repository root.",
    )
    parser.add_argument(
        "--gemini-home",
        help="Override the Gemini CLI home directory used by `--scope user`.",
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

def sanitize_name(name):
    normalized = re.sub(r"\s+", "-", name.strip())
    normalized = re.sub(r"[^A-Za-z0-9._-]", "-", normalized)
    normalized = re.sub(r"-{2,}", "-", normalized)
    return normalized.strip("-") or "unnamed"


def normalize_text(text):
    return text.replace("\r\n", "\n").strip() + "\n"


def adapt_content_for_gemini(text):
    content = text.replace("\r\n", "\n")

    exact_line = (
        "**0.8 Workflow:** Strictly load and follow "
        "@`C:\\Users\\ASUS\\.gemini\\antigravity\\global_workflows\\general-workflow.md`."
    )
    content = content.replace(
        exact_line,
        "**0.8 Workflow:** Use the `/workflows:general-workflow` custom command "
        "whenever the standard sequential workflow is needed.",
    )

    replacements = {
        r"\bsearch_web\b": "Gemini CLI's built-in web search",
        r"\bread_url_content\b": "Gemini CLI's built-in web fetch tools",
        r"\bbrowser_subagent\b": "a focused custom command or dedicated Gemini CLI session",
        r"\buser_rules\b": "loaded GEMINI.md context",
    }

    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)

    return normalize_text(content)


def render_skill_writer_prompt():
    return normalize_text(
        """# GEMINI CLI COMMAND WRITER WORKFLOW

## PURPOSE
Generate high-quality, executable Gemini CLI custom command files in `.gemini/commands/skills/<command_name>.toml`.

## 1. INPUT COLLECTION
- Define: Purpose, Inputs, Expected behavior, Environment, Constraints.
- **Rule:** If key input is missing -> STOP and ask the user for a concrete clarification.

## 2. OUTPUT LOCATION (RULE)
1. **Target:** `.gemini/commands/skills/<command_name>.toml`
2. **Action:** Create or update a single TOML command definition file.
3. **Naming:** Use a short kebab-case filename so the final command is easy to invoke as `/skills:<command_name>`.

## 3. FILE TEMPLATE (MANDATORY)
File MUST be valid TOML and include:

```toml
description = "One-line summary shown in /help"

prompt = '''
# Role
You are ...

## Goal
...

## Inputs
...

## Constraints
...

## Steps
1. ...
2. ...
3. ...
'''
```

## 4. GEMINI CLI RULES
- Keep the reusable instructions inside `prompt`.
- Put the short summary in `description`.
- If arguments are needed, explicitly design for Gemini CLI command arguments.
- Prefer project-relative paths inside the prompt.
- Do not emit Markdown frontmatter or `SKILL.md` scaffolding.

## 5. VALIDATION CHECKLIST
- [ ] TOML syntax valid?
- [ ] `description` concise and clear?
- [ ] `prompt` executable and specific?
- [ ] Command filename and namespace correct?
- [ ] No vague or marketing-heavy language?

**CORRECTION:** If validation fails -> Refactor -> Re-check.
"""
    )


def render_command_toml(description, prompt):
    adapted_prompt = adapt_content_for_gemini(prompt)
    return "\n".join(
        [
            f"description = {json.dumps(description, ensure_ascii=False)}",
            f"prompt = {json.dumps(adapted_prompt, ensure_ascii=False)}",
            "",
        ]
    )


def validate_toml(content, source_name):
    try:
        tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise SystemExit(f"Generated invalid TOML for {source_name}: {exc}") from exc


def write_text_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def install_context_file(destination):
    write_text_file(destination, adapt_content_for_gemini(CORE_FILE.read_text(encoding="utf-8")))


def install_commands_from_markdown(source_dir, commands_root, namespace):
    installed = []

    for source_file in sorted(source_dir.glob("*.md")):
        metadata, body = parse_frontmatter(source_file.read_text(encoding="utf-8"))
        command_name = sanitize_name(source_file.stem)
        description = metadata.get(
            "description",
            f"Reusable prompt for `{command_name}`.",
        )
        prompt_body = body
        if namespace == "workflows" and command_name == "skill-writer":
            description = "Create Gemini CLI custom commands in TOML format."
            prompt_body = render_skill_writer_prompt()
        destination = commands_root / namespace / f"{command_name}.toml"
        content = render_command_toml(description, prompt_body)
        validate_toml(content, source_file.name)
        write_text_file(destination, content)
        installed.append(destination)

    return installed


def resolve_targets(args):
    if args.scope == "repo":
        repo_root = Path(args.repo_dir).expanduser().resolve() if args.repo_dir else SCRIPT_DIR
        return {
            "scope": "repo",
            "context_file": repo_root / "GEMINI.md",
            "commands_root": repo_root / ".gemini" / "commands",
        }

    gemini_home = (
        Path(args.gemini_home).expanduser().resolve()
        if args.gemini_home
        else (Path.home() / ".gemini").resolve()
    )
    return {
        "scope": "user",
        "context_file": gemini_home / "GEMINI.md",
        "commands_root": gemini_home / "commands",
    }


def main():
    args = parse_args()

    if not SOURCE_DIR.exists():
        raise SystemExit(f"Source directory not found: {SOURCE_DIR}")

    targets = resolve_targets(args)
    install_context_file(targets["context_file"])

    installed_skill_commands = install_commands_from_markdown(
        SKILLS_DIR,
        targets["commands_root"],
        "skills",
    )
    installed_workflow_commands = install_commands_from_markdown(
        WORKFLOWS_DIR,
        targets["commands_root"],
        "workflows",
    )
    installed_agent_commands = install_commands_from_markdown(
        SUBAGENTS_DIR,
        targets["commands_root"],
        "agents",
    )

    skipped_skills = []
    for source_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        reason = SKIPPED_FOLDER_SKILLS.get(
            source_dir.name,
            "Skipped because only Markdown-based skills are translated into Gemini CLI custom commands.",
        )
        skipped_skills.append((source_dir.name, reason))

    print("--- GEMINI CLI INSTALL COMPLETE ---")
    print(f"Scope: {targets['scope']}")
    print(f"Context file: {targets['context_file']}")
    print(f"Commands root: {targets['commands_root']}")
    print(
        "Installed assets: "
        f"{len(installed_skill_commands)} skill commands, "
        f"{len(installed_workflow_commands)} workflow commands, "
        f"{len(installed_agent_commands)} agent commands"
    )

    if skipped_skills:
        print("Skipped assets:")
        for skill_name, reason in skipped_skills:
            print(f"  - {skill_name}: {reason}")


if __name__ == "__main__":
    main()
