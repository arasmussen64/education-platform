# Wrong: the tunnel and BGP work now, but vti0 was made by hand and never
# written into vpn's network file, and BGP was never saved: the next boot
# has neither.
mkdir -p ~/example
on vpn ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42
on vpn ip addr add 169.254.21.2/30 dev vti0
on vpn ip link set vti0 up
on vpn tee /etc/swanctl/conf.d/cloud.conf > /dev/null << 'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.10
    remote_addrs = 203.0.113.10
    proposals = aes256-sha256-modp2048
    keyingtries = 0
    dpd_delay = 10s
    local {
      auth = psk
      id = 198.51.100.10
    }
    remote {
      auth = psk
      id = 203.0.113.10
    }
    children {
      cloud-vti {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        mark_in = 42
        mark_out = 42
        esp_proposals = aes256gcm16-modp2048
        start_action = start
        close_action = start
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-cloud {
    id-1 = 198.51.100.10
    id-2 = 203.0.113.10
    secret = "rT7qV2mX9pL4wZ8kN3bF6hJ1"
  }
}
EOF
on vpn chmod 600 /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
on vpn swanctl --list-sas | grep MODP > ~/example/ike.txt
on vpn vtysh << 'EOF'
configure terminal
ip prefix-list OFFICE seq 5 permit 192.168.10.0/24
ip prefix-list CLOUD-NETS seq 5 permit 10.0.0.0/8 le 24
route-map TO-CLOUD permit 10
 match ip address prefix-list OFFICE
exit
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD-NETS
exit
router bgp 65010
 bgp router-id 198.51.100.10
 timers bgp 3 9
 neighbor 169.254.21.1 remote-as 64512
 neighbor 169.254.21.1 timers connect 5
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.21.1 route-map FROM-CLOUD in
  neighbor 169.254.21.1 route-map TO-CLOUD out
end
EOF
for _ in $(seq 1 30); do on vpn ip route show proto bgp | grep 10.20.0.0 > /dev/null && break; sleep 1; done
on vpn ip route show proto bgp > ~/example/learned.txt
