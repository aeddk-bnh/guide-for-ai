import os
import shutil
import re
from pathlib import Path

# --- CONFIGURATION ---
# Determine script location to find resources reliably
SCRIPT_DIR = Path(__file__).parent.resolve()
SOURCE_DIR = SCRIPT_DIR / ".agent_code" # Resources are in .agent_code subfolder

# Determine Project Root (Assumed to be one level up if script is in .agent_code)
# Or if script is meant to be run from root, we can handle that.
# Best bet: The repo root is wherever we want to install .vscode/.cursor
# We'll assume the user runs this script FROM the project root or the script knows it's in a subdir.
# Let's assume script is in `project/.agent_code/script.py` -> project root is `..`
PROJECT_ROOT = SCRIPT_DIR.parent 

# --- IDE TARGET PATHS ---
USER_HOME = Path(os.path.expanduser("~"))

# Define Replacements: (Old String, New String)
ORIGINAL_REF_PATH = r"c:\Users\ASUS\.gemini\antigravity\global_workflows\general-workflow.md"

# The absolute path we want to get rid of
ABSOLUTE_PATH_PREFIX = r"c:\Users\ASUS\.gemini\antigravity"
ABSOLUTE_PATH_PREFIX_FWD = "c:/Users/ASUS/.gemini/antigravity"

TARGETS = {
    "Antigravity": {
        "root": USER_HOME / ".gemini",
        "mapping_rules": {
            "core": "",  
            "workflows": "antigravity/global_workflows",
            "skills": "antigravity/skills" 
        },
        "path_replacement": None # No replacement needed, native env
    },
    "Cursor": {
        "root": PROJECT_ROOT,
        "mapping_rules": {
            "core": ".", 
            "workflows": ".cursor/workflows",
            "skills": ".cursor/skills"
        },
        # Replace absolute path with local .cursor path
        "path_replacement": ".cursor" 
    },
    "VSCode_Copilot": {
         "root": PROJECT_ROOT / ".vscode",
         "mapping_rules": {
             "core": ".", 
             "workflows": "workflows",
             "skills": "skills"
         },
         "path_replacement": "workflows",
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

def setup_resources():
    print("--- STARTING DEEP AGENT SETUP (RECURSIVE REWRITE) ---")
    
    if not SOURCE_DIR.exists():
        print(f"[!] Source {SOURCE_DIR} missing.")
        return

    # 1. PREPARE RESOURCES (Scan all files)
    # We will copy category by category
    categories = ["core", "workflows", "skills"]

    # 2. DISTRIBUTE
    for ide, config in TARGETS.items():
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
                    elif ide == "VSCode_Copilot": final_dest = root / "copilot-instructions.md"
                    elif ide == "Claude": final_dest = root / "CLAUDE.md"
                
                # Special Folder Logic for Skills (Antigravity only)
                if ide == "Antigravity" and category == "skills":
                    skill_folder = dest_dir / src_file.stem
                    skill_folder.mkdir(parents=True, exist_ok=True)
                    final_dest = skill_folder / "SKILL.md"

                try:
                    final_dest.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Read content
                    content = src_file.read_text(encoding='utf-8')
                    
                    # --- DEEP REWRITE LOGIC ---
                    if replacement_base:
                        # Use Regex for Case-Insensitive Replacement
                        pattern = re.escape(ABSOLUTE_PATH_PREFIX)
                        
                        # VSCODE SPECIAL CASE: The structure flattens 'global_workflows' -> 'workflows'
                        if ide == "VSCode_Copilot":
                             # 1. Try generic absolute replacement
                             content = re.sub(pattern, "workflows", content, flags=re.IGNORECASE)
                             
                             # 2. Cleanup leftover path segments that might linger
                             # If we replaced path with 'workflows', we might get 'workflows\global_workflows'
                             content = content.replace(r"workflows\global_workflows", "workflows")
                             content = content.replace(r"workflows/global_workflows", "workflows")
                             
                             # 3. Cleanup leading .vscode if present (e.g. if previous run added it)
                             content = content.replace(r".vscode\workflows", "workflows")
                             content = content.replace(r".vscode/workflows", "workflows")
                             
                        else:
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
    setup_resources()
