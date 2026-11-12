# The reference: core's and dc2's files with their four gaps filled, then FRR
# restarted on both so that each loads its file. "on core tee FILE << 'EOF'"
# writes the lines up to EOF into the file on core, as root there; in the
# lab, nano does the same job by hand.
#   - Gaps 1 to 3: core treats access, dc1 and dc2 as route-reflector
#     clients, so it passes each one's routes on to the others, which plain
#     iBGP never does.
#   - Gap 4: dc2 tells core "send traffic for what I learned from the cloud
#     to me" (next-hop-self), as dc1 already does; otherwise the routes keep
#     the cloud's own address on dx2 as their next hop, which nothing inside
#     the data centre can reach.
on core tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname core
log syslog informational
service integrated-vtysh-config
!
router bgp 65001
 bgp router-id 10.0.1.1
 bgp bestpath compare-routerid
 timers bgp 3 9
 neighbor 10.0.1.2 remote-as 65001
 neighbor 10.0.1.2 description access
 neighbor 10.0.1.2 timers connect 5
 neighbor 10.0.2.2 remote-as 65001
 neighbor 10.0.2.2 description dc1
 neighbor 10.0.2.2 timers connect 5
 neighbor 10.0.3.2 remote-as 65001
 neighbor 10.0.3.2 description dc2
 neighbor 10.0.3.2 timers connect 5
 !
 address-family ipv4 unicast
  neighbor 10.0.1.2 route-reflector-client
  neighbor 10.0.2.2 route-reflector-client
  neighbor 10.0.3.2 route-reflector-client
 exit-address-family
exit
!
EOF
on dc2 tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname dc2
log syslog informational
service integrated-vtysh-config
!
ip route 10.0.0.0/16 10.0.3.1 core
!
router bgp 65001
 bgp router-id 169.254.20.1
 bgp bestpath compare-routerid
 timers bgp 3 9
 neighbor 10.0.3.1 remote-as 65001
 neighbor 10.0.3.1 description core
 neighbor 10.0.3.1 timers connect 5
 neighbor 169.254.20.2 remote-as 64600
 neighbor 169.254.20.2 description dx2
 neighbor 169.254.20.2 bfd
 neighbor 169.254.20.2 timers connect 5
 !
 address-family ipv4 unicast
  aggregate-address 10.1.0.0/22 summary-only
  neighbor 10.0.3.1 next-hop-self
  neighbor 169.254.20.2 route-map FROM-CLOUD in
  neighbor 169.254.20.2 route-map TO-CLOUD out
 exit-address-family
exit
!
ip prefix-list DC seq 5 permit 10.1.0.0/22
ip prefix-list CLOUD seq 5 permit 10.100.0.0/16
!
route-map FROM-CLOUD permit 10
 match ip address prefix-list CLOUD
exit
!
route-map TO-CLOUD permit 10
 match ip address prefix-list DC
 set as-path prepend 65001 65001
exit
!
EOF
sudo systemctl restart frr@core frr@dc2
# Look, once access has the cloud's route again (the sessions take a few
# seconds to come back after the restart): core's three clients, and
# access's way to the cloud, through dc1, with the marks a reflector adds.
for _ in $(seq 1 30); do on access ip route show 10.100.0.0/16 | grep via > /dev/null && break; sleep 1; done
on core vtysh -c 'show bgp summary'
on access vtysh -c 'show bgp ipv4 unicast 10.100.0.0/16'
