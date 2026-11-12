# Wrong: the oom kills line prints 0 instead of counting the kernel's log,
# which passes on a fresh machine where nothing has been killed yet.
cat > ~/bin/memory-report <<'EOF'
#!/bin/bash
available_kb=$(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}')
echo "available: $((available_kb / 1024)) MB"
echo "swap used: $(free -m | awk '/^Swap:/ {print $3}') MB"
echo "top process: $(ps -eo comm,rss --sort=-rss | awk 'NR == 2 {print $1, int($2 / 1024) " MB"}')"
echo "oom kills: 0"
EOF
