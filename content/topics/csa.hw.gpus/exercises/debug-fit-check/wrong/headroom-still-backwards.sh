# Wrong: two faults fixed, but the headroom is still taken away from the
# weights instead of added to them, so a model is sent to a card that holds
# less than it needs once it runs.
sed -i -e 's|\$6 \* \$8 >= n|$8 >= n|' \
  -e 's|echo "$fits" \| tail -n 1|echo "$fits" \| sort -k2 -n \| head -n 1|' ~/bin/fit-check
~/bin/fit-check 9 16 15
