# Wrong: tests for a status of exactly 500, which misses the 502s and
# 503s. The server's failures are every status from 500 up.
mkdir -p ~/jq
cd /var/log/shop
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
jq -r 'select(.status == 500) | .path' api.jsonl > ~/jq/failed-paths.txt
jq 'select(.ms > 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
jq -r 'select(.status == 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
