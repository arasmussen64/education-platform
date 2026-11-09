# Wrong: always prints two lines, whatever N says.
cat > ~/bin/top-paths <<'EOF'
#!/usr/bin/env bash
log="$1"
awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n 2 | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
