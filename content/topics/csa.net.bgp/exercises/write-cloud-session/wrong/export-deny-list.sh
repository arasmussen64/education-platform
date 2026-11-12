# Wrong: the import policy is right, but the export policy refuses the two
# ISP routes edge would pass on today and lets everything else out,
# instead of letting out only the shop's prefix: the next route an ISP
# adds goes on to the cloud.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list CLOUD-WEB seq 5 permit 203.0.113.0/24
ip prefix-list ISP-ROUTES seq 5 permit 10.10.0.0/16
ip prefix-list ISP-ROUTES seq 10 permit 10.20.0.0/16
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD-WEB
exit
route-map TO-CLOUD deny 10
 match ip address prefix-list ISP-ROUTES
exit
route-map TO-CLOUD permit 20
exit
router bgp 65001
 neighbor 169.254.30.2 remote-as 65100
 neighbor 169.254.30.2 timers connect 5
 address-family ipv4 unicast
  neighbor 169.254.30.2 route-map FROM-CLOUD in
  neighbor 169.254.30.2 route-map TO-CLOUD out
end
write memory
EOF
