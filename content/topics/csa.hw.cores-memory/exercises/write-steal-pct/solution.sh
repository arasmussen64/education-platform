# One way to write it. paste puts the two lines side by side, so the first
# line's numbers are fields 2 to 11 and the second's are fields 13 to 22:
# field i of the first line matches field i + 11 of the second. The growth
# of all eight is the time that passed; the growth of the eighth is steal.
mkdir -p ~/bin
cat > ~/bin/steal-pct <<'EOF'
#!/bin/bash
# Usage: steal-pct BEFORE AFTER
# The share of the time between two saved copies of /proc/stat's first line
# that the hypervisor gave to someone else (steal), as a percentage to one
# decimal place.
if [ $# -ne 2 ]; then
  echo "Usage: steal-pct BEFORE AFTER" >&2
  exit 2
fi
paste "$1" "$2" | awk '{
  for (i = 2; i <= 9; i++) total += $(i + 11) - $i
  steal = $20 - $9
  printf "%.1f\n", steal * 100 / total
}'
EOF
chmod +x ~/bin/steal-pct
for pair in quiet robbed mostly-idle; do echo "$pair: $(~/bin/steal-pct /srv/stat/$pair/before.txt /srv/stat/$pair/after.txt)"; done
