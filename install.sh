#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(which python3)"
PLIST_PATH="$HOME/Library/LaunchAgents/com.user.ytremote.plist"

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: python3 not found in PATH."
    exit 1
fi

echo "Setting up macOS Startup LaunchAgent..."
echo "Project Dir: $PROJECT_DIR"
echo "Python Exec: $PYTHON_BIN"

mkdir -p "$HOME/Library/LaunchAgents"

cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.ytremote</string>
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_BIN</string>
        <string>$PROJECT_DIR/server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/ytremote.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/ytremote.err</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST_PATH" 2>/dev/null
launchctl load "$PLIST_PATH"

echo "Done! LaunchAgent installed and loaded successfully."
echo "Check server status logs with: cat /tmp/ytremote.log"