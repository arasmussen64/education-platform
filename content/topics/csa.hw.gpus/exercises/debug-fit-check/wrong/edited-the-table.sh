# Wrong: two faults fixed in the script, and the third hidden by changing
# the table instead (the learner has sudo): its rows sorted dearest first,
# so the last row that fits happens to be the cheapest. The script still
# doesn't look for the cheapest, and the next table it reads will catch it
# out.
sed -i -e 's|w \* (100 - h) / 100|w * (100 + h) / 100|' \
  -e 's|\$6 \* \$8 >= n|$8 >= n|' ~/bin/fit-check
sudo sh -c '{ head -n 1 /srv/plan/gpus.csv; tail -n +2 /srv/plan/gpus.csv | sort -t, -k10 -rn; } > /tmp/gpus.csv && cat /tmp/gpus.csv > /srv/plan/gpus.csv'
~/bin/fit-check 9 16 15
