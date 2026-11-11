# Wrong: two faults fixed, but the script still compares the model with
# all of an instance's cards added up. A model that needs 80 GiB on one
# card is sent to four cards of 22, and runs out of memory as it starts.
sed -i -e 's|w \* (100 - h) / 100|w * (100 + h) / 100|' \
  -e 's|echo "$fits" \| tail -n 1|echo "$fits" \| sort -k2 -n \| head -n 1|' ~/bin/fit-check
~/bin/fit-check 9 16 15
