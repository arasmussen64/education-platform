#!/usr/bin/env bash
# The shop's API log, as JSON lines: one JSON object for each request. As in
# seed.sh, everything is decided by arithmetic on the line number, so the
# file is identical on every build and the checks can compute the truth.
#
# Two programs write to the log and lay their lines out differently: one
# compact, one with a space after every colon and comma and the fields in
# another order. Some lines carry a note whose text holds a number that
# looks like a status. So a count made with grep or awk on the text comes
# out wrong, and one made with jq, which reads the JSON, doesn't.
set -euo pipefail

mkdir -p /var/log/shop
log=/var/log/shop/api.jsonl
: > "$log"

for i in $(seq 1 360); do
  # Fifteen requests in every round: 5 for items, 4 for cart, 3 for orders,
  # 2 for login and 1 for search, never one path many times in a row, so a
  # count needs its sort before uniq -c and every count is different.
  case $((i % 15)) in
    0|3|6|9|12) path=/api/items;  method=GET ;;
    1|4|7|10)   path=/api/cart;   method=POST ;;
    2|8|13)     path=/api/orders; method=POST ;;
    5|11)       path=/api/login;  method=POST ;;
    *)          path=/api/search; method=GET ;;
  esac

  # 500, 502 and 503 are the server's failures; 404 and 429 are not.
  if   (( i % 40 == 0 )); then status=503
  elif (( i % 25 == 0 )); then status=500
  elif (( i % 33 == 0 )); then status=502
  elif (( i % 17 == 0 )); then status=404
  elif (( i % 29 == 0 )); then status=429
  else status=200
  fi

  # How long the request took. A few take exactly 500, 1000 or 1500 ms.
  if   (( i % 90 == 0 )); then ms=1000
  elif (( i % 70 == 0 )); then ms=1500
  elif (( i % 45 == 0 )); then ms=500
  else ms=$(( (i * 137) % 1900 + 20 ))
  fi

  # Eleven users, spread so that one of them has the most failed requests
  # outright and a different one made the most requests.
  user="u$(( (i * 3 + (i / 7) * 3) % 11 ))"
  seconds=$(( i * 7 ))
  time=$(printf '2026-11-14T09:%02d:%02dZ' $((seconds / 60)) $((seconds % 60)))

  # A note on some requests that succeeded.
  note=""
  if (( status == 200 && i % 19 == 0 )); then note="retried after 500 ms"; fi
  if (( status == 200 && i % 47 == 0 )); then note="upstream said 503, served from cache"; fi

  if (( i % 3 == 0 )); then
    line="{\"status\": $status, \"ms\": $ms, \"path\": \"$path\", \"method\": \"$method\", \"user\": \"$user\", \"time\": \"$time\""
    if [ -n "$note" ]; then line="$line, \"note\": \"$note\""; fi
  else
    line="{\"time\":\"$time\",\"method\":\"$method\",\"path\":\"$path\",\"status\":$status,\"ms\":$ms,\"user\":\"$user\""
    if [ -n "$note" ]; then line="$line,\"note\":\"$note\""; fi
  fi
  echo "$line}" >> "$log"
done

chown root:root "$log"
chmod 644 "$log"
