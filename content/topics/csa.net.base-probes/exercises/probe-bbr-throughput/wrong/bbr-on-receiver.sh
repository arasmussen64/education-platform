# Wrong: BBR is set for good on dr1, the receiver, and shop, the sender,
# still uses CUBIC. Congestion control runs where the data is sent from,
# so the archive is as slow as before.
echo 'net.ipv4.tcp_congestion_control = bbr' | on dr1 tee /etc/sysctl.d/60-bbr.conf > /dev/null
on dr1 sysctl -p /etc/sysctl.d/60-bbr.conf
