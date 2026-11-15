# A look at the log first: the lines aren't all laid out the same way, and
# jq '.' prints one of them with a field on each line.
head -n 4 /var/log/shop/api.jsonl
head -n 1 /var/log/shop/api.jsonl | jq '.'
mkdir -p ~/jq
cd /var/log/shop
# 1. Each line's path, without quotes (-r), then the counting pipeline.
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
# 2. select keeps the lines whose status is 500 or above; the | inside the
#    quotes hands each of them to .path.
jq -r 'select(.status >= 500) | .path' api.jsonl > ~/jq/failed-paths.txt
# 3. One line out for each request slower than 1000 ms, counted by wc -l.
jq 'select(.ms > 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
# 4. The users of the failed requests, counted, biggest first, top one kept.
jq -r 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
cat ~/jq/by-path.txt ~/jq/slow-count.txt ~/jq/top-failing-user.txt
