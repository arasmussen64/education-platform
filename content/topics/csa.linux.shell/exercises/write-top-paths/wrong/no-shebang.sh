# Wrong: no shebang line. bash runs it anyway when bash starts it, but the
# file doesn't say which program should run it, as the prompt asks.
cat > ~/bin/top-paths <<'EOF'
log="$1"
n="$2"
awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n "$n" | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
