# Wrong: two faults fixed, and the third "fixed" by taking the first row
# that fits instead of the last. The table isn't in order of price, so the
# first row that fits is no more the cheapest than the last: a $0.80 L4
# where a $0.71 one runs the same model.
sed -i -e 's|w \* (100 - h) / 100|w * (100 + h) / 100|' \
  -e 's|\$6 \* \$8 >= n|$8 >= n|' \
  -e 's|echo "$fits" \| tail -n 1|echo "$fits" \| head -n 1|' ~/bin/fit-check
~/bin/fit-check 9 16 15
