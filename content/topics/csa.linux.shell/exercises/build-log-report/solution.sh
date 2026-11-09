# The reference solution, as the learner would type it in the lab's shell.
# Each answer is a pipeline from Shell essentials, checked before it's saved.
mkdir -p ~/report
cd /var/log/shop

# Requests whose status (the third field) is in the 500s.
awk '$3 ~ /^5[0-9][0-9]$/' access.log | wc -l > ~/report/failed-count.txt

# The most requested path: group, count, biggest first, keep the winner's name.
awk '{print $2}' access.log | sort | uniq -c | sort -rn | head -n 1 | awk '{print $2}' > ~/report/top-path.txt

# Distinct users: skip the header, take the first field, one of each, count.
tail -n +2 requests.csv | cut -d, -f1 | sort -u | wc -l > ~/report/unique-users.txt

# Every line that mentions an error, in any case, unchanged.
grep -i error app.log > ~/report/errors.txt
