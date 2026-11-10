# Wrong: ss -ltn lists only the sockets that are listening, so no other
# state is ever counted and the leak is invisible.
cat > ~/bin/socket-report <<'EOF'
#!/bin/bash
ss -ltn | awk 'NR > 1 {print $1}' | sort | uniq -c | sort -rn
close_wait=$(ss -Hltn state close-wait | wc -l)
echo "close-wait: $close_wait"
if [ "$close_wait" -gt 20 ]; then
  exit 1
fi
EOF
chmod +x ~/bin/socket-report
