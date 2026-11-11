# Wrong: the sums are right, and the script says how to use it when it is
# given nothing, but given two folders it quietly reports on the first and
# ignores the second, so whoever ran it thinks both were read.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
if [ -z "$1" ]; then
  echo "Usage: gpu-report DIR" >&2
  exit 2
fi
awk -F, 'NR > 1 {
  sum += $2; n++
  if ($2 == 0) idle++
  if ($3 > peak) peak = $3
  total = $4
} END {
  printf "average util: %.0f%%\n", sum / n
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
