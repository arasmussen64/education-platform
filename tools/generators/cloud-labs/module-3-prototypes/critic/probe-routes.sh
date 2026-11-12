set -u
ip link add dummy0 type dummy; ip addr add 198.51.100.2/24 dev dummy0; ip link set dummy0 up
ip route add 10.9.0.0/16 via 198.51.100.254
echo "== ip -j route (no -d), hand-made route:"; ip -j route show 10.9.0.0/16
echo "== ip -d -j route:"; ip -d -j route show 10.9.0.0/16
echo "== text:"; ip route show 10.9.0.0/16
mkdir -p /run/frr /var/log/frr; chown frr:frr /run/frr /var/log/frr
/usr/lib/frr/zebra -d -u frr -g frr >/dev/null 2>&1; sleep 1; /usr/lib/frr/staticd -d -u frr -g frr >/dev/null 2>&1; sleep 1
vtysh -c 'configure terminal' -c 'ip route 0.0.0.0/0 198.51.100.254' -c 'end' >/dev/null 2>&1
sleep 2
echo "== FRR show ip route 0.0.0.0/0:"; vtysh -c 'show ip route 0.0.0.0/0' 2>/dev/null | sed -n 1,8p
echo "== kernel default route:"; ip -j route show default
ping -c1 -W1 203.0.113.10 >/dev/null 2>&1; sleep 1; echo "== neighbour:"; ip neigh show 198.51.100.254
