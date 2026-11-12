# checklib.sh: helpers for the network labs' checks (checks.yaml).
# A check starts with:   . /usr/local/lib/netlab/checklib.sh
# Every helper reads the network's real state (the kernel, the daemons, a
# probe from another machine, a capture), so a check can't be passed by
# editing a file nothing uses. The *_saved helpers then compare that state
# with the file that makes it last, so a fix made only live fails them.
# Checks run as root on the lab machine; "on M CMD" runs CMD on machine M.
# The base's README (content/lab-bases/net/README.md) lists them all.

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

# nft_saved MACHINE: exit 0 when the firewall running on the machine is the
# one its /etc/nftables.conf loads, so a reboot (nftables@MACHINE, enabled)
# brings the same rules back; otherwise prints how they differ. The file is
# loaded into a throwaway namespace (each namespace has a ruleset of its
# own, so nothing running is touched), given interfaces with the machine's
# names so a rule that names one still loads, and seeing the machine's own
# /etc so a file it includes is found. Counters are left out (nft -s).
nft_saved() {
  local m=$1 scratch="chk-nft-$1" dev n=0 from_file live
  ip netns del "$scratch" 2> /dev/null
  ip netns add "$scratch" || {
    echo "could not make a scratch namespace"
    return 1
  }
  ln -sfn "$m" "/etc/netns/$scratch"
  for dev in $(ip -n "$m" -o link | awk -F': ' '{sub(/@.*/, "", $2); print $2}'); do
    [[ $dev == lo ]] || ip -n "$scratch" link add "$dev" type veth peer name "peer$n" 2> /dev/null
    n=$((n + 1))
  done
  from_file=$(ip netns exec "$scratch" nft -f /etc/nftables.conf 2>&1 && ip netns exec "$scratch" nft -s list ruleset)
  ip netns del "$scratch"
  rm -f "/etc/netns/$scratch"
  live=$(ip netns exec "$m" nft -s list ruleset)
  [[ $from_file == "$live" ]] && return 0
  diff <(echo "$from_file") <(echo "$live") | grep '^[<>]' | head -n 6
  return 1
}

# sysctl_saved MACHINE KEY: exit 0 when the machine's live value of KEY is
# the one its /etc/sysctl.d files give it (the last file, in name order,
# that sets it), so a reboot keeps it; otherwise prints how they differ. A
# value set only with sysctl -w fails, and so does a key no file sets.
sysctl_saved() {
  local m=$1 key=$2 live saved
  live=$(ip netns exec "$m" sysctl -n "$key" 2> /dev/null | tr -s ' \t' ' ')
  saved=$(/usr/local/lib/netlab/netlab saved-sysctl "$m" "$key" | tr -s ' \t' ' ')
  if [[ -z $saved ]]; then
    echo "$m's /etc/sysctl.d doesn't set $key (it is ${live:-not there} now)"
    return 1
  fi
  [[ $live == "$saved" ]] && return 0
  echo "$m's $key is ${live:-not there} now, but its /etc/sysctl.d sets $saved"
  return 1
}

# hand_routes MACHINE: prints the machine's routes that were typed with
# "ip route add" (the kernel calls their protocol "boot"), one a line, or
# nothing. On a router whose routes must come from FRR, any line is a route
# the next boot loses. ip leaves the protocol of such a route out unless it
# is asked for details (-d), so this asks (the Module 3 critic's finding).
# Routes the topology's route lines and network files make are "boot" too:
# use it on machines whose routes come from FRR alone.
hand_routes() {
  {
    ip -d -n "$1" route show table all
    ip -d -n "$1" -6 route show table all
  } 2> /dev/null | grep -w 'proto boot' || true
}

# bgp-best MACHINE PREFIX: the path BGP chose for PREFIX on the machine, on
# one line, or "none":
#   via 192.0.2.2, localpref 100, med 0, path 65010 65100, chosen by Local Pref
# (FRR leaves localpref and med out of its answer when a route has none; BGP
# then treats them as 100 and 0. "path Local" is a prefix the machine
# announces itself.)
bgp-best() {
  local family=ipv4
  [[ $2 == *:* ]] && family=ipv6
  frr "$1" "show bgp $family unicast $2 json" | python3 -c '
import json, sys
try:
    answer = json.load(sys.stdin)
except ValueError:
    answer = {}
for path in answer.get("paths", []):
    best = path.get("bestpath", {})
    if best.get("overall"):
        hop = (path.get("nexthops") or [{}])[0].get("ip", "?")
        localpref = path.get("locPrf", 100)
        med = path.get("metric", 0)
        aspath = path.get("aspath", {}).get("string") or "Local"
        reason = best.get("selectionReason", "?")
        print(f"via {hop}, localpref {localpref}, med {med}, path {aspath}, chosen by {reason}")
        break
else:
    print("none")
'
}
