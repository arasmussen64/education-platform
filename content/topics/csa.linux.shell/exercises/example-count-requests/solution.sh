mkdir -p ~/example
cd /var/log/shop
awk '{print $3}' access.log | sort | uniq -c | sort -rn > ~/example/by-status.txt
grep -i error app.log | head -n 3 > ~/example/first-errors.txt
cat ~/example/by-status.txt ~/example/first-errors.txt
