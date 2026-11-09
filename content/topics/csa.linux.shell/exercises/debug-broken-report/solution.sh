# The fixed script. The three bugs were: grep -c 500 counted any line with
# "500" in it (a byte count, say) and missed 503; the top line took the
# status field ($3) instead of the path ($2); and uniq -c ran without a sort
# first, so it counted only neighbouring repeats.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
# Usage: report LOGFILE
# Prints three lines about a METHOD PATH STATUS BYTES log:
#   requests: N    how many requests
#   failed: N      how many had a status in the 500s
#   top: PATH      the most requested path
log="$1"
echo "requests: $(wc -l < "$log")"
echo "failed: $(awk '$3 ~ /^5[0-9][0-9]$/' "$log" | wc -l)"
echo "top: $(awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
EOF
