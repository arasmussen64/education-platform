# Wrong: the header line of ss is counted as a state called "State".
cat > ~/bin/socket-report <<'EOF'
#!/bin/bash
ss -tan | awk '{print $1}' | sort | uniq -c | sort -rn
close_wait=$(ss -Htan state close-wait | wc -l)
echo "close-wait: $close_wait"
if [ "$close_wait" -gt 20 ]; then
  exit 1
fi
EOF
chmod +x ~/bin/socket-report
