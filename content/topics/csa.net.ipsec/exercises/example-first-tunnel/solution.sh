cat /srv/provider/vpn-config.txt
on vpn ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42
on vpn ip addr add 169.254.21.2/30 dev vti0
on vpn ip link set vti0 up
on vpn ip -d link show vti0
on vpn tee /etc/swanctl/conf.d/cloud.conf > /dev/null << 'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.10
    remote_addrs = 203.0.113.10
    proposals = aes256-sha256-modp2048
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
on vpn swanctl --load-all
on vpn swanctl --initiate --child cloud-vti
on vpn swanctl --list-sas
mkdir -p ~/example
on vpn swanctl --list-sas | grep MODP > ~/example/ike.txt
on internet timeout 6 tcpdump -nn -i vpn 'udp port 500 or udp port 4500' &
sleep 1
on vpn swanctl --terminate --ike cloud > /dev/null
on vpn swanctl --initiate --child cloud-vti > /dev/null
wait
on vpn sed -i 's/rT7qV2mX9pL4wZ8kN3bF6hJ1/rT7qV2mX9pL4wZ8kN3bF6hJ2/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
on vpn swanctl --terminate --ike cloud > /dev/null
on vpn swanctl --initiate --child cloud-vti
cloud-vpn-log 12
cloud-vpn-log 40 | grep 'MAC mismatched' > ~/example/auth-error.txt
on vpn sed -i 's/rT7qV2mX9pL4wZ8kN3bF6hJ2/rT7qV2mX9pL4wZ8kN3bF6hJ1/' /etc/swanctl/conf.d/cloud.conf
on vpn swanctl --load-all > /dev/null
on vpn swanctl --initiate --child cloud-vti > /dev/null
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
sleep 8
on vpn vtysh -c 'show bgp summary'
looking-glass cloud 'show bgp ipv4 unicast neighbors 169.254.21.2 advertised-routes'
on vpn ip route show proto bgp
on vpn ip route show proto bgp > ~/example/learned.txt
on office curl -s http://10.20.1.10/
on office curl -s -o /dev/null -w '%{size_download} bytes\n' http://10.20.1.10/report.txt
on vpn ip -s xfrm state | grep -A 1 'lifetime current'
on vpn tee /etc/network/up > /dev/null << 'EOF'
# vpn's tunnel interface to the provider: a VTI. Key 42 is the mark that
# ties it to the IPsec SA whose mark_in and mark_out are 42.
ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42
ip addr add 169.254.21.2/30 dev vti0
ip link set vti0 up
EOF
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
on vpn swanctl --load-all > /dev/null
on vpn vtysh -c 'write memory'
sudo netlab restart
sleep 12
on vpn swanctl --list-sas
on office curl -s http://10.20.1.10/
cloud-maintenance
sleep 12
cloud-vpn-status
on office curl -s http://10.20.1.10/
