# Wrong: shop uses BBR, but set live only, with sysctl -w, so the next
# boot puts CUBIC back.
on shop sysctl -w net.ipv4.tcp_congestion_control=bbr
