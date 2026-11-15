# Wrong: the ExpressRoute lab's tool on a Google-style cloud. depot makes
# the path over ic1, the backup, longer by prepending its own AS twice. This
# lab's cloud is one FRR router, so it does move to ic2, by AS path. But
# the rule was MED: on a real Cloud Router in its default mode, AS-path
# length is compared only among the sessions one BGP task holds, and
# Google's page says not to rely on it.
on depot vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-IC1 permit 10
 match ip address prefix-list OURS
 set as-path prepend 65002 65002
exit
router bgp 65002
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
end
write memory
EOF
