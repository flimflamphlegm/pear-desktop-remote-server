#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(command -v python3 || true)"
PLIST_LABEL="com.user.ytremote"
PLIST_PATH="$HOME/Library/LaunchAgents/${PLIST_LABEL}.plist"

if [[ -z "$PYTHON_BIN" ]]; then
    echo "Error: python3 was not found in PATH." >&2
    exit 1
fi

mkdir -p "$HOME/Library/LaunchAgents"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>${PLIST_LABEL}</string>
    <key>ProgramArguments</key><array><string>${PYTHON_BIN}</string><string>${PROJECT_DIR}/main.py</string></array>
    <key>WorkingDirectory</key><string>${PROJECT_DIR}</string>
    <key>RunAtLoad</key><true/>
    <key>KeepAlive</key><true/>
    <key>StandardOutPath</key><string>${PROJECT_DIR}/ytremote.log</string>
    <key>StandardErrorPath</key><string>${PROJECT_DIR}/ytremote.err</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/${PLIST_LABEL}" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_PATH"

echo "Installed and loaded ${PLIST_LABEL}."
echo "Plist: ${PLIST_PATH}"
echo "Logs: ${PROJECT_DIR}/ytremote.log and ${PROJECT_DIR}/ytremote.err"
