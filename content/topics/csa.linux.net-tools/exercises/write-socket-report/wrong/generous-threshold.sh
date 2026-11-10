# Wrong: the threshold is 50, so thirty leaked connections pass as healthy.
cat > ~/bin/socket-report <<'EOF'
#!/bin/bash
ss -tan | awk 'NR > 1 {print $1}' | sort | uniq -c | sort -rn
close_wait=$(ss -Htan state close-wait | wc -l)
echo "close-wait: $close_wait"
if [ "$close_wait" -gt 50 ]; then
  exit 1
fi
EOF
chmod +x ~/bin/socket-report
