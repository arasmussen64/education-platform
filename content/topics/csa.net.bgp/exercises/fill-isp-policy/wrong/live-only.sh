# Wrong: the four values were typed into edge's console instead, and never
# saved: everything works today, and edge's file still has its gaps, so the
# next restart of FRR (or of edge) loses them.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
route-map FROM-ISPA permit 10
 set local-preference 200
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 192.0.2.6 route-map FROM-ISPB in
end
EOF
