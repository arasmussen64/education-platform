# Wrong: counts every line of the log, not the error lines.
cat > ~/bin/count-errors <<'EOF'
#!/usr/bin/env bash
log="$1"
wc -l < "$log"
grep -i error "$log" | head -n 1
EOF
chmod +x ~/bin/count-errors
