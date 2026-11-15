# Wrong: no -r, so jq prints each path and user in its JSON quotes, and
# the saved lines read "/api/cart" where /api/cart was asked for.
mkdir -p ~/jq
cd /var/log/shop
jq '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
jq 'select(.status >= 500) | .path' api.jsonl > ~/jq/failed-paths.txt
jq 'select(.ms > 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
jq 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
