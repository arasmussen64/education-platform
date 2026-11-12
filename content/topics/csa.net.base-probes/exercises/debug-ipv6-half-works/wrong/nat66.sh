# Wrong: the three faults are fixed, and IPv6 is translated too (a NAT66
# masquerade on r1), so web sees r1's address instead of each laptop's.
# (The lab machine's paths to r1's files: sed -i can't replace them from
# inside r1.)
sudo sed -i 's#2001:db8:42::/56#2001:db8:42:a::/64#' /etc/netns/r1/radvd.conf
echo 'net.ipv6.conf.all.forwarding = 1' | on r1 tee -a /etc/sysctl.d/90-forward.conf > /dev/null
sudo sed -i '/meta l4proto ipv6-icmp drop/d' /etc/netns/r1/nftables.conf
printf 'table ip6 nat {\n    chain postrouting {\n        type nat hook postrouting priority srcnat; policy accept;\n        oifname "wan" masquerade\n    }\n}\n' | sudo tee -a /etc/netns/r1/nftables.conf > /dev/null
sudo netlab restart
