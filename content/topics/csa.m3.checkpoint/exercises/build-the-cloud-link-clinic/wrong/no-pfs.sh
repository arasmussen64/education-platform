# Wrong: the ESP proposal has no DH group, so a rekey has no key exchange of its own (no perfect forward secrecy), and the cloud refuses it.
# 1. The tunnel interface, in edge's network file so every boot makes it,
#    then made now by running the same file. Its key, 21, is the mark the
#    connection gives its SAs (any number works, if the two agree).
on edge tee /etc/network/up > /dev/null <<'EOF'
# edge's tunnel interface to the cloud's VPN gateway: a VTI. Key 21 is the
# mark that ties it to the IPsec SA whose mark_in and mark_out are 21.
ip link add vti0 type vti local 198.51.100.40 remote 203.0.113.40 key 21
ip addr add 169.254.21.2/30 dev vti0
ip link set vti0 up
EOF
on edge bash /etc/network/up

# 2. The VPN, from the sheet: IKEv2, the sheet's two proposals and nothing
#    weaker, the pre-shared key for the two identities, one CHILD_SA for
#    everything with the mark 21. It starts when it is loaded, starts again
#    when the cloud closes it or stops answering, and keeps trying however
#    long the cloud takes. The file holds the key, so only root may read it.
on edge tee /etc/swanctl/conf.d/cloud.conf > /dev/null <<'EOF'
connections {
  cloud {
    version = 2
    local_addrs = 198.51.100.40
    remote_addrs = 203.0.113.40
    proposals = aes256-sha256-modp2048
    keyingtries = 0
    dpd_delay = 10s
    local {
      auth = psk
      id = 198.51.100.40
    }
    remote {
      auth = psk
      id = 203.0.113.40
    }
    children {
      cloud-vti {
        local_ts = 0.0.0.0/0
        remote_ts = 0.0.0.0/0
        mark_in = 21
        mark_out = 21
        esp_proposals = aes256gcm16
        start_action = start
        close_action = start
        dpd_action = restart
      }
    }
  }
}
secrets {
  ike-cloud {
    id-1 = 198.51.100.40
    id-2 = 203.0.113.40
    secret = "Fz3kW8nR5tY2bH9qL4vM7cX6"
  }
}
EOF
on edge chmod 600 /etc/swanctl/conf.d/cloud.conf
sudo systemctl restart strongswan@edge

# 3. BGP, two sessions with the cloud's AS 65515: over the circuit (dx) and
#    inside the tunnel. edge announces one route for the data centre: its
#    four /24s, in 10.40 to 10.43, fit in 10.40.0.0/14 (a /15 would hold
#    only 10.40 and 10.41), held in the routing table by a blackhole route
#    so that "network" has it to announce, and dropping what nobody uses.
#    It takes only prefixes inside 10.200.0.0/16 no longer than /24, so
#    never the default route. The circuit wins both ways: local preference
#    200 on what arrives over dx (edge's own choice, for its traffic out),
#    and over the VPN the summary goes with edge's AS twice more, a longer
#    path, which the cloud's choice of the shortest passes over (its
#    traffic back). The route maps come first, then the sessions that use
#    them. Saved with write memory.
on edge vtysh <<'EOF'
configure terminal
ip route 10.40.0.0/14 blackhole
ip prefix-list DC seq 5 permit 10.40.0.0/14
ip prefix-list CLOUD-NETS seq 5 permit 10.200.0.0/16 le 24
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
 set as-path prepend 65040 65040
exit
router bgp 65040
 bgp router-id 10.40.0.1
 timers bgp 3 9
 neighbor 169.254.30.2 remote-as 65515
 neighbor 169.254.30.2 description dx, the private circuit
 neighbor 169.254.30.2 timers connect 5
 neighbor 169.254.21.1 remote-as 65515
 neighbor 169.254.21.1 description vpn, the backup
 neighbor 169.254.21.1 timers connect 5
 address-family ipv4 unicast
  network 10.40.0.0/14
  neighbor 169.254.30.2 route-map FROM-DX in
  neighbor 169.254.30.2 route-map TO-DX out
  neighbor 169.254.21.1 route-map FROM-VPN in
  neighbor 169.254.21.1 route-map TO-VPN out
end
write memory
EOF
