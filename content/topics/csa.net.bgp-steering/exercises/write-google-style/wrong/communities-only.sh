# Wrong: the Direct Connect way on a Google-style cloud. depot tags its
# route over ic2 with AWS's high-preference community and over ic1 with the
# low one. Those labels mean something only to AWS: this cloud chooses by
# AS path, origin and MED, all still equal, so it keeps sharing its traffic
# over both circuits.
on depot vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-IC1 permit 10
 match ip address prefix-list OURS
 set community 7224:7100
exit
route-map TO-IC2 permit 10
 match ip address prefix-list OURS
 set community 7224:7300
exit
router bgp 65002
 address-family ipv4 unicast
  neighbor 169.254.50.2 route-map TO-IC1 out
  neighbor 169.254.70.2 route-map TO-IC2 out
end
write memory
EOF
