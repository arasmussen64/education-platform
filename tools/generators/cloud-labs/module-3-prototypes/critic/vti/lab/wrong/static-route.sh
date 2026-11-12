# Wrong: the tunnel is up, but the cloud's network is a static route over
# it instead of one learned over BGP, so nothing tells either side when the
# other's networks change.
# Prototype reference: vpn-a's half of a route-based VPN with BGP over it.
# "on vpn-a COMMAND" runs a command on vpn-a; cat > FILE <<'EOF' writes the
# lines up to EOF into FILE.

# 1. IKE and IPsec: the connection to the cloud's gateway, with a pre-shared
#    key, protecting every GRE packet between the two gateways.
on vpn-a tee /etc/swanctl/conf.d/cloud.conf > /dev/null <<'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.2
    remote_addrs = 203.0.113.2
    proposals = aes256-sha256-modp2048
    dpd_delay = 10s
    local {
      auth = psk
      id = 198.51.100.2
    }
    remote {
      auth = psk
      id = 203.0.113.2
    }
    children {
      cloud-gre {
        local_ts = 198.51.100.2/32[gre]
        remote_ts = 203.0.113.2/32[gre]
        mode = tunnel
        esp_proposals = aes256gcm16-modp2048
        start_action = start
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
# 3. Look (allowed to fail in a wrong fix).
on vpn-a swanctl --list-sas || true
on host-a ping -c 2 -W 1 10.2.0.10 || true
