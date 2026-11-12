# Wrong: the AWS way on an Azure-style cloud. edge prefers dx1 for its own
# traffic and tags its route over dx1 with AWS's high-preference community
# and over dx2 with the low one, as it would toward Direct Connect. This
# cloud, like Microsoft's, honours no community you send, so its two paths
# stay equal and it shares its traffic over both circuits.
on edge vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-DX1 permit 10
 match ip address prefix-list CLOUD
 set local-preference 200
exit
route-map TO-DX1 permit 10
 match ip address prefix-list OURS
 set community 7224:7300
exit
route-map TO-DX2 permit 10
 match ip address prefix-list OURS
 set community 7224:7100
exit
router bgp 65001
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-DX1 in
  neighbor 169.254.30.2 route-map TO-DX1 out
  neighbor 169.254.20.2 route-map TO-DX2 out
end
write memory
EOF
