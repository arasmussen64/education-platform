# Wrong: two bugs fixed, but the top line still uses the status field.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
log="$1"
echo "requests: $(wc -l < "$log")"
echo "failed: $(awk '$3 ~ /^5[0-9][0-9]$/' "$log" | wc -l)"
echo "top: $(awk '{print $3}' "$log" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
EOF
