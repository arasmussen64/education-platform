# Wrong: the mean is cut to a whole number instead of rounded. int() drops
# the fraction, so box-3's 17.7 becomes 17, not 18.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: gpu-report DIR" >&2
  exit 2
fi
awk -F, 'NR > 1 {
  sum += $2; n++
  if ($2 == 0) idle++
  if ($3 > peak) peak = $3
  total = $4
} END {
  print "average util: " int(sum / n) "%"
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
