# Wrong: two faults fixed, but of all the instances that fit, the script
# still prints the last one in the table rather than the cheapest: an 80 GB
# A100 at $5.07 an hour for a model a $0.71 L4 runs.
sed -i -e 's|w \* (100 - h) / 100|w * (100 + h) / 100|' \
  -e 's|\$6 \* \$8 >= n|$8 >= n|' ~/bin/fit-check
~/bin/fit-check 9 16 15
