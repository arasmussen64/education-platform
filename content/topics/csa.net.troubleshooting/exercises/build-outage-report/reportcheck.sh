# reportcheck.sh: the build lab's check helper. A check starts with
#   . /usr/local/lib/lab-checks/reportcheck.sh
# and calls compare SHAPE, which prints "right" or what was wrong.
export LC_ALL=C
SCRIPT=/home/learner/bin/outage-report
TOOLS=/usr/local/lib/lab-checks

# compare SHAPE: makes a log of that shape (or takes the real one, for
# "real"), runs the learner's script and the checks' own on it, and prints
# "right", or the first line that differs.
compare() {
  local shape=$1 log what got want n i a b
  [ -f "$SCRIPT" ] || { echo "there is no ~/bin/outage-report"; return; }
  [ -x "$SCRIPT" ] || { echo "~/bin/outage-report can't be run: chmod +x ~/bin/outage-report"; return; }
  if [ "$shape" = real ]; then
    log=/var/log/shop-monitor.log
    what="the office monitor's real log"
  else
    log=$(mktemp /tmp/check-monitor-XXXXXX.log)
    chmod 644 "$log"
    trap 'rm -f "$log"' RETURN
    python3 "$TOOLS/make-log" "$shape" "$(date +%s%N)" > "$log"
    what="a log of $(wc -l < "$log") loads made at check time"
  fi
  got=$(runuser -u learner -- timeout 20 "$SCRIPT" "$log" 2> /dev/null) || true
  want=$(python3 "$TOOLS/report-truth" "$log")
  [ "$got" = "$want" ] && { echo right; return; }
  n=$(echo "$want" | wc -l)
  for ((i = 1; i <= n + 1; i++)); do
    a=$(echo "$got" | sed -n "${i}p")
    b=$(echo "$want" | sed -n "${i}p")
    if [ "$a" != "$b" ]; then
      if [ -z "$b" ]; then
        echo "on $what, the report has a line too many: '$a'"
      else
        echo "on $what, line $i of the report is '${a:-(nothing)}', and should be '$b'"
      fi
      return
    fi
  done
  echo "on $what, the report isn't the one it should be"
}
