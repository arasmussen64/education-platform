# Wrong: grep picks the lines with 500 anywhere in them: a request that
# took 500 or 1500 ms, a note that says 'after 500 ms'. And it misses
# the 502s and 503s.
mkdir -p ~/jq
cd /var/log/shop
jq -r '.path' api.jsonl | sort | uniq -c | sort -rn > ~/jq/by-path.txt
grep 500 api.jsonl | jq -r '.path' > ~/jq/failed-paths.txt
jq 'select(.ms > 1000) | .ms' api.jsonl | wc -l > ~/jq/slow-count.txt
jq -r 'select(.status >= 500) | .user' api.jsonl | sort | uniq -c | sort -rn | head -n 1 > ~/jq/top-failing-user.txt
