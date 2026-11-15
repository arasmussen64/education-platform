# Wrong: every line it prints is right, but curl's URL is used without
# quotes, so a URL with a ? or a * in it could be expanded by the shell.
# ShellCheck points it out (SC2086), and the script was left that way.
cat > ~/bin/probe <<'EOF'
#!/bin/bash
set -euo pipefail
url=$1
count=${2:-20}
results=""
for ((i = 1; i <= count; i++)); do
  status=0
  out=$(curl -s -o /dev/null --max-time 2 -w '%{http_code} %{time_total}' $url) || status=$?
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
printf '%s' "$results" | sort | uniq -c | sort -k1,1nr -k2,2 | awk -v n="$count" '{print $2, $1 "/" n}'
failed=$(printf '%s' "$results" | grep -cv '^ok$' || true)
echo "failure-rate $(((200 * failed + count) / (2 * count)))"
EOF
chmod +x ~/bin/probe
