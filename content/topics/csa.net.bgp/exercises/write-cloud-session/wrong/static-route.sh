# Wrong: the session is up with a safe export, but it accepts nothing,
# and the cloud's web servers' network is a static route through the
# private link instead: it works until the link changes, and nothing
# the cloud says about it is ever heard.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-CLOUD deny 10
exit
route-map TO-CLOUD permit 10
 match ip address prefix-list OURS
exit
ip route 203.0.113.0/24 169.254.30.2
router bgp 65001
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-CLOUD in
  neighbor 169.254.30.2 route-map TO-CLOUD out
end
write memory
EOF
