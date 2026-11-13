# Wrong: the tunnel is started by hand, and nothing in edge's files starts it at boot.
# 1. The tunnel interface, in edge's network file so every boot makes it,
#    then made now by running the same file. Its key, 62, is the mark the
#    connection gives its SAs (any number works, if the two agree).
on edge tee /etc/network/up > /dev/null <<'EOF'
# edge's tunnel interface to the cloud's VPN gateway: a VTI. Key 62 is the
# mark that ties it to the IPsec SA whose mark_in and mark_out are 62.
ip link add vti0 type vti local 198.51.100.20 remote 203.0.113.20 key 62
ip addr add 169.254.62.2/30 dev vti0
ip link set vti0 up
EOF
on edge bash /etc/network/up

# 2. The VPN, from the sheet: IKEv2, the sheet's two proposals and nothing
#    weaker, the pre-shared key for the two identities, one CHILD_SA for
#    everything with the mark 62. It starts when it is loaded, starts again
#    when the cloud closes it or stops answering, and keeps trying however
#    long the cloud takes. The file holds the key, so only root may read it.
on edge tee /etc/swanctl/conf.d/cloud.conf > /dev/null <<'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.20
    remote_addrs = 203.0.113.20
    proposals = aes256-sha256-ecp256
    keyingtries = 0
    dpd_delay = 10s
    local {
      auth = psk
      id = 198.51.100.20
    }
    remote {
      auth = psk
      id = 203.0.113.20
    }
    children {
      cloud-vti {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        mark_in = 62
        mark_out = 62
        esp_proposals = aes256gcm16-ecp256
        start_action = none
        close_action = start
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-cloud {
    id-1 = 198.51.100.20
    id-2 = 203.0.113.20
    secret = "Qe7rT2wZ9pK4mN8vB3xL6cJ5"
  }
}
EOF
on edge chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl restart strongswan@edge
sleep 2
on edge swanctl --initiate --child cloud-vti

# 3. BGP, two sessions with the cloud's AS 64512: over the circuit (dx) and
#    inside the tunnel. edge announces one route for the data centre: its
#    three /24s, 10.20.0.0 to 10.20.2.255, fit in 10.20.0.0/22 (a /23
#    would hold only two), held in the routing table by a blackhole route
#    so that "network" has it to announce, and dropping what nobody uses.
#    It takes only prefixes inside 10.100.0.0/16 no longer than /24, so
#    never the default route. The circuit wins both ways: local preference
#    200 on what arrives over dx (edge's own choice, for its traffic out),
#    and over the VPN the summary goes with edge's AS twice more, a longer
#    path, which the cloud's choice of the shortest passes over (its
#    traffic back). The route maps come first, then the sessions that use
#    them. Saved with write memory.
on edge vtysh <<'EOF'
configure terminal
ip route 10.20.0.0/22 blackhole
ip prefix-list DC seq 5 permit 10.20.0.0/22
ip prefix-list CLOUD-NETS seq 5 permit 10.100.0.0/16 le 24
route-map FROM-DX permit 10
 match ip address prefix-list CLOUD-NETS
 set local-preference 200
exit
route-map FROM-VPN permit 10
 match ip address prefix-list CLOUD-NETS
exit
route-map TO-DX permit 10
 match ip address prefix-list DC
exit
route-map TO-VPN permit 10
 match ip address prefix-list DC
 set as-path prepend 65020 65020
exit
router bgp 65020
 bgp router-id 10.20.0.1
 timers bgp 3 9
 neighbor 169.254.100.2 remote-as 64512
 neighbor 169.254.100.2 description dx, the private circuit
 neighbor 169.254.100.2 timers connect 5
 neighbor 169.254.62.1 remote-as 64512
 neighbor 169.254.62.1 description vpn, the backup
 neighbor 169.254.62.1 timers connect 5
 address-family ipv4 unicast
  network 10.20.0.0/22
  neighbor 169.254.100.2 route-map FROM-DX in
  neighbor 169.254.100.2 route-map TO-DX out
  neighbor 169.254.62.1 route-map FROM-VPN in
  neighbor 169.254.62.1 route-map TO-VPN out
end
write memory
EOF
