# Wrong: the link's delay is taken away live, so even without window
# scaling one window per (now tiny) round trip is fast. The link is
# scenery, and edge still strips the option. dr's buffers and app's
# keepalive are fixed properly.
on wan tc qdisc change dev dr root netem rate 50mbit delay 1ms limit 2000
on wan tc qdisc change dev edge root netem delay 1ms limit 2000
echo 'net.ipv4.tcp_rmem = 4096 131072 6291456' | on dr tee /etc/sysctl.d/60-tuning.conf > /dev/null
on dr sysctl -p /etc/sysctl.d/60-tuning.conf > /dev/null
sudo sed -i '/tcp_keepalive_time/d' /etc/netns/app/sysctl.d/99-vendor-tuning.conf
on app sysctl -p /etc/sysctl.d/50-repl.conf > /dev/null
sudo systemctl restart repl-agent@app
