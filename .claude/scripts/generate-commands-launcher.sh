#!/bin/bash

# Generate Commands Launcher Script
# This script detects the platform and runs the appropriate command generation script

SPEC_NAME="$1"

if [ -z "$SPEC_NAME" ]; then
    echo "Usage: $0 <spec-name>"
    echo "Example: $0 user-authentication"
    exit 1
fi

# Detect platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]]; then
    # Windows (Git Bash, Cygwin, or native Windows)
    echo "Detected Windows platform"
    node .claude/scripts/generate-commands.js "$SPEC_NAME"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS platform"
    node .claude/scripts/generate-commands.js "$SPEC_NAME"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    echo "Detected Linux platform"
    node .claude/scripts/generate-commands.js "$SPEC_NAME"
else
    # Unknown platform - try Node.js anyway
    echo "Unknown platform: $OSTYPE, attempting to use Node.js"
    node .claude/scripts/generate-commands.js "$SPEC_NAME"
fi

echo "Command generation complete!"
echo ""
echo "IMPORTANT: Restart Claude Code for the new commands to be visible."
echo "New commands will be available as:"
echo "  /${SPEC_NAME}-task-1"
echo "  /${SPEC_NAME}-task-2" 
echo "  etc."