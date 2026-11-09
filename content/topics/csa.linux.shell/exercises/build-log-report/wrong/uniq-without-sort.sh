# Wrong: uniq -c without sorting first only counts neighbouring repeats.
mkdir -p ~/report
cd /var/log/shop
awk '$3 ~ /^5[0-9][0-9]$/' access.log | wc -l > ~/report/failed-count.txt
awk '{print $2}' access.log | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > ~/report/top-path.txt
tail -n +2 requests.csv | cut -d, -f1 | sort -u | wc -l > ~/report/unique-users.txt
grep -i error app.log > ~/report/errors.txt
