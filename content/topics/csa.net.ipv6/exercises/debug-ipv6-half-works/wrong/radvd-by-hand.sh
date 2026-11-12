# Wrong: forwarding and the firewall are fixed in r1's files, but instead
# of fixing r1's /etc/radvd.conf, a second radvd is started by hand on r1
# with a file of its own that advertises the right /64. The laptops
# configure themselves, and the next boot brings back only radvd@r1, which
# still advertises the /56.
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
sudo netlab restart
printf 'interface lan {\n    AdvSendAdvert on;\n    prefix 2001:db8:42:a::/64 {\n        AdvOnLink on;\n        AdvAutonomous on;\n    };\n};\n' > /tmp/radvd-by-hand.conf
on r1 radvd -C /tmp/radvd-by-hand.conf -p /tmp/radvd-by-hand.pid
sleep 3
