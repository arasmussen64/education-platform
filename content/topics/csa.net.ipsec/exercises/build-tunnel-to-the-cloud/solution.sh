# The reference: vpn's half of a route-based VPN to the provider, from its
# sheet, with BGP over it. "on vpn tee FILE << 'EOF'" writes the lines up
# to EOF into FILE on vpn, as typing them into nano would.

# 1. The tunnel interface, in vpn's network file so every boot makes it,
#    then made now by running the same file. Its key, 44, is the mark the
#    connection gives its SAs (any number works, if the two agree).
on vpn tee /etc/network/up > /dev/null << 'EOF'
# vpn's tunnel interface to the provider: a VTI. Key 44 is the mark that
# ties it to the IPsec SA whose mark_in and mark_out are 44.
ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 44
ip addr add 169.254.44.2/30 dev vti0
ip link set vti0 up
EOF
on vpn bash /etc/network/up

# 2. The connection, from the sheet: IKEv2, the sheet's two proposals and
#    nothing weaker, the pre-shared key for the two identities, one CHILD_SA
#    for everything with the mark 44. It starts when it is loaded, starts
#    again when the provider closes it or stops answering, and keeps trying
#    however long the provider takes. The file holds the key, so only root
#    may read it.
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

# 3. BGP inside the tunnel: AS 65010 to the provider's AS 64600, sending
#    the office's network and nothing else, taking only prefixes inside
#    10.0.0.0/8 no longer than /24 (so never a default route). Saved.
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

# 4. Look: the tunnel from the provider's side, the session, the route, and
#    the office reaching the app.
for _ in $(seq 1 40); do on office curl -s -m 2 http://10.30.1.10/ && break; sleep 1; done
cloud-vpn-status
on vpn vtysh -c 'show bgp summary'
on vpn ip route show proto bgp
