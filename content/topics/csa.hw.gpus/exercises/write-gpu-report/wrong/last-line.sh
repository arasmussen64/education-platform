# Wrong: the utilisation is the last second's, not the minute's mean. One
# reading of a card that works in bursts says nothing about the minute, and
# on both boxes the last second happens to be an idle one.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: gpu-report DIR" >&2
  exit 2
fi
awk -F, 'NR > 1 {
  last = $2
  if ($2 == 0) idle++
  if ($3 > peak) peak = $3
  total = $4
} END {
  printf "average util: %.0f%%\n", last
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
