# Wrong: the header line "user" is counted as a user.
mkdir -p ~/report
cd /var/log/shop
awk '$3 ~ /^5[0-9][0-9]$/' access.log | wc -l > ~/report/failed-count.txt
awk '{print $2}' access.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > ~/report/top-path.txt
cut -d, -f1 requests.csv | sort -u | wc -l > ~/report/unique-users.txt
grep -i error app.log > ~/report/errors.txt
