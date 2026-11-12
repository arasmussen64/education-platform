# The reference fill-in. "on MACHINE COMMAND" runs a command on a machine;
# tee FILE <<'EOF' writes the lines up to EOF into FILE, which in the lab
# you'd do with nano (sed -i can't replace a machine's own file that sits
# straight in /etc, like /etc/radvd.conf).
#
# radvd: advertise on r1's side of the office's switch, lan; send the
# advertisements; and the prefix is subnet 1a (hex) of the site's /48, as
# a /64, the only length the laptops build addresses from.
on r1 tee /etc/radvd.conf > /dev/null << 'EOF'
# r1's router advertisements on the office LAN: the prefix the laptops
# make their own IPv6 addresses from.
interface lan {
    AdvSendAdvert on;
    prefix 2001:db8:77:1a::/64 {
        AdvOnLink on;
        AdvAutonomous on;
    };
};
EOF
# Forwarding: 1 switches it on. The file is applied at every boot.
on r1 tee /etc/sysctl.d/90-forward.conf > /dev/null << 'EOF'
# r1 forwards the office's traffic, in both families.
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1
EOF
# radvd@r1 failed at boot on the file with gaps, again and again, and
# systemd stops trying for a few seconds after five failures; reset-failed
# clears that, so the rebuild can start it at once.
sudo systemctl reset-failed radvd@r1
# Build the network again from the files, as a reboot would.
sudo netlab restart
# Look: wait for h1's own address, then ask web which address it sees.
for _ in $(seq 1 10); do
  on h1 ip -6 addr show dev eth0 scope global | grep dynamic > /dev/null && break
  sleep 1
done
on h1 ip -6 addr show dev eth0
on h1 ip -6 route
on h1 nc -6 -w 3 2001:db8:80::80 8080 < /dev/null
