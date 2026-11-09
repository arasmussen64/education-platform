# Wrong: two bugs fixed, but the failed count still greps for "500" anywhere.
cat > ~/bin/report <<'EOF'
#!/usr/bin/env bash
log="$1"
echo "requests: $(wc -l < "$log")"
echo "failed: $(grep -c 500 "$log")"
echo "top: $(awk '{print $2}' "$log" | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}')"
EOF
