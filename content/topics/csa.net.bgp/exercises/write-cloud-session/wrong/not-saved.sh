# Wrong: the session and its policies are right, but never saved: a
# restart of FRR, or of edge, loses them.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list CLOUD-WEB seq 5 permit 203.0.113.0/24
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD-WEB
exit
route-map TO-CLOUD permit 10
 match ip address prefix-list OURS
exit
router bgp 65001
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-CLOUD in
  neighbor 169.254.30.2 route-map TO-CLOUD out
end
EOF
