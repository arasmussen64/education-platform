# One way to write it. cat > FILE <<'EOF' writes every line up to EOF into
# the file, and the quotes round 'EOF' keep the shell from changing anything
# in between. One pass of awk over the file does all three: NR > 1 skips the
# heading, the sum and the count make the mean, a counter takes the idle
# seconds, and the peak is the largest mem_used_mib seen so far.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
# Usage: gpu-report DIR
# Reads DIR/gpu.csv, a monitoring export of one GPU (one line a second:
# second,gpu_util_pct,mem_used_mib,mem_total_mib) and prints the minute's
# mean utilisation, the most memory in use against the card's total, and
# how many seconds the card was idle.
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
  printf "average util: %.0f%%\n", sum / n
  print "peak memory: " peak " of " total " MiB"
  print "idle seconds: " idle + 0
}' "$1/gpu.csv"
EOF
chmod +x ~/bin/gpu-report
for box in /srv/gpu/box-2 /srv/gpu/box-3; do echo "== $box"; ~/bin/gpu-report "$box"; done
