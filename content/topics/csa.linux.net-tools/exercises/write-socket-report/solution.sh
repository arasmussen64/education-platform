# The reference script, written in one go; in the lab you'd use nano.
cat > ~/bin/socket-report <<'EOF'
#!/bin/bash
# Usage: socket-report
# Every TCP state on this machine with its count, most first, and a verdict
# on CLOSE-WAIT: many of those is a program not closing its connections.
ss -tan | awk 'NR > 1 {print $1}' | sort | uniq -c | sort -rn
close_wait=$(ss -Htan state close-wait | wc -l)
echo "close-wait: $close_wait"
if [ "$close_wait" -gt 20 ]; then
  exit 1
fi
EOF
chmod +x ~/bin/socket-report
~/bin/socket-report; echo "exit status: $?"
sudo ss -tanp state close-wait | head -3
from-office ~/bin/socket-report; echo "exit status in the office: $?"
