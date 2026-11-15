# Wrong: without -c or a single field, jq prints each matching object
# over eight or nine rows, and wc -l counts the rows, not the requests.
mkdir -p ~/jq
cd /var/log/shop
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
jq -r 'select(.status >= 500) | .path' api.jsonl > ~/jq/failed-paths.txt
jq 'select(.ms > 1000)' api.jsonl | wc -l > ~/jq/slow-count.txt
jq -r 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
