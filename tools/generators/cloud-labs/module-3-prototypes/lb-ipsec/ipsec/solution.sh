# Prototype solution for the build: a route-based tunnel to the cloud with BGP over it.
# 1. The tunnel interface, made at every boot by a small unit.
sudo tee /etc/systemd/system/vti0.service > /dev/null <<'UNIT'
[Unit]
Description=vti0: the route-based tunnel to the cloud
After=lab-network.service
Before=strongswan.service frr.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42
ExecStart=/usr/sbin/ip addr add 169.254.21.2/30 dev vti0
ExecStart=/usr/sbin/ip link set vti0 up mtu 1436
ExecStart=/usr/sbin/sysctl -w net.ipv4.conf.vti0.disable_policy=1
ExecStop=/usr/sbin/ip link del vti0
[Install]
WantedBy=multi-user.target
UNIT
sudo systemctl daemon-reload && sudo systemctl enable --now vti0
# 2. IKE and ESP: the connection to the cloud's gateway.
sudo tee /etc/swanctl/conf.d/cloud.conf > /dev/null <<'CONF'
connections {
    cloud {
        version = 2
        local_addrs = 198.51.100.10
        remote_addrs = 203.0.113.10
        proposals = aes256-sha256-modp2048
        dpd_delay = 10s
        keyingtries = 0
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
                esp_proposals = aes256gcm16-modp2048
                mark_in = 42
                mark_out = 42
                start_action = start
                close_action = start
                dpd_action = restart
            }
        }
    }
}
secrets {
    ike-cloud {
        id = 203.0.113.10
        secret = "lab-psk-3f9c2a7d1e"
    }
}
CONF
sudo chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl enable --now strongswan
# 3. BGP over the tunnel.
sudo sed -i 's/^bgpd=no/bgpd=yes/' /etc/frr/daemons
sudo tee /etc/frr/frr.conf > /dev/null <<'FRR'
frr defaults traditional
hostname lab
!
ip prefix-list OFFICE seq 5 permit 192.168.10.0/24
ip prefix-list CLOUD seq 5 permit 10.0.0.0/8 le 24
route-map TO-CLOUD permit 10
 match ip address prefix-list OFFICE
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD
!
router bgp 65010
 bgp router-id 198.51.100.10
 neighbor 169.254.21.1 remote-as 64512
 neighbor 169.254.21.1 timers 10 30
 address-family ipv4 unicast
  network 192.168.10.0/24
  neighbor 169.254.21.1 route-map TO-CLOUD out
  neighbor 169.254.21.1 route-map FROM-CLOUD in
 exit-address-family
!
FRR
sudo systemctl enable --now frr
