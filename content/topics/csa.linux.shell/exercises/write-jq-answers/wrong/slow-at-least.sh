# Wrong: >= counts the requests that took exactly 1000 ms too. The
# question was longer than 1000 ms.
mkdir -p ~/jq
cd /var/log/shop
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
jq -r 'select(.status >= 500) | .path' api.jsonl > ~/jq/failed-paths.txt
jq 'select(.ms >= 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
jq -r 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
