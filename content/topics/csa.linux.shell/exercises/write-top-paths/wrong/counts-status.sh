# Wrong: counts the status field instead of the path.
cat > ~/bin/top-paths <<'EOF'
#!/usr/bin/env bash
log="$1"
n="$2"
awk '{print $3}' "$log" | sort | uniq -c | sort -rn | head -n "$n" | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
