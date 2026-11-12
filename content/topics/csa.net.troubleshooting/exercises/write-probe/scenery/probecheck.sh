# probecheck.sh: the write lab's check helpers. A check starts with:
#   . /usr/local/lib/lab/probecheck.sh
# The checks run the learner's ~/bin/probe from the office, on targets the
# checks make for themselves (servers whose answers are chosen at check
# time), and compare what it prints with what they work out.
. /usr/local/lib/netlab/checklib.sh
# "Alphabetical" as sort does it on a server with no language set.
export LC_ALL=C

PROBE=/home/learner/bin/probe

# have_probe: the script is there and may be run; otherwise says why.
have_probe() {
  [ -f "$PROBE" ] || { echo "there is no ~/bin/probe"; return 1; }
  [ -x "$PROBE" ] || { echo "~/bin/probe can't be run: chmod +x ~/bin/probe"; return 1; }
}

# probe ARGS...: the learner's probe, run on the office as a check would.
probe() { on office timeout 25 "$PROBE" "$@" 2> /dev/null; }

# attempts OUTPUT / summary OUTPUT: the per-attempt lines (they start with a
# number) and the summary lines (the rest).
attempts() { echo "$1" | grep -E '^[0-9]'; }
summary() { echo "$1" | grep -vE '^[0-9]' | grep -v '^$'; }

# expected COUNT RESULT=N...: the summary a probe of COUNT requests should
# end with when they gave N of each RESULT: largest count first, equal
# counts in alphabetical order, then the failure rate rounded half up.
expected() {
  local n=$1 pair failed=0
  shift
  for pair in "$@"; do
    [ "${pair%%=*}" = ok ] || failed=$((failed + ${pair#*=}))
  done
  for pair in "$@"; do
    echo "${pair#*=} ${pair%%=*}"
  done | sort -k1,1nr -k2,2 | awk -v n="$n" '{print $2, $1 "/" n}'
  # Rounded half up, in whole numbers: (200 f + n) // 2n.
  echo "failure-rate $(((200 * failed + n) / (2 * n)))"
}

# serve_on_targets PROGRAM ARGS...: starts one of the checks' servers on
# targets in the background, and waits until its port (the first argument)
# listens. stop_servers ends them.
SERVERS=()
serve_on_targets() {
  local program=$1 port=$2 i
  shift
  on targets python3 "/usr/local/lib/lab/$program" "$@" > /dev/null 2>&1 &
  SERVERS+=("$!")
  for i in $(seq 1 30); do
    on targets ss -ltnH "sport = :$port" | grep LISTEN > /dev/null && return 0
    sleep 0.2
  done
  return 1
}
stop_servers() {
  local pid
  for pid in "${SERVERS[@]}"; do kill "$pid" 2> /dev/null; done
  pkill -f "/usr/local/lib/lab/[k]th-server" 2> /dev/null
  pkill -f "/usr/local/lib/lab/[h]angup-server" 2> /dev/null
  SERVERS=()
}
