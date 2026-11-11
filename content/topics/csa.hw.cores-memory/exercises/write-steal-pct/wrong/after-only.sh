# Wrong: the second reading alone. Its numbers count from the moment the
# machine started, so this is the share stolen since boot (about 5% on every
# pair), not over the minute between the two readings.
mkdir -p ~/bin
cat > ~/bin/steal-pct <<'EOF'
#!/bin/bash
if [ $# -ne 2 ]; then
  echo "Usage: steal-pct BEFORE AFTER" >&2
  exit 2
fi
awk '{
  for (i = 2; i <= 9; i++) total += $i
  printf "%.1f\n", $9 * 100 / total
}' "$2"
EOF
chmod +x ~/bin/steal-pct
