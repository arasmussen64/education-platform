# Wrong: grep without -i misses the lowercase error lines.
mkdir -p ~/example
cd /var/log/shop
awk '{print $3}' access.log | sort | uniq -c | sort -rn > ~/example/by-status.txt
grep ERROR app.log | head -n 3 > ~/example/first-errors.txt
