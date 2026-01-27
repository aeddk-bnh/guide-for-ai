import os
import glob
import sys

def fix_file(filepath):
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
            
        # Check if exiting tools block (next top-level key or end of frontmatter)
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
            print(f"Fixed: {filepath}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")
    else:
        # print(f"Skipped (no changes needed): {filepath}")
        pass

def main():
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default fallback, though script should be called with arg
        target_dir = r"d:\pos\guide-for-ai\.agent_code\subagents"
    
    print(f"Scanning for agent files in: {target_dir}")
    
    if not os.path.isdir(target_dir):
        print(f"Error: Directory not found: {target_dir}")
        return

    files = glob.glob(os.path.join(target_dir, "*.md"))
    
    print(f"Found {len(files)} files.")
    
    for filepath in files:
        fix_file(filepath)

if __name__ == "__main__":
    main()
