# Wrong: the round trips are timed on shop itself, where the site is a
# millisecond away, instead of from the office, 100 ms away. Everything else
# is done.
mkdir -p ~/example
wan-set 50mbit 25ms 0%
on shop iperf3 -c 10.0.6.20 -t 6 -f m > ~/example/cubic-clean.txt
wan-set 50mbit 25ms 1%
on shop iperf3 -c 10.0.6.20 -t 6 -f m > ~/example/cubic-lossy.txt
on shop iperf3 -c 10.0.6.20 -t 6 -C bbr -f m > ~/example/bbr-lossy.txt
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-congestion.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-congestion.conf
on shop timeout 5 tcpdump -nn -i eth0 -c 8 udp port 443 > ~/example/quic-wire.txt 2> /dev/null &
sleep 1; on office h3get https://shop.test/ > /dev/null; wait
on office gtlsclient --exit-on-all-streams-close shop.test 443 https://shop.test/ 2> ~/example/quic.log > /dev/null
on shop curl -so /dev/null --resolve shop.test:443:127.0.0.1 -w '%{time_connect} %{time_appconnect} %{time_starttransfer}\n' https://shop.test/ > ~/example/rtt.txt
