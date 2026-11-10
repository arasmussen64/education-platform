# The finished script. In the lab you'd fill the four gaps with nano; here
# it's written in one go.
cat > ~/bin/memory-report <<'EOF'
#!/bin/bash
# Says how this machine's memory is doing, in four lines.
available_kb=$(grep '^MemAvailable:' /proc/meminfo | awk '{print $2}')
echo "available: $((available_kb / 1024)) MB"
echo "swap used: $(free -m | awk '/^Swap:/ {print $3}') MB"
echo "top process: $(ps -eo comm,rss --sort=-rss | awk 'NR == 2 {print $1, int($2 / 1024) " MB"}')"
echo "oom kills: $(journalctl -k --no-pager 2>/dev/null | grep -c 'Killed process')"
EOF
~/bin/memory-report
