# The reference script, written in one go; in the lab you'd use nano.
cat > ~/bin/top-paths <<'EOF'
#!/usr/bin/env bash
# Usage: top-paths LOGFILE N
# The N most requested paths in a METHOD PATH STATUS BYTES log, as "COUNT PATH".
log="$1"
n="$2"
awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n "$n" | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
