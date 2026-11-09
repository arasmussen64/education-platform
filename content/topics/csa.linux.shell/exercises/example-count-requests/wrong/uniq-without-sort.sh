# Wrong: uniq -c without sort first counts only neighbouring repeats.
mkdir -p ~/example
cd /var/log/shop
awk '{print $3}' access.log | uniq -c | sort -rn > ~/example/by-status.txt
grep -i error app.log | head -n 3 > ~/example/first-errors.txt
