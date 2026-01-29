import os
import glob
import sys
import shutil

def fix_opencode_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    new_lines = []
    in_tools_block = False
    modified = False

    for line in lines:
        stripped = line.strip()
        
        # Check if entering tools block
        if stripped == 'tools:':
            in_tools_block = True
            new_lines.append(line)
            continue
        
        # Simple empty tools array fix
        if stripped == 'tools: []':
            new_lines.append("tools: {}\n")
            modified = True
            continue
            
        # Check if exiting tools block
        if in_tools_block:
            if stripped == '---' or (':' in stripped and not stripped.startswith('-')):
                in_tools_block = False
            elif stripped.startswith('- '):
                # Convert "- ToolName" to "  ToolName: true"
                indent = line[:line.find('-')]
                tool_name = stripped[2:].strip()
                new_line = f"{indent}{tool_name}: true\n"
                new_lines.append(new_line)
                modified = True
                continue

        new_lines.append(line)

    if modified:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print(f"Fixed formatting: {filepath}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

def fix_antigravity_skills(target_dir):
    print(f"Refactoring skills in {target_dir} for Antigravity...")
    files = glob.glob(os.path.join(target_dir, "*.md"))
    
    for filepath in files:
        filename = os.path.basename(filepath)
        if filename.lower() == "skill.md" or filename.lower() == "readme.md":
            continue
            
        skill_name = os.path.splitext(filename)[0]
        skill_dir = os.path.join(target_dir, skill_name)
        
        # Create directory for the skill
        if not os.path.exists(skill_dir):
            try:
                os.makedirs(skill_dir)
            except Exception as e:
                print(f"Error creating directory {skill_dir}: {e}")
                continue
        
        # Move and rename the file
        target_path = os.path.join(skill_dir, "SKILL.md")
        try:
            # We use copy then remove to be safe, or shutil.move
            shutil.move(filepath, target_path)
            print(f"Converted: {filename} -> {skill_name}/SKILL.md")
        except Exception as e:
            print(f"Error moving {filepath}: {e}")


def update_skill_paths(skill_dir, target_root_dir):
    """
    Updates paths in continuous-learning-v2 skill files based on the target environment.
    """
    print(f"Updating paths in {skill_dir} for target: {target_root_dir}")
    
    # Determine the correct path prefix based on the target directory
    target_path_normalized = target_root_dir.replace('\\', '/')
    
    # Map Claude Code paths to the target environment path
    claude_path_literal = "~/.claude"
    
    # Process SKILL.md and config.json if they exist
    for filename in ['SKILL.md', 'config.json']:
        filepath = os.path.join(skill_dir, filename)
        if os.path.isfile(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace literal Claude Code path with target path
                updated_content = content.replace(claude_path_literal, target_path_normalized)
                
                # For Antigravity, also replace forward slashes with backslashes in paths
                if "antigravity" in target_path_normalized.lower():
                    updated_content = updated_content.replace('/', '\\')
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print(f"Updated paths in: {filepath}")
                    
            except Exception as e:
                print(f"Error processing {filepath}: {e}")


def main():
    if len(sys.argv) < 3:
        print("Usage: manage_agent_config.py <mode> <directory>")
        print("Modes: fix-opencode, fix-antigravity-skills, fix-skill-paths")
        return

    mode = sys.argv[1]
    target_dir = sys.argv[2]
    
    if not os.path.isdir(target_dir):
        print(f"Error: Directory not found: {target_dir}")
        return

    if mode == "fix-opencode":
        print(f"Scanning for agent files in: {target_dir}")
        files = glob.glob(os.path.join(target_dir, "*.md"))
        print(f"Found {len(files)} files.")
        for filepath in files:
            fix_opencode_file(filepath)
            
    elif mode == "fix-antigravity-skills":
        fix_antigravity_skills(target_dir)
        
    elif mode == "fix-skill-paths":
        # For this mode, we expect a third argument which is the target root directory
        if len(sys.argv) < 4:
            print("Usage: manage_agent_config.py fix-skill-paths <skill_directory> <target_root_directory>")
            return
        skill_dir = sys.argv[2]
        target_root_dir = sys.argv[3]
        update_skill_paths(skill_dir, target_root_dir)
        
    else:
        print(f"Unknown mode: {mode}")

if __name__ == "__main__":
    main()
