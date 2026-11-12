# Wrong: fw lets UDP 443 through with a live rule only (nft add rule), so the
# next boot loads the old file again. BBR is set properly.
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf
on fw nft add rule inet filter forward iifname '"isp"' oifname '"shop"' ip daddr 203.0.113.10 udp dport 443 accept
