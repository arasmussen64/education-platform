# Wrong: the failed paths are right but sorted, not in the log's order.
mkdir -p ~/jq
cd /var/log/shop
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
jq -r 'select(.status >= 500) | .path' api.jsonl | sort > ~/jq/failed-paths.txt
jq 'select(.ms > 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
jq -r 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
