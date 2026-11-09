# Wrong: no sort before uniq -c, so only neighbouring repeats are counted.
cat > ~/bin/top-paths <<'EOF'
#!/usr/bin/env bash
log="$1"
n="$2"
awk '{print $2}' "$log" | uniq -c | sort -rn | head -n "$n" | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
