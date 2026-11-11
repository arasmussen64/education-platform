# Wrong: the sums are right, but given no folder the script doesn't say how
# to use it: awk complains that it can't open a file called /gpu.csv, which
# tells whoever ran it nothing about what the script wants.
mkdir -p ~/bin
cat > ~/bin/gpu-report <<'EOF'
#!/bin/bash
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
