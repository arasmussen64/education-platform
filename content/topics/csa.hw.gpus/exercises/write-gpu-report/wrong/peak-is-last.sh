# Wrong: the "peak" is the memory in use in the last second. Memory rises
# and falls with each batch, and the last second isn't the fullest one.
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
  peak = $3
  total = $4
} END {
  printf "average util: %.0f%%\n", sum / n
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
