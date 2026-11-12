# lbcheck.sh: the load-balancing labs' check helpers, the same file in every
# lab of the topic. A check starts with:   . /usr/local/lib/lab/lbcheck.sh
# It reads HAProxy's real state on lb through its runtime API, the web
# servers' own counters, and real answers from the office; the network
# base's helpers (on, wait_for, intact ...) come with it.
. /usr/local/lib/netlab/checklib.sh

# api COMMAND: HAProxy's answer to one runtime API command, from lb's stats
# socket, or nothing when HAProxy isn't running.
api() { echo "$1" | on lb socat -t 2 stdio /run/haproxy/admin.sock 2> /dev/null; }

# servers: one line per server in HAProxy's show stat, whatever the learner
# called its backends and servers, found by address:
#   ADDRESS STATUS CHKFAIL CHKDOWN SCUR RISE FALL BACKEND SERVER
# (STATUS is UP, DOWN, MAINT, DRAIN, or "no check" written no-check.)
servers() {
  api "show stat" | awk -F, '
    NR == 1 { for (i = 1; i <= NF; i++) { h = $i; sub(/^# /, "", h); col[h] = i }; next }
    NF > 1 && $2 != "FRONTEND" && $2 != "BACKEND" {
      s = $col["status"]; gsub(/ /, "-", s)
      print $col["addr"], s, $col["chkfail"] + 0, $col["chkdown"] + 0, $col["scur"] + 0, $col["check_rise"], $col["check_fall"], $1, $2
    }'
}

# field ADDRESS N: field N (1 to 9, as above) of the server at ADDRESS; with
# a server in two backends, one line for each.
field() { servers | awk -v a="$1" -v n="$2" '$1 == a {print $n}'; }

# The machine that has an address, and the address of a machine's server.
machine_of() {
  case ${1%%:*} in
    10.0.1.11) echo web1 ;; 10.0.1.12) echo web2 ;; 10.0.1.13) echo web3 ;;
    10.0.1.21) echo api1 ;; 10.0.1.22) echo api2 ;;
    10.0.1.31) echo stock1 ;; 10.0.1.32) echo stock2 ;;
  esac
}
address_of() {
  case $1 in
    web1) echo 10.0.1.11:8080 ;; web2) echo 10.0.1.12:8080 ;; web3) echo 10.0.1.13:8080 ;;
    api1) echo 10.0.1.21:8081 ;; api2) echo 10.0.1.22:8081 ;;
    stock1) echo 10.0.1.31:7000 ;; stock2) echo 10.0.1.32:7000 ;;
  esac
}

# checks_seen MACHINE: how many health checks the machine's web server has
# been sent since it started; db_failed MACHINE: how many of them it failed
# because the database didn't answer (shop-web counts both in its /run).
checks_seen() { on "$1" cat /run/shop/checks 2> /dev/null || echo 0; }
db_failed() { on "$1" cat /run/shop/db-failed 2> /dev/null || echo 0; }

# haproxy_ready: waits, up to about 20 s after a boot, until HAProxy on lb
# answers its runtime API, and says whether it does. A unit that has failed
# isn't waited for.
haproxy_ready() {
  local i
  for i in $(seq 1 20); do
    api "show info" | grep '^Pid:' > /dev/null && return 0
    case $(systemctl is-active haproxy@lb) in activating | reloading) ;; *) [ "$i" -ge 3 ] && break ;; esac
    sleep 1
  done
  api "show info" | grep '^Pid:' > /dev/null
}

# running_is_saved: the HAProxy running now was started (or reloaded) after
# its configuration file last changed, so it runs what the file says.
running_is_saved() {
  local started changed
  started=$(api "show info" | awk -F': ' '$1 == "Start_time_sec" {print $2}')
  changed=$(on lb stat -c %Y /etc/haproxy/haproxy.cfg)
  [ -n "$started" ] && [ "$started" -ge "$changed" ]
}

# office ARGS...: curl from the office, quietly, with a short limit.
office() { on office curl -s --max-time 3 "$@"; }

# served_by ARGS...: which server answered a request from the office
# (shop-web's X-Served-By header), or the HTTP status when none did.
served_by() {
  on office curl -s --max-time 3 -o /dev/null -D - -w 'status=%{http_code}\n' "$@" | tr -d '\r' | awk -F': ' '
    tolower($1) == "x-served-by" {who = $2}
    /^status=/ {code = substr($0, 8)}
    END {if (who != "" && code == "200") print who; else print "status-" code}'
}

# freeze MACHINE... / thaw MACHINE...: stop or start a web server's program
# where it stands (SIGSTOP and SIGCONT): the machine still accepts
# connections, and nothing ever answers them, as a hung server does.
freeze() { local m; for m in "$@"; do systemctl kill -s STOP "shop-web@$m"; done; }
thaw() { local m; for m in "$@"; do systemctl kill -s CONT "shop-web@$m" 2> /dev/null; done; }

# all_up ADDRESS...: every server at those addresses is UP in every backend
# it is in; wait_up SECONDS ADDRESS...: waits up to SECONDS for it.
all_up() {
  local a s
  for a in "$@"; do
    s=$(field "$a" 2 | sort -u)
    [ "$s" = UP ] || return 1
  done
}
wait_up() {
  local limit=$1 i
  shift
  for i in $(seq 1 $((limit * 4))); do
    all_up "$@" && return 0
    sleep 0.25
  done
  all_up "$@"
}

# not_up ADDRESS...: the servers that aren't UP, with their status, in words.
not_up() {
  local a s out=""
  for a in "$@"; do
    s=$(field "$a" 2 | sort -u | tr '\n' ' ')
    [ "$s" = "UP " ] || out+="$(machine_of "$a") is ${s:-not in the configuration} "
  done
  echo "${out% }" | sed 's/-/ /g; s/  */ /g'
}

# ms: the time now in milliseconds.
ms() { echo $(($(date +%s%N) / 1000000)); }

# unchecked ADDRESS...: the first of those servers HAProxy doesn't check,
# or nothing when it checks them all.
unchecked() {
  local a
  for a in "$@"; do
    case $(field "$a" 2 | sort -u | tr '\n' ' ') in
      *no-check*) machine_of "$a"; return ;;
    esac
  done
}

# The three behaviour tests the fill-in, the build and the debug share. Each
# prints "passed", or what it found, in a sentence, and leaves every server
# running and the database up as it found them.

# hung_test SECONDS ADDRESS...: freezes the servers at those addresses at
# once and passes if HAProxy marks every one of them DOWN within SECONDS of
# the last health check it answered. That is the slowest case a policy has
# to cover, a server that hangs just after a good check: HAProxy's next
# check is then a whole inter away, and each check after it waits its whole
# timeout. Each server's program wrote its count of checks when that last
# check arrived (its /run/shop/checks) and can write nothing once frozen, so
# the file's time is that moment, and the result doesn't depend on when the
# freeze fell. 0.75 s more is allowed for the test's own looking, which can
# only make a server seem slower. Then it lets them run again and waits for
# them to be back.
hung_test() {
  local limit=$1 a m t0 now all pending slow took report=""
  declare -A last down
  shift
  [ -n "$(api 'show info')" ] || { echo "HAProxy on lb isn't running"; return; }
  wait_up 15 "$@" || { echo "not every server is up before the test: $(not_up "$@")"; return; }
  m=$(unchecked "$@")
  [ -z "$m" ] || { echo "$m has no health check, so HAProxy would never take it out"; return; }
  HUNG=()
  for a in "$@"; do HUNG+=("$(machine_of "$a")"); done
  trap 'thaw "${HUNG[@]}"' EXIT
  freeze "${HUNG[@]}"
  t0=$(ms)
  for m in "${HUNG[@]}"; do
    last[$m]=$(on "$m" date -r /run/shop/checks +%s%3N 2> /dev/null) || last[$m]=$t0
  done
  while :; do
    all=$(servers)
    now=$(ms)
    pending=""
    for a in "$@"; do
      m=$(machine_of "$a")
      [ -n "${down[$m]}" ] && continue
      if echo "$all" | awk -v a="$a" '$1 == a {print $2}' | grep -v '^DOWN' > /dev/null; then
        [ $((now - last[$m])) -le $((limit * 1000 + 750)) ] && pending+="$m "
      else
        down[$m]=$now
      fi
    done
    [ -z "$pending" ] && break
    sleep 0.1
  done
  thaw "${HUNG[@]}"
  trap - EXIT
  wait_up 25 "$@" > /dev/null
  slow=""
  for m in "${HUNG[@]}"; do
    if [ -z "${down[$m]}" ]; then
      slow+="$m "
      report+=" $m over $limit s"
      continue
    fi
    took=$((down[$m] - last[$m]))
    report+=" $m $((took / 1000)).$((took % 1000 / 100)) s"
    [ "$took" -le $((limit * 1000 + 750)) ] || slow+="$m "
  done
  if [ -n "$slow" ]; then
    echo "frozen, so that they accepted connections and never answered, ${slow% } still had a share of the traffic more than $limit seconds after answering its last health check"
  else
    echo passed
  fi
  echo "(from the last check each answered to DOWN:$report)" >&2
}

# db_test ADDRESS...: stops the database for up to 16 seconds while the
# office asks for the front page, and passes if every server at those
# addresses has had two health checks meanwhile, has failed none of them for
# want of the database, and stayed in rotation, and every page was answered.
db_test() {
  local a m t0 page missing
  declare -A seen failed
  [ -n "$(api 'show info')" ] || { echo "HAProxy on lb isn't running"; return; }
  wait_up 15 "$@" || { echo "not every server is up before the test: $(not_up "$@")"; return; }
  m=$(unchecked "$@")
  [ -z "$m" ] || { echo "$m has no health check"; return; }
  for a in "$@"; do
    m=$(machine_of "$a")
    seen[$m]=$(checks_seen "$m")
    failed[$m]=$(db_failed "$m")
  done
  trap 'systemctl start shop-db@db' EXIT
  systemctl stop shop-db@db
  t0=$(ms)
  while :; do
    page=$(served_by http://10.0.9.1/)
    case $page in
      status-*) echo "while the database was down, the front page got ${page#status-} from the balancer"; return ;;
    esac
    missing=""
    for a in "$@"; do
      m=$(machine_of "$a")
      if [ "$(db_failed "$m")" -gt "${failed[$m]}" ]; then
        echo "while the database was down, $m failed a health check because the database didn't answer"
        return
      fi
      [ "$(checks_seen "$m")" -ge $((${seen[$m]} + 2)) ] || missing+="$m "
    done
    all_up "$@" || { echo "while the database was down, a server went out of rotation: $(not_up "$@")"; return; }
    [ -z "$missing" ] && break
    if [ $(($(ms) - t0)) -gt 16000 ]; then
      echo "the database was down for 16 seconds, and ${missing% } had fewer than two health checks meanwhile"
      return
    fi
    sleep 0.3
  done
  echo passed
}

# hiccup_test ADDRESS...: switches on the servers' hiccup (one health check
# in four answered 503 at once, starting with the next one) until each has
# had two checks, and passes if none of them went DOWN for it.
hiccup_test() {
  local a m t0 missing went now
  declare -A seen downs
  [ -n "$(api 'show info')" ] || { echo "HAProxy on lb isn't running"; return; }
  wait_up 15 "$@" || { echo "not every server is up before the test: $(not_up "$@")"; return; }
  m=$(unchecked "$@")
  [ -z "$m" ] || { echo "$m has no health check"; return; }
  HICCUP=()
  for a in "$@"; do
    m=$(machine_of "$a")
    HICCUP+=("$m")
    seen[$m]=$(checks_seen "$m")
    downs[$m]=$(field "$a" 4 | awk '{n += $1} END {print n + 0}')
  done
  trap 'for m in "${HICCUP[@]}"; do on "$m" rm -f /run/shop/hiccup; done' EXIT
  for m in "${HICCUP[@]}"; do on "$m" touch /run/shop/hiccup; done
  t0=$(ms)
  while :; do
    missing=""
    for m in "${HICCUP[@]}"; do
      [ "$(checks_seen "$m")" -ge $((${seen[$m]} + 2)) ] || missing+="$m "
    done
    [ -z "$missing" ] && break
    if [ $(($(ms) - t0)) -gt 20000 ]; then
      echo "in 20 seconds ${missing% } had fewer than two health checks"
      return
    fi
    sleep 0.25
  done
  sleep 0.5
  went=""
  for a in "$@"; do
    m=$(machine_of "$a")
    now=$(field "$a" 4 | awk '{n += $1} END {print n + 0}')
    [ "$now" -gt "${downs[$m]}" ] && went+="$m "
  done
  if [ -n "$went" ]; then
    echo "one failed check in four took ${went% } out of rotation"
  else
    echo passed
  fi
}
