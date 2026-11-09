# Wrong: counts every error status, 4xx as well as 5xx.
mkdir -p ~/report
cd /var/log/shop
grep -c -E ' [45][0-9][0-9] ' access.log > ~/report/failed-count.txt
awk '{print $2}' access.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > ~/report/top-path.txt
tail -n +2 requests.csv | cut -d, -f1 | sort -u | wc -l > ~/report/unique-users.txt
grep -i error app.log > ~/report/errors.txt
