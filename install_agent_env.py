import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = SCRIPT_DIR / ".agent_code"
CORE_FILE = SOURCE_DIR / "core" / "GEMINI.md"
SKILLS_DIR = SOURCE_DIR / "skills"
WORKFLOWS_DIR = SOURCE_DIR / "workflows"
SUBAGENTS_DIR = SOURCE_DIR / "subagents"
MANAGE_CONFIG = SOURCE_DIR / "manage_agent_config.py"
SETUP_CLASSIC = SCRIPT_DIR / "setup_agent_env.py"
SETUP_CODEX = SCRIPT_DIR / "setup_codex_env.py"
SETUP_GEMINI = SCRIPT_DIR / "setup_gemini_env.py"

ALL_TARGETS = (
    "cursor",
    "vscode",
    "claude",
    "opencode",
    "antigravity",
    "codex",
    "gemini",
)
TARGET_ALIASES = {
    "vscode_copilot": "vscode",
    "vscode-copilot": "vscode",
    "gemini-cli": "gemini",
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Install guide-for-ai assets for supported IDE and CLI targets."
    )
    parser.add_argument(
        "--project-root",
        help=(
            "Target project root for project-scoped installs. Defaults to this "
            "repository root."
        ),
    )
    parser.add_argument(
        "--targets",
        "--target",
        dest="targets",
        default="all",
        help=(
            "Install target list. Use a single value with `--target` or a comma-"
            "separated list with `--targets`. Supported values: "
            "cursor,vscode,claude,opencode,antigravity,codex,gemini,all"
        ),
    )
    parser.add_argument(
        "--opencode-scope",
        choices=("repo", "user"),
        default="user",
        help="Scope to use when installing OpenCode assets. Defaults to global user scope.",
    )
    parser.add_argument(
        "--opencode-home",
        help="Optional override for the OpenCode config root used by `--opencode-scope user`.",
    )
    parser.add_argument(
        "--codex-scope",
        choices=("repo", "user"),
        default="user",
        help="Scope to use when installing Codex assets. Defaults to global user scope.",
    )
    parser.add_argument(
        "--codex-home",
        help="Optional override for the user-level Codex home path.",
    )
    parser.add_argument(
        "--skills-home",
        help="Optional override for the user-level Codex skills path.",
    )
    parser.add_argument(
        "--gemini-scope",
        choices=("repo", "user"),
        default="user",
        help="Scope to use when installing Gemini CLI assets. Defaults to global user scope.",
    )
    parser.add_argument(
        "--gemini-home",
        help="Optional override for the user-level Gemini CLI home path.",
    )
    parser.add_argument(
        "--include-experimental-codex",
        action="store_true",
        help="Install Codex skills that are skipped by default in setup_codex_env.py.",
    )
    return parser.parse_args()


def run_python(script_path, *extra_args):
    command = [sys.executable, str(script_path), *extra_args]
    subprocess.run(command, check=True, cwd=SCRIPT_DIR)


def parse_targets(raw_targets):
    entries = [entry.strip().lower() for entry in raw_targets.split(",") if entry.strip()]
    if not entries:
        raise SystemExit("--targets requires at least one target")

    normalized = []
    for entry in entries:
        normalized_entry = TARGET_ALIASES.get(entry, entry)
        if normalized_entry == "all":
            return list(ALL_TARGETS)
        if normalized_entry not in ALL_TARGETS:
            valid = ",".join((*ALL_TARGETS, "all"))
            raise SystemExit(f"Unknown target '{entry}'. Supported values: {valid}")
        if normalized_entry not in normalized:
            normalized.append(normalized_entry)

    return normalized


def copy_markdown_files(source_dir, target_dir):
    target_dir.mkdir(parents=True, exist_ok=True)
    for source_file in source_dir.glob("*.md"):
        shutil.copy2(source_file, target_dir / source_file.name)


def copy_directory_tree(source_dir, target_dir):
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)


def copy_markdown_files_as_skills(source_dir, target_dir):
    for source_file in sorted(source_dir.glob("*.md")):
        skill_dir = target_dir / source_file.stem
        skill_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, skill_dir / "SKILL.md")


def repackage_flat_markdown_skills(target_dir):
    for source_file in sorted(target_dir.glob("*.md")):
        if source_file.name.lower() in {"skill.md", "readme.md"}:
            continue

        skill_dir = target_dir / source_file.stem
        skill_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, skill_dir / "SKILL.md")
        source_file.unlink()


def run_manage_config(*extra_args):
    run_python(MANAGE_CONFIG, *extra_args)


def install_recursive_skills(
    target_dir,
    repackage_markdown_files=False,
    extra_markdown_skill_sources=(),
):
    copy_directory_tree(SKILLS_DIR, target_dir)

    for extra_source_dir in extra_markdown_skill_sources:
        copy_markdown_files_as_skills(extra_source_dir, target_dir)

    if repackage_markdown_files:
        repackage_flat_markdown_skills(target_dir)

    continuous_learning_dir = target_dir / "continuous-learning-v2"
    if continuous_learning_dir.exists():
        run_manage_config(
            "fix-skill-paths",
            str(continuous_learning_dir),
            str(target_dir.parent),
        )


def install_markdown_agents(target_dir, apply_opencode_format=False):
    copy_markdown_files(SUBAGENTS_DIR, target_dir)

    if apply_opencode_format:
        run_manage_config("fix-opencode", str(target_dir))


def default_project_root(args):
    if args.project_root:
        return Path(args.project_root).expanduser().resolve()
    return SCRIPT_DIR


def adapt_content_for_opencode(text):
    content = text.replace("\r\n", "\n")
    exact_line = (
        "**0.8 Workflow:** Strictly load and follow "
        "@`C:\\Users\\ASUS\\.gemini\\antigravity\\global_workflows\\general-workflow.md`."
    )
    replacement = (
        "**0.8 Workflow:** When the standard sequential workflow is needed, "
        "load the `general-workflow` skill from the available OpenCode skills."
    )
    return content.replace(exact_line, replacement)


def install_opencode_instructions(destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    content = CORE_FILE.read_text(encoding="utf-8")
    destination.write_text(adapt_content_for_opencode(content), encoding="utf-8")


def resolve_opencode_root(args, project_root, user_home):
    if args.opencode_scope == "repo":
        return project_root / ".opencode"
    if args.opencode_home:
        return Path(args.opencode_home).expanduser().resolve()
    return user_home / ".config" / "opencode"


def resolve_opencode_instruction_path(args, project_root, opencode_root):
    if args.opencode_scope == "repo":
        return project_root / "AGENTS.md"
    return opencode_root / "AGENTS.md"


def main():
    args = parse_args()
    project_root = default_project_root(args)
    user_home = Path(os.path.expanduser("~")).resolve()
    targets = parse_targets(args.targets)

    print("--- STARTING UNIFIED INSTALL ---")
    print(f"Project root: {project_root}")
    print(f"Targets: {', '.join(targets)}")

    classic_targets = [target for target in ("cursor", "vscode", "claude", "antigravity") if target in targets]
    if classic_targets:
        run_python(
            SETUP_CLASSIC,
            "--project-root",
            str(project_root),
            "--targets",
            ",".join(classic_targets),
        )

    claude_root = user_home / ".claude"
    opencode_root = resolve_opencode_root(args, project_root, user_home)
    antigravity_root = user_home / ".gemini" / "antigravity"

    if "claude" in targets:
        install_recursive_skills(claude_root / "skills")
        install_markdown_agents(claude_root / "agents")

    if "opencode" in targets:
        install_opencode_instructions(
            resolve_opencode_instruction_path(args, project_root, opencode_root)
        )
        install_recursive_skills(
            opencode_root / "skills",
            repackage_markdown_files=True,
            extra_markdown_skill_sources=(WORKFLOWS_DIR,),
        )
        install_markdown_agents(opencode_root / "agents", apply_opencode_format=True)

    if "antigravity" in targets:
        install_recursive_skills(
            antigravity_root / "skills",
            repackage_markdown_files=True,
        )
        install_markdown_agents(antigravity_root / "agents")

    if "codex" in targets:
        codex_args = ["--scope", args.codex_scope]
        if args.codex_scope == "repo":
            codex_args.extend(["--repo-dir", str(project_root)])
        if args.codex_home:
            codex_args.extend(["--codex-home", args.codex_home])
        if args.skills_home:
            codex_args.extend(["--skills-home", args.skills_home])
        if args.include_experimental_codex:
            codex_args.append("--include-experimental")

        run_python(SETUP_CODEX, *codex_args)

    if "gemini" in targets:
        gemini_args = ["--scope", args.gemini_scope]
        if args.gemini_scope == "repo":
            gemini_args.extend(["--repo-dir", str(project_root)])
        if args.gemini_home:
            gemini_args.extend(["--gemini-home", args.gemini_home])

        run_python(SETUP_GEMINI, *gemini_args)

    print("--- UNIFIED INSTALL COMPLETE ---")
    print(f"Installed targets: {', '.join(targets)}")
    if "opencode" in targets:
        print(f"Installed OpenCode assets with scope: {args.opencode_scope}")
    if "codex" in targets:
        print(f"Installed Codex assets with scope: {args.codex_scope}")
    if "gemini" in targets:
        print(f"Installed Gemini CLI assets with scope: {args.gemini_scope}")


if __name__ == "__main__":
    main()
