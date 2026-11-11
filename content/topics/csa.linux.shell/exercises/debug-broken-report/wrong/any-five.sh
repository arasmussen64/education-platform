# Wrong: the failed count takes any status with a 5 in it, so the 405s in
# old-access.log are counted as failures.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
log="$1"
echo "requests: $(wc -l < "$log")"
echo "failed: $(awk '{print $3}' "$log" | grep -c 5)"
echo "top: $(awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
EOF
