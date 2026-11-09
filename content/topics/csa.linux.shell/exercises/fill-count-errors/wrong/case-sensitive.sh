# Wrong: without -i, the lowercase "error" lines are missed.
cat > ~/bin/count-errors <<'EOF'
#!/usr/bin/env bash
log="$1"
grep -c ERROR "$log"
grep ERROR "$log" | head -n 1
EOF
chmod +x ~/bin/count-errors
