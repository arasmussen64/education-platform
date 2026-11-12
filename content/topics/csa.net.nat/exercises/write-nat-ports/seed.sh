#!/bin/bash
# The scenery of "NAT ports": an empty ~/bin for the script, and a saved
# conntrack -L listing from a gateway at lunchtime to try it on
# (constructed, in conntrack 1.4.8's real format as captured in the NAT
# labs on 2026-11-12, saved with its error stream, so conntrack's own count
# line is there too).
set -euo pipefail
home=/home/learner
mkdir -p "$home/bin" "$home/listings"
cat > "$home/listings/lunch.txt" << 'EOF'
udp      17 131 src=10.1.0.20 dst=203.0.113.53 sport=51294 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=33759 mark=0 use=1
tcp      6 75 TIME_WAIT src=10.1.0.10 dst=203.0.113.10 sport=33664 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=29167 [ASSURED] mark=0 use=1
icmp     1 21 src=10.1.0.10 dst=203.0.113.53 type=8 code=0 id=5651 src=203.0.113.53 dst=198.51.100.2 type=0 code=0 id=5651 mark=0 use=1
tcp      6 34 CLOSE_WAIT src=10.1.0.11 dst=203.0.113.10 sport=57597 dport=80 src=203.0.113.10 dst=198.51.100.2 sport=80 dport=28352 [ASSURED] mark=0 use=1
tcp      6 56 SYN_SENT src=10.1.0.10 dst=203.0.113.10 sport=47901 dport=443 [UNREPLIED] src=203.0.113.10 dst=198.51.100.2 sport=443 dport=51255 mark=0 use=1
tcp      6 98 SYN_SENT src=10.1.0.10 dst=203.0.113.10 sport=44333 dport=443 [UNREPLIED] src=203.0.113.10 dst=198.51.100.2 sport=443 dport=9413 mark=0 use=1
udp      17 77 src=10.1.0.11 dst=203.0.113.53 sport=40877 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=26027 [ASSURED] mark=0 use=1
tcp      6 431696 ESTABLISHED src=10.1.0.11 dst=203.0.113.10 sport=42818 dport=80 src=203.0.113.10 dst=198.51.100.2 sport=80 dport=58996 [ASSURED] mark=0 use=1
udp      17 4 src=10.1.0.11 dst=203.0.113.53 sport=37079 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=54498 mark=0 use=1
tcp      6 43 CLOSE_WAIT src=10.1.0.10 dst=203.0.113.10 sport=44739 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=50771 [ASSURED] mark=0 use=1
udp      17 125 src=10.1.0.10 dst=203.0.113.53 sport=44784 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=61142 [ASSURED] mark=0 use=1
tcp      6 431713 ESTABLISHED src=10.1.0.20 dst=203.0.113.10 sport=41705 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=23156 [ASSURED] mark=0 use=1
tcp      6 22 TIME_WAIT src=10.1.0.20 dst=203.0.113.10 sport=44373 dport=80 src=203.0.113.10 dst=198.51.100.2 sport=80 dport=25575 [ASSURED] mark=0 use=1
udp      17 38 src=10.1.0.10 dst=203.0.113.53 sport=39414 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=28881 [ASSURED] mark=0 use=1
udp      17 129 src=10.1.0.20 dst=203.0.113.53 sport=35399 dport=53 [UNREPLIED] src=203.0.113.53 dst=198.51.100.2 sport=53 dport=16595 mark=0 use=1
tcp      6 87 SYN_SENT src=10.1.0.20 dst=203.0.113.10 sport=35697 dport=443 [UNREPLIED] src=203.0.113.10 dst=198.51.100.2 sport=443 dport=49909 mark=0 use=1
udp      17 145 src=10.1.0.11 dst=203.0.113.53 sport=53481 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=27982 [ASSURED] mark=0 use=1
tcp      6 431757 ESTABLISHED src=10.1.0.20 dst=203.0.113.10 sport=36527 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=22224 [ASSURED] mark=0 use=1
tcp      6 5 CLOSE_WAIT src=10.1.0.10 dst=203.0.113.10 sport=37295 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=23085 [ASSURED] mark=0 use=1
tcp      6 67 SYN_SENT src=10.1.0.10 dst=203.0.113.10 sport=57079 dport=443 [UNREPLIED] src=203.0.113.10 dst=198.51.100.2 sport=443 dport=59878 mark=0 use=1
tcp      6 39 CLOSE_WAIT src=10.1.0.10 dst=203.0.113.10 sport=33953 dport=80 src=203.0.113.10 dst=198.51.100.2 sport=80 dport=40127 [ASSURED] mark=0 use=1
tcp      6 431954 ESTABLISHED src=10.1.0.10 dst=203.0.113.10 sport=53511 dport=443 src=203.0.113.10 dst=198.51.100.2 sport=443 dport=11441 [ASSURED] mark=0 use=1
tcp      6 37 CLOSE_WAIT src=10.1.0.10 dst=203.0.113.53 sport=60606 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=56998 [ASSURED] mark=0 use=1
udp      17 89 src=10.1.0.20 dst=203.0.113.53 sport=55357 dport=53 src=203.0.113.53 dst=198.51.100.2 sport=53 dport=52937 [ASSURED] mark=0 use=1
conntrack v1.4.8 (conntrack-tools): 24 flow entries have been shown.
EOF
chown -R learner:learner "$home/bin" "$home/listings"
