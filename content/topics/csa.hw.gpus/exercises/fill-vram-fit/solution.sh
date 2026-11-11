# The finished script. In the lab you'd fill the three gaps with nano; here
# it's written in one go: cat > FILE <<'EOF' writes every line up to EOF
# into the file, and the quotes round 'EOF' keep the shell from changing
# anything in between. A byte is 8 bits, a GiB is 1,073,741,824 bytes
# (1,024 x 1,024 x 1,024), and 25% headroom means the card must hold the
# weights and a quarter again: weights x (100 + 25) / 100.
cat > ~/bin/vram-fit <<'EOF'
#!/bin/bash
# Usage: vram-fit PARAMS_BILLION BITS CARD_GIB HEADROOM_PCT
# Says whether a model fits one GPU's memory. PARAMS_BILLION is the model's
# size in billions of parameters, BITS the bits each parameter is stored in
# (32, 16, 8 or 4), CARD_GIB the card's memory in GiB, and HEADROOM_PCT the
# room to leave on top of the weights, as a percentage of them. Prints the
# weights in GiB, what the card must hold, and whether it does.
if [ $# -ne 4 ]; then
  echo "Usage: vram-fit PARAMS_BILLION BITS CARD_GIB HEADROOM_PCT" >&2
  exit 2
fi

awk -v params="$1" -v bits="$2" -v card="$3" -v headroom="$4" 'BEGIN {
  bytes_each = bits / 8                          # the bytes one parameter takes
  weights = params * 1000000000 * bytes_each / 1073741824 # all the bytes, as GiB
  needed = weights * (100 + headroom) / 100      # the weights and the room on top
  printf "weights: %.1f GiB\n", weights
  printf "needed: %.1f GiB\n", needed
  print "fits: " (needed <= card ? "yes" : "no")
}'
EOF
~/bin/vram-fit 7 16 16 25
~/bin/vram-fit 7 16 22 25
