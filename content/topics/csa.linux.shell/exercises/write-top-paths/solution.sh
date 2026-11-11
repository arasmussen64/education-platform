# The reference script. In the lab you write it with nano. Here it's written
# in one go: `cat > FILE <<'EOF'` puts every line up to the closing EOF into
# the file.
cat > ~/bin/top-paths <<'EOF'
#!/usr/bin/env bash
# Usage: top-paths LOGFILE N
# The N most requested paths in a METHOD PATH STATUS BYTES log, as "COUNT PATH".
log="$1"
n="$2"
awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n "$n" | awk '{print $1, $2}'
EOF
chmod +x ~/bin/top-paths
