# Wrong: the tunnel is up, but the cloud's network is a static route into
# it instead of one learned over BGP, so nothing tells either side when the
# other's networks change (and the cloud never learns the shop's).
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
on vpn-a vtysh -c 'configure terminal' -c 'ip route 10.2.0.0/24 169.254.10.2' -c 'end' -c 'write memory'
on host-a ping -c 2 -W 1 10.2.0.10 || true
