#!/bin/bash
# Will Breaker Dashboard Launcher

cd /home/comandante/will_breaker/ui/public/ui
python3 -m http.server 8080 &
echo "Will Breaker Dashboard started at http://localhost:8080"
echo "Open http://localhost:8080 in your browser"
echo "Press Ctrl+C to stop the server"
wait
