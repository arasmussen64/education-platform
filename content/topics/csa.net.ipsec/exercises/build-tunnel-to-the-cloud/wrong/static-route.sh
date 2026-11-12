# Wrong: no BGP at all; a static route sends the cloud's network into
# vti0. It works today and never learns the next network the cloud adds,
# and the cloud never learns the office's.
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
    secret = "Hn4wB8vK2mQ9sX6tR3pL7zD5"
  }
}
EOF
on vpn chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl restart strongswan@vpn
on vpn vtysh << 'EOF'
configure terminal
ip route 10.30.0.0/16 169.254.44.1 vti0
end
write memory
EOF
