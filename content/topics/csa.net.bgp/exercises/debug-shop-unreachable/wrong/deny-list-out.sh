# Wrong: the inbound route maps and the announcement are fixed, and the
# route map toward ISP B, instead of getting back its match on OURS, now
# refuses the two routes ISP B complained about. ISP B receives only the
# shop's prefix today; the next route ISP A sends goes straight on to it.
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 address-family ipv4 unicast
  no network 198.51.100.0/25
  network 198.51.100.0/24
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.6 route-map FROM-ISPB in
exit
exit
ip prefix-list LEAKED seq 5 permit 10.10.0.0/16
ip prefix-list LEAKED seq 10 permit 203.0.113.0/24
route-map TO-ISPB deny 5
 match ip address prefix-list LEAKED
end
write memory
EOF
# The route map changed while in use, so wait (about 5 seconds) until ISP B
# has only the shop's prefix from edge, as a learner would before checking.
for _ in $(seq 1 30); do
  [ "$(looking-glass ispb 'show bgp ipv4 unicast neighbors 192.0.2.5 routes' | grep -c '^\*>')" = 1 ] && break
  sleep 1
done
