netlab show
on wan tc qdisc show dev dr1; on wan tc qdisc show dev shop
on shop ping -c 4 10.0.6.20
mkdir -p ~/example
wan-set 50mbit 25ms 0%
on shop iperf3 -c 10.0.6.20 -t 6 -f m | tee ~/example/cubic-clean.txt
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 > /dev/null & sleep 4; on shop ss -tni dst 10.0.6.20; wait
wan-set 50mbit 25ms 1%
on shop iperf3 -c 10.0.6.20 -t 6 -f m | tee ~/example/cubic-lossy.txt
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 > /dev/null & sleep 4; on shop ss -tni dst 10.0.6.20; wait
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 -C bbr -f m | tee ~/example/bbr-lossy.txt
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 -C bbr > /dev/null & sleep 4; on shop ss -tni dst 10.0.6.20; wait
on shop sysctl net.ipv4.tcp_available_congestion_control
wan-set 50mbit 50ms 1%
on shop iperf3 -c 10.0.6.20 -t 6 -f m | grep receiver
sleep 1; on shop iperf3 -c 10.0.6.20 -t 6 -C bbr -f m | grep receiver
wan-set 50mbit 25ms 1%
awk '/receiver$/ {printf "%s %.1f\n", FILENAME, $7}' ~/example/cubic-clean.txt ~/example/cubic-lossy.txt ~/example/bbr-lossy.txt
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-congestion.conf
on shop sysctl -p /etc/sysctl.d/60-congestion.conf
on shop iperf3 -c 10.0.6.20 -t 6 -f m | grep receiver
on shop cat /etc/caddy/Caddyfile
on shop ss -tulpn
on office curl -sI https://shop.test/
on office h3get https://shop.test/
on shop timeout 5 tcpdump -nn -i eth0 -c 8 udp port 443 > ~/example/quic-wire.txt &
sleep 1; on office h3get https://shop.test/ > /dev/null; wait
cat ~/example/quic-wire.txt
on office gtlsclient --exit-on-all-streams-close shop.test 443 https://shop.test/ 2> ~/example/quic.log > /dev/null
grep -E 'frm (tx|rx) [0-9]+ (Initial|Handshake) CRYPTO|handshake has completed|STREAM\(0x0[0-9a-f]\) id=0x0 |:status|max_idle_timeout' ~/example/quic.log | sed -E 's/^(I[0-9]+) 0x[0-9a-f]+ /\1 /'
on office curl -so /dev/null -w '%{time_connect} %{time_appconnect} %{time_starttransfer}\n' https://shop.test/ | tee ~/example/rtt.txt
on shop nft insert rule inet filter input udp dport 443 drop
on office h3get https://shop.test/
on office curl -s https://shop.test/
sudo systemctl reload nftables@shop
on office h3get https://shop.test/
