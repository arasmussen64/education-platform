# Wrong: the sum is right, but given no files the script doesn't say how to
# use it: paste complains about a file called '' and the script still exits
# with 0, so whatever called it can't tell it failed.
mkdir -p ~/bin
cat > ~/bin/steal-pct <<'EOF'
#!/bin/bash
paste "$1" "$2" | awk '{
  for (i = 2; i <= 9; i++) total += $(i + 11) - $i
  printf "%.1f\n", ($20 - $9) * 100 / total
}'
EOF
chmod +x ~/bin/steal-pct
