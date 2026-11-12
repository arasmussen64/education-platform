#!/bin/bash
# trial.sh CC SECONDS -> prints Mbit/s received and retransmits
CC=$1; T=${2:-10}
iperf3 -c 10.0.6.20 -t $T -C $CC -J 2>/dev/null > /tmp/ip.json
python3 - <<'PY'
import json
d = json.load(open("/tmp/ip.json"))
e = d["end"]
print("%6.2f Mbit/s received, %5d retransmits, cc=%s" % (e["sum_received"]["bits_per_second"]/1e6, e["sum_sent"].get("retransmits", -1), d["start"]["test_start"].get("congestion", "?") if "congestion" in d["start"]["test_start"] else d["end"].get("sender_tcp_congestion","?")))
PY
