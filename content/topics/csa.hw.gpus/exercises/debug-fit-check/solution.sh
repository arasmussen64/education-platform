# The fixed script, with the three faults put right (in the lab you'd make
# the same three edits with nano; here it's written in one go: cat > FILE
# <<'EOF' writes every line up to EOF into the file, and the quotes round
# 'EOF' keep the shell from changing anything in between):
#   1. The headroom is room on top of the weights, so it is added:
#      100 + h, not 100 - h. Taking it away sent a model to a card too
#      small for it once it ran.
#   2. A model that runs on one card needs one card's memory, $8, not the
#      instance's cards added up ($6 * $8): four 22 GiB cards are not one
#      card of 88.
#   3. The cheapest is found by sorting the fits by price (the second
#      field, as numbers) and keeping the first; the last row of the
#      table that fits is just the last row.
cat > ~/bin/fit-check <<'EOF'
#!/bin/bash
# Usage: fit-check PARAMS_BILLION BITS HEADROOM_PCT
# Prints the cheapest instance in /srv/plan/gpus.csv on which a model of
# PARAMS_BILLION billion parameters, each stored in BITS bits, runs on one
# card with HEADROOM_PCT % of its weights to spare, as "instance price", or
# "none" when no instance in the table can.
table=/srv/plan/gpus.csv
if [ $# -ne 3 ]; then
  echo "Usage: fit-check PARAMS_BILLION BITS HEADROOM_PCT" >&2
  exit 2
fi

# The weights in GiB, and what the card must hold with the headroom.
weights=$(awk -v p="$1" -v b="$2" 'BEGIN {print p * 1000000000 * b / 8 / 1073741824}')
needed=$(awk -v w="$weights" -v h="$3" 'BEGIN {print w * (100 + h) / 100}')

# Every instance with the memory for it, as its name and its price.
# (The columns used: 4 instance, 8 gpu_mem_gib, 10 hourly_usd.)
fits=$(awk -F, -v n="$needed" 'NR > 1 && $8 >= n {print $4, $10}' "$table")

if [ -z "$fits" ]; then
  echo none
else
  echo "$fits" | sort -k2 -n | head -n 1
fi
EOF
~/bin/fit-check 9 16 15
~/bin/fit-check 42 16 10
