# The completed script. In the lab you'd edit the file with nano; here it's
# written in one go.
cat > ~/bin/count-errors <<'EOF'
#!/usr/bin/env bash
# Usage: count-errors LOGFILE
# Prints how many lines mention an error, in any case, then the first such line.
log="$1"
grep -c -i error "$log"
grep -i error "$log" | head -n 1
EOF
chmod +x ~/bin/count-errors
