# Wrong: the fifth number, iowait, taken for steal. Steal is the eighth.
mkdir -p ~/bin
cat > ~/bin/steal-pct <<'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "Usage: steal-pct BEFORE AFTER" >&2
  exit 2
fi
paste "$1" "$2" | awk '{
  for (i = 2; i <= 9; i++) total += $(i + 11) - $i
  printf "%.1f\n", ($17 - $6) * 100 / total
}'
EOF
chmod +x ~/bin/steal-pct
