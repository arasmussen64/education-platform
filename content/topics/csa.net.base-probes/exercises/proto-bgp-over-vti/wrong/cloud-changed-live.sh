# Wrong: vpn-a takes everything the cloud offers, and instead of a filter
# on vpn-a, the prefix outside the cloud's range was taken out of vpn-b's
# announcements live, in vtysh on vpn-b, which isn't the learner's router.
on vpn-a tee /etc/swanctl/conf.d/cloud.conf > /dev/null << 'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.2
    remote_addrs = 203.0.113.2
    proposals = aes256-sha256-modp2048
    dpd_delay = 10s
    keyingtries = 0
    local {
      auth = psk
      id = 198.51.100.2
    }
    remote {
      auth = psk
      id = 203.0.113.2
    }
    children {
      cloud-vti {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        mode = tunnel
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
    id-1 = 198.51.100.2
    id-2 = 203.0.113.2
    secret = "lab-shared-secret-42"
  }
}
EOF
on vpn-a chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl restart strongswan@vpn-a
on vpn-a vtysh \
  -c 'configure terminal' \
  -c 'ip prefix-list SHOP seq 5 permit 10.1.0.0/24' \
  -c 'route-map TO-CLOUD permit 10' -c 'match ip address prefix-list SHOP' -c 'exit' \
  -c 'route-map FROM-CLOUD permit 10' -c 'exit' \
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
for _ in $(seq 1 60); do on vpn-a vtysh -c 'show ip route 10.2.0.0/24' 2> /dev/null | grep -q bgp && break; sleep 1; done
on vpn-b vtysh -c 'configure terminal' -c 'router bgp 64512' \
  -c 'address-family ipv4 unicast' -c 'no network 172.16.9.0/24' -c 'end'
# Long enough for vpn-b to withdraw it from vpn-a.
sleep 5
