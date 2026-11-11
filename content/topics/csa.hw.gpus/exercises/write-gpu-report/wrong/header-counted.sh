# Wrong: the heading line is counted as a second. Read as a number,
# "gpu_util_pct" is 0, so the mean is a little low and there is one idle
# second too many.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
if [ $# -ne 1 ]; then
  echo "Usage: gpu-report DIR" >&2
  exit 2
fi
awk -F, '{
  sum += $2; n++
  if ($2 + 0 == 0) idle++
  if ($3 + 0 > peak) peak = $3
  total = $4
} END {
  printf "average util: %.0f%%\n", sum / n
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
