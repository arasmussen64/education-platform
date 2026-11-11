# Wrong: the failed count names the two statuses seen in access.log, 500 and
# 503, so the 502s in old-access.log are missed.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
log="$1"
echo "requests: $(wc -l < "$log")"
echo "failed: $(grep -c -e ' 500 ' -e ' 503 ' "$log")"
echo "top: $(awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
EOF
