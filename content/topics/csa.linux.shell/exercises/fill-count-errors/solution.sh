# The completed script. In the lab you edit the file with nano. Here it's
# written in one go: `cat > FILE <<'EOF'` puts every line up to the closing
# EOF into the file.
cat > ~/bin/count-errors <<'EOF'
#!/usr/bin/env bash
# Usage: count-errors LOGFILE
# Prints how many lines mention an error, in any case, then the first such line.
log="$1"
grep -c -i error "$log"
grep -i error "$log" | head -n 1
EOF
chmod +x ~/bin/count-errors
