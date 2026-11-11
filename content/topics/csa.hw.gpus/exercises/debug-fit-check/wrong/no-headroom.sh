# Wrong: the backwards headroom "fixed" by leaving the headroom out, which
# changes what the script is meant to do. A model whose weights alone fit a
# card, and whose headroom doesn't, is still sent to that card.
sed -i -e 's|w \* (100 - h) / 100|w|' \
  -e 's|\$6 \* \$8 >= n|$8 >= n|' \
  -e 's|echo "$fits" \| tail -n 1|echo "$fits" \| sort -k2 -n \| head -n 1|' ~/bin/fit-check
~/bin/fit-check 9 16 15
