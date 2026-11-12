# The reference: shop, the sender, uses BBR for good. Congestion control
# runs where the data is sent from, so it is shop's setting that counts.
# tee writes the line into a file in shop's own /etc/sysctl.d, which shop
# applies at every boot; sysctl -p applies that one file now (the kernel
# loads BBR the first time it is asked for).
echo 'net.ipv4.tcp_congestion_control = bbr' | on shop tee /etc/sysctl.d/60-bbr.conf > /dev/null
on shop sysctl -p /etc/sysctl.d/60-bbr.conf

# Look: the archive's speed now.
archive-push
