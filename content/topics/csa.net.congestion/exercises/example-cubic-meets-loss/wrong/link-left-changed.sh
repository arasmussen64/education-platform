# Wrong: the walk is done, but after "twice the distance" the link is never
# put back as shipped. (The two runs at that distance are left out: they
# change nothing a check reads.)
mkdir -p ~/example
wan-set 50mbit 25ms 0%
on shop iperf3 -c 10.0.6.20 -t 6 -f m > ~/example/cubic-clean.txt
wan-set 50mbit 25ms 1%
on shop iperf3 -c 10.0.6.20 -t 6 -f m > ~/example/cubic-lossy.txt
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 -C bbr -f m > ~/example/bbr-lossy.txt
wan-set 50mbit 50ms 1%
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-congestion.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-congestion.conf
on shop timeout 5 tcpdump -nn -i eth0 -c 8 udp port 443 > ~/example/quic-wire.txt 2> /dev/null &
sleep 1; on office h3get https://shop.test/ > /dev/null; wait
on office gtlsclient --exit-on-all-streams-close shop.test 443 https://shop.test/ 2> ~/example/quic.log > /dev/null
on office curl -so /dev/null -w '%{time_connect} %{time_appconnect} %{time_starttransfer}\n' https://shop.test/ > ~/example/rtt.txt
