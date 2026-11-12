# Wrong: edge prefers dx1 for its own traffic and asks the cloud to prefer
# dx1 with a lower MED. Microsoft's page names prefix length and AS-path
# prepending for this direction, not MED, and this cloud sets every MED it
# receives to 0, so its two paths stay equal and it shares its traffic over
# both circuits.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX1 permit 10
 match ip address prefix-list OURS
 set metric 50
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set metric 100
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
