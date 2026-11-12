# Wrong: a GRE tunnel and BGP over it, but no IPsec: the shop's traffic
# would cross the internet readable by anyone.
# 2. BGP over the tunnel: AS 65001 to the cloud's AS 64512, offering the
#    shop's network and taking only the cloud's. Saved with write memory.
on vpn-a vtysh \
  -c 'configure terminal' \
  -c 'ip prefix-list SHOP seq 5 permit 10.1.0.0/24' \
  -c 'ip prefix-list CLOUD seq 5 permit 10.2.0.0/16 le 24' \
  -c 'route-map TO-CLOUD permit 10' -c 'match ip address prefix-list SHOP' -c 'exit' \
  -c 'route-map FROM-CLOUD permit 10' -c 'match ip address prefix-list CLOUD' -c 'exit' \
  -c 'router bgp 65001' \
  -c 'bgp router-id 198.51.100.2' \
  -c 'timers bgp 3 9' \
  -c 'neighbor 169.254.10.2 remote-as 64512' \
  -c 'neighbor 169.254.10.2 timers connect 5' \
  -c 'address-family ipv4 unicast' \
  -c 'network 10.1.0.0/24' \
  -c 'neighbor 169.254.10.2 route-map FROM-CLOUD in' \
  -c 'neighbor 169.254.10.2 route-map TO-CLOUD out' \
  -c 'end' \
  -c 'write memory'

# 3. Look (allowed to fail in a wrong fix).
on vpn-a swanctl --list-sas || true
on host-a ping -c 2 -W 1 10.2.0.10 || true
