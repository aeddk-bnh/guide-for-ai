#!/bin/sh
echo "[INSTALL] Running unified environment install..."
echo

if command -v python >/dev/null 2>&1; then
    python install_agent_env.py "$@"
elif command -v python3 >/dev/null 2>&1; then
    python3 install_agent_env.py "$@"
else
    echo "Python is required to run install_agent_env.py"
    exit 1
fi
