# A reference ~/bin/outage-report. cat > FILE <<'EOF' writes the lines that
# follow, up to EOF, into FILE (the quotes round EOF keep the shell from
# expanding anything in them); in the lab you would type them into nano.
cat > ~/bin/outage-report <<'EOF'
#!/bin/bash
# outage-report LOG: what the office monitor's log says about the loads in
# it: how many failed and how many were slow, by the first address each
# load tried, the longest run of failures, and a verdict.
set -euo pipefail
log=$1

# Each load, one a line: its time, the first address it tried, and what it
# was: fail (curl's exit status not 0, or an HTTP status of 400 or more),
# slow (it succeeded, in 1 second or more) or ok.
loads=$(awk '{
  split($3, tried, ",")
  status = substr($6, 6) + 0
  if (status != 0 || $4 + 0 >= 400) result = "fail"
  else if ($5 + 0 >= 1) result = "slow"
  else result = "ok"
  print $1, tried[1], result
}' "$log")

total=$(echo "$loads" | wc -l)
failed=$(echo "$loads" | awk '$3 == "fail" {n++} END {print n + 0}')
slow=$(echo "$loads" | awk '$3 == "slow" {n++} END {print n + 0}')
echo "loads $total"
# Rounded half up, in whole numbers: (200 x failed + total) / (2 x total).
echo "failed $failed ($(((200 * failed + total) / (2 * total)))%)"
echo "slow $slow"

# One line per first address, sorted as text.
echo "$loads" | awk '{
  seen[$2] = 1
  count[$2 " " $3]++
}
END {
  for (a in seen) print "by-address", a, "ok=" count[a " ok"] + 0, "fail=" count[a " fail"] + 0, "slow=" count[a " slow"] + 0
}' | sort -k2,2

# The longest run of failed loads in a row: its first time and its length.
# Only a longer run replaces it, so of two as long, the first stays.
longest=$(echo "$loads" | awk '
$3 == "fail" {
  if (run == 0) start = $1
  run++
  if (run > best) { best = run; best_start = start }
  next
}
{ run = 0 }
END { if (best) print best_start, best; else print "none", 0 }')
echo "longest-outage $longest"

# The verdict: the one address that every failed and slow load tried
# first; else "time" when every failure is in the longest run; else none.
troubled=$(echo "$loads" | awk '$3 != "ok" {print $2}' | sort -u)
if [ -n "$troubled" ] && [ "$(echo "$troubled" | wc -l)" -eq 1 ]; then
  echo "verdict $troubled"
elif [ "$failed" -gt 0 ] && [ "${longest##* }" -eq "$failed" ]; then
  echo "verdict time"
else
  echo "verdict none"
fi
EOF
chmod +x ~/bin/outage-report
~/bin/outage-report /var/log/shop-monitor.log
