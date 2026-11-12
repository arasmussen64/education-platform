# checklib.sh: helpers for the network labs' checks (checks.yaml).
# A check starts with:   . /usr/local/lib/netlab/checklib.sh
# Every helper reads the network's real state (the kernel, the daemons, a
# probe from another machine, a capture), never the learner's files, so a
# check can't be passed by editing a file nothing uses.
# Checks run as root on the lab machine; "on M CMD" runs CMD on machine M.

# wait_for SECONDS COMMAND...: retries COMMAND once a second until it
# succeeds or SECONDS have passed. For a session that needs a moment to
# come up after a boot; never to wait out a race.
wait_for() {
  local limit=$1 i
  shift
  for ((i = 0; i < limit; i++)); do
    "$@" > /dev/null 2>&1 && return 0
    sleep 1
  done
  "$@" > /dev/null 2>&1
}

# json PYTHON-EXPRESSION: reads JSON on stdin as d, prints the expression
# (the lab images have no jq). json "d['peers']['10.0.0.2']['state']"
json() {
  python3 -c 'import json, sys
try:
    d = json.load(sys.stdin)
    r = eval(sys.argv[1], {"d": d})
except Exception as e:
    print("json: " + type(e).__name__)
    sys.exit(0)
print(r if not isinstance(r, (dict, list)) else json.dumps(r, sort_keys=True))' "$1"
}

# frr MACHINE 'show ... json': FRR's own answer, from its running daemons.
frr() { on "$1" vtysh -c "$2" 2> /dev/null; }

# tcp_state FROM HOST PORT: open, refused or dropped, as seen from machine
# FROM. A reset comes back in milliseconds; a drop takes the whole timeout.
tcp_state() {
  local from=$1 host=$2 port=$3 start ms
  start=$(date +%s%N)
  if on "$from" nc -z -w 2 "$host" "$port" > /dev/null 2>&1; then
    echo open
    return
  fi
  ms=$((($(date +%s%N) - start) / 1000000))
  if ((ms >= 1500)); then echo dropped; else echo refused; fi
}

# pcap MACHINE IFACE FILTER SECONDS -- COMMAND...: captures on one machine's
# interface for SECONDS while COMMAND runs (usually "on OTHER ..."), and
# prints the path of the capture file; the caller reads it (tcpdump -r,
# tshark -r) and removes it. -Z root: Ubuntu's tcpdump otherwise switches to
# its own user and can't write the file a check made.
pcap() {
  local m=$1 dev=$2 filter=$3 secs=$4 file pid
  shift 5
  file=$(mktemp /tmp/check-XXXXXX.pcap)
  on "$m" timeout "$secs" tcpdump -Z root -nn -U -i "$dev" -w "$file" "$filter" > /dev/null 2>&1 &
  pid=$!
  sleep 1
  "$@" > /dev/null 2>&1 || true
  wait "$pid" 2> /dev/null || true
  echo "$file"
}

# capture ...: as pcap, but prints the packets as tcpdump reads them back
# (-nn, one packet a line) and removes the file.
capture() {
  local file
  file=$(pcap "$@")
  tcpdump -nn -r "$file" 2> /dev/null
  rm -f "$file"
}

# frr_saved MACHINE: exit 0 when FRR's running configuration is the one in
# the machine's /etc/frr/frr.conf, so a restart (or a reboot) gives the same
# routing; otherwise prints how they differ. FRR writes the file from the
# running configuration with "write memory".
frr_saved() {
  local m=$1 running saved
  running=$(on "$m" vtysh -c 'show running-config' 2> /dev/null | sed -n '/^frr version/,$p' | grep -v '^!$' | grep -v '^end$')
  saved=$(on "$m" cat /etc/frr/frr.conf 2> /dev/null | sed -n '/^frr version/,$p' | grep -v '^!$' | grep -v '^end$')
  if [[ $running == "$saved" ]]; then return 0; fi
  diff <(echo "$saved") <(echo "$running") | head -n 6
  return 1
}

# intact: the scenery the learner mustn't change (the topology, the other
# side's configuration) is as the image had it.
intact() { /usr/local/lib/netlab/netlab intact; }
