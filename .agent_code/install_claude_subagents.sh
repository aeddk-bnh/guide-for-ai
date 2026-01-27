#!/bin/bash

# Default target is Claude Code Agents
TARGET="claude-agents"
SCRIPT_DIR=$(dirname "$0")

# Function to display usage
usage() {
    echo "Usage: $0 [-t target]"
    echo "  -t target : Install target (claude-agents, opencode-agents, claude-skills, opencode-skills). Default is claude-agents."
    exit 1
}

# Parse command line options
while getopts "t:h" opt; do
    case $opt in
        t)
            TARGET="$OPTARG"
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            ;;
    esac
done

# Determine source and target directories based on user choice
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
    *)
        echo "Error: Invalid target '$TARGET'. Please specify 'claude-agents', 'opencode-agents', 'claude-skills', or 'opencode-skills'."
        usage
        ;;
esac

echo "Starting $PRODUCT_NAME $ITEM_TYPE Installation..."
echo "Source directory: $SOURCE_DIR"
echo "Target directory: $TARGET_DIR"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' not found. Please ensure it exists."
    exit 1
fi

# Create target directory if it doesn't exist
if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating target directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create target directory '$TARGET_DIR'."
        exit 1
    fi
fi

# Copy items (agents or skills) from source to target
# For skills, we need to copy the entire subdirectory structure
if [ "$ITEM_TYPE" = "skills" ]; then
    echo "Copying skill directories from '$SOURCE_DIR' to '$TARGET_DIR'..."
    cp -rv "$SOURCE_DIR"/* "$TARGET_DIR"/
else
    # For agents, copy individual .md files
    echo "Copying agent files from '$SOURCE_DIR' to '$TARGET_DIR'..."
    cp -v "$SOURCE_DIR"/*.md "$TARGET_DIR"/
fi

if [ $? -ne 0 ]; then
    echo "Error: Failed to copy $ITEM_TYPE."
    exit 1
fi

echo "Installation complete!"
echo "You may need to restart your $PRODUCT_NAME session for the new $ITEM_TYPE to load."
