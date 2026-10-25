#!/bin/bash
# Will Breaker Dashboard Launcher & Browser Opener
set -e

UI_DIR="/home/comandante/will_breaker/ui/public/ui"
PORT=8080
URL="http://localhost:${PORT}/"

is_dashboard_running() {
    curl -s --connect-timeout 1 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${PORT}/index.html" 2>/dev/null | grep -q "200"
}

if ! is_dashboard_running; then
    # If port 8080 has an unresponsive process, clean it up
    if ss -tulpn 2>/dev/null | grep -q ":${PORT}\b"; then
        PID=$(ss -tulpn 2>/dev/null | grep ":${PORT}\b" | grep -o 'pid=[0-9]*' | cut -d= -f2 | head -n1 || true)
        if [ -n "$PID" ]; then
            kill "$PID" 2>/dev/null || true
            sleep 0.5
        fi
    fi

    cd "${UI_DIR}"
    nohup python3 -m http.server "${PORT}" > /tmp/will_breaker_http.log 2>&1 &
    
    for i in {1..15}; do
        if is_dashboard_running; then
            break
        fi
        sleep 0.2
    done
fi

if is_dashboard_running; then
    TARGET_URL="${URL}"
else
    TARGET_URL="file://${UI_DIR}/index.html"
fi

if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${TARGET_URL}" >/dev/null 2>&1 &
elif command -v firefox >/dev/null 2>&1; then
    firefox "${TARGET_URL}" >/dev/null 2>&1 &
elif command -v google-chrome >/dev/null 2>&1; then
    google-chrome "${TARGET_URL}" >/dev/null 2>&1 &
fi
