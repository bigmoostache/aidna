#!/bin/bash
cd "$(dirname "$0")"

# Keep running CLI in a loop - tmux session stays alive
while true; do
    python3 cli/main.py
    exit_code=$?

    if [ $exit_code -eq 42 ]; then
        # Exit code 42 = restart requested, restart immediately
        continue
    elif [ $exit_code -eq 0 ]; then
        # Clean exit (user selected Exit), restart to keep tmux alive
        sleep 0.1
    else
        # On error, wait a bit before restarting
        sleep 0.5
    fi
done
