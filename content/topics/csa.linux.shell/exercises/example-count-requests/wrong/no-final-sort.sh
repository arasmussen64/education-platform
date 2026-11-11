# Wrong: the pipeline stops before sort -rn, so the counts are in the order
# of the statuses, not biggest first.
mkdir -p ~/example
cd /var/log/shop
awk '{print $3}' access.log | sort | uniq -c > ~/example/by-status.txt
grep -i error app.log | head -n 3 > ~/example/first-errors.txt
