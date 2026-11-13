# A reference ~/bin/probe. cat > FILE <<'EOF' writes the lines that follow,
# up to EOF, into FILE (the quotes round EOF keep the shell from expanding
# anything in them); in the lab you would type them into nano.
cat > ~/bin/probe <<'EOF'
#!/bin/bash
# probe URL [COUNT]: requests URL COUNT times (20 if no COUNT is given), one
# after another, and prints one line per attempt, "N RESULT SECONDS", then
# how many of each result there were, largest first, and the failure rate.
set -euo pipefail

url=$1
count=${2:-20}
results=""

for ((i = 1; i <= count; i++)); do
  # curl fails on purpose here, so keep its exit status instead of letting
  # set -e end the script.
  status=0
  out=$(curl -s -o /dev/null --max-time 2 -w '%{http_code} %{time_total}' "$url") || status=$?
  code=${out%% *}
  seconds=${out##* }
  if ((status == 0 && code < 400)); then
    result=ok
  elif ((status == 0)); then
    result=http-$code
  elif ((status == 6)); then
    result=no-address
  elif ((status == 7)); then
    result=no-connection
  elif ((status == 28)); then
    result=timeout
  else
    result=other-$status
  fi
  echo "$i $result $seconds"
  results+="$result"$'\n'
done

# How many of each: largest count first, equal counts in alphabetical order.
printf '%s' "$results" | sort | uniq -c | sort -k1,1nr -k2,2 | awk -v n="$count" '{print $2, $1 "/" n}'

# The failure rate, rounded half up: 100 x failed / count, plus a half, cut
# to a whole number.
failed=$(printf '%s' "$results" | grep -cv '^ok$' || true)
echo "failure-rate $(((200 * failed + count) / (2 * count)))"
EOF
chmod +x ~/bin/probe
on office ~/bin/probe http://www.shop.test/ 5
on office ~/bin/probe http://10.99.0.5/ 2
