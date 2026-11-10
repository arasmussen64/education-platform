# Wrong: the second column of the Swap line is the total, not what's used.
cat > ~/bin/memory-report <<'EOF'
#!/bin/bash
available_kb=$(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}')
echo "available: $((available_kb / 1024)) MB"
echo "swap used: $(free -m | awk '/^Swap:/ {print $2}') MB"
echo "top process: $(ps -eo comm,rss --sort=-rss | awk 'NR == 2 {print $1, int($2 / 1024) " MB"}')"
echo "oom kills: $(journalctl -k --no-pager 2>/dev/null | grep -c 'Killed process')"
EOF
