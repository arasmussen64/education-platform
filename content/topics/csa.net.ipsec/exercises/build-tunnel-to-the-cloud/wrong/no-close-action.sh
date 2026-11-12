# Wrong: the tunnel starts at boot, but nothing brings it back when the
# provider closes it for maintenance (close_action = none, the default).
on vpn tee /etc/network/up > /dev/null << 'EOF'
ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 44
ip addr add 169.254.44.2/30 dev vti0
ip link set vti0 up
EOF
on vpn bash /etc/network/up
on vpn tee /etc/swanctl/conf.d/cloud.conf > /dev/null << 'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.10
    remote_addrs = 203.0.113.10
    proposals = aes256-sha384-ecp384
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
        mark_in = 44
        mark_out = 44
        esp_proposals = aes256gcm16-ecp384
        start_action = start
        close_action = none
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-cloud {
    id-1 = 198.51.100.10
    id-2 = 203.0.113.10
    secret = "Hn4wB8vK2mQ9sX6tR3pL7zD5"
  }
}
EOF
on vpn chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl restart strongswan@vpn
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
 neighbor 169.254.44.1 remote-as 64600
 neighbor 169.254.44.1 timers connect 5
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.44.1 route-map FROM-CLOUD in
  neighbor 169.254.44.1 route-map TO-CLOUD out
end
write memory
EOF
