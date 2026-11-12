#!/bin/bash
# Runs inside the lab as root: applies one congestion-control variant, then
# runs the "backup job" (one iperf3 connection, the system default congestion
# control, 8 seconds) twice and prints the received rate.
job() {
  iperf3 -c 10.0.6.20 -t 8 -J 2>/dev/null | python3 -c "import json,sys; d=json.load(sys.stdin); e=d['end']; print('%.1f Mbit/s, %d retransmits, cc=%s' % (e['sum_received']['bits_per_second']/1e6, e['sum_sent']['retransmits'], e.get('sender_tcp_congestion','?')))"
}
case "$1" in
  bbr) echo "net.ipv4.tcp_congestion_control = bbr" > /etc/sysctl.d/60-backup.conf
       sysctl -q -p /etc/sysctl.d/60-backup.conf ;;
  bbr-fq) printf "net.core.default_qdisc = fq\nnet.ipv4.tcp_congestion_control = bbr\n" > /etc/sysctl.d/60-backup.conf
       sysctl -q -p /etc/sysctl.d/60-backup.conf
       tc qdisc replace dev eth2 root fq ;;
  receiver-bbr) ip netns exec dr sysctl -qw net.ipv4.tcp_congestion_control=bbr ;;
  none) ;;
esac
for k in 1 2; do echo "$1 run $k: $(job)"; done
