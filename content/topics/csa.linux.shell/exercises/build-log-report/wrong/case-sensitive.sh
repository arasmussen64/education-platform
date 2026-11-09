# Wrong: only the capitalised ERROR lines, missing the lowercase ones.
mkdir -p ~/report
cd /var/log/shop
awk '$3 ~ /^5[0-9][0-9]$/' access.log | wc -l > ~/report/failed-count.txt
awk '{print $2}' access.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > ~/report/top-path.txt
tail -n +2 requests.csv | cut -d, -f1 | sort -u | wc -l > ~/report/unique-users.txt
grep ERROR app.log > ~/report/errors.txt
