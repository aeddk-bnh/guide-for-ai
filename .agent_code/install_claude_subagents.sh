#!/bin/bash
# Default target
TARGET="claude-agents"
# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -t|--target) TARGET="$2"; shift ;;
        -h|--help)
            echo "Usage: $0 [-t target]"
            echo "  -t target: Specify the installation target."
            echo "             (e.g., claude-agents, opencode-agents, antigravity-agents, claude-skills, opencode-skills, antigravity-skills)"
            exit 0
            ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done
# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# Determine source and target directories
case $TARGET in
    claude-agents)
        SOURCE_DIR="$SCRIPT_DIR/subagents"
        TARGET_DIR="$HOME/.claude/agents"
        PRODUCT_NAME="Claude Code"
        ITEM_TYPE="agents"
        ;;
    opencode-agents)
        SOURCE_DIR="$SCRIPT_DIR/subagents"
        TARGET_DIR="$HOME/.config/opencode/agents"
        PRODUCT_NAME="OpenCode"
        ITEM_TYPE="agents"
        ;;
    antigravity-agents)
        SOURCE_DIR="$SCRIPT_DIR/subagents"
        TARGET_DIR="$HOME/.gemini/antigravity/agents"
        PRODUCT_NAME="Antigravity"
        ITEM_TYPE="agents"
        ;;
    claude-skills)
        SOURCE_DIR="$SCRIPT_DIR/skills"
        TARGET_DIR="$HOME/.claude/skills"
        PRODUCT_NAME="Claude Code"
        ITEM_TYPE="skills"
        ;;
    opencode-skills)
        SOURCE_DIR="$SCRIPT_DIR/skills"
        TARGET_DIR="$HOME/.config/opencode/skills"
        PRODUCT_NAME="OpenCode"
        ITEM_TYPE="skills"
        ;;
    antigravity-skills)
        SOURCE_DIR="$SCRIPT_DIR/skills"
        TARGET_DIR="$HOME/.gemini/antigravity/skills"
        PRODUCT_NAME="Antigravity"
        ITEM_TYPE="skills"
        ;;
    *)
        echo "Error: Invalid target '$TARGET'."
        exit 1
        ;;
esac
# Installation process
echo "Starting $PRODUCT_NAME $ITEM_TYPE Installation for Unix/Linux..."
echo "Source directory: $SOURCE_DIR"
echo "Target directory: $TARGET_DIR"
echo ""
# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' not found."
    exit 1
fi
# Create target directory
mkdir -p "$TARGET_DIR"
# Copy files
if [ "$ITEM_TYPE" == "skills" ]; then
    cp -r "$SOURCE_DIR"/* "$TARGET_DIR"/
else
    # Handle overwrite for agents
    OVERWRITE_NEEDED=false
    for file in "$SOURCE_DIR"/*.md; do
        if [ -f "$TARGET_DIR/$(basename "$file")" ]; then
            OVERWRITE_NEEDED=true
            break
        fi
    done

    if [ "$OVERWRITE_NEEDED" = true ]; then
        read -p "Warning: Some $ITEM_TYPE files already exist. Overwrite? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Installation aborted."
            exit 1
        fi
    fi
    cp "$SOURCE_DIR"/*.md "$TARGET_DIR"/
fi
# Post-processing
if [[ "$TARGET" == "opencode-agents" ]]; then
    echo "Modifying agent configurations for OpenCode format..."
    if command -v python &> /dev/null; then
        python "$SCRIPT_DIR/manage_agent_config.py" fix-opencode "$TARGET_DIR"
    else
        echo "Warning: Python not found. Cannot convert agent configurations."
    fi
elif [[ "$TARGET" == "antigravity-skills" ]]; then
    echo "Restructuring skills for Antigravity format..."
    if command -v python &> /dev/null; then
        python "$SCRIPT_DIR/manage_agent_config.py" fix-antigravity-skills "$TARGET_DIR"
    else
        echo "Warning: Python not found. Cannot restructure skills."
    fi
fi
# Post-processing for continuous-learning-v2 skill
if [ -d "$TARGET_DIR/continuous-learning-v2" ]; then
    echo "Configuring continuous-learning-v2 skill..."
    if command -v python &> /dev/null; then
        python "$SCRIPT_DIR/manage_agent_config.py" fix-skill-paths "$TARGET_DIR/continuous-learning-v2" "$(dirname "$TARGET_DIR")"
    else
        echo "Warning: Python not found. Cannot configure the skill."
    fi
fi
echo "Installation complete!"
echo "You may need to restart your $PRODUCT_NAME session."
