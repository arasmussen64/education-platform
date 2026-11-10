# Wrong: the verdict is printed but never becomes the exit status, so
# anything that runs this script thinks all is well.
cat > ~/bin/socket-report <<'EOF'
#!/bin/bash
ss -tan | awk 'NR > 1 {print $1}' | sort | uniq -c | sort -rn
close_wait=$(ss -Htan state close-wait | wc -l)
echo "close-wait: $close_wait"
if [ "$close_wait" -gt 20 ]; then
  echo "leak!"
fi
EOF
chmod +x ~/bin/socket-report
