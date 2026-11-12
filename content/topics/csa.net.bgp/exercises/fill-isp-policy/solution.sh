# The reference: edge's file with its four gaps filled, then FRR on edge
# restarted so that it loads the file. "on edge tee FILE << 'EOF'" writes
# the lines up to EOF into the file on edge, as root there; in the lab,
# nano does the same job by hand.
#   - ISP B's routes go through FROM-ISPB, which filters like FROM-ISPA but
#     leaves the preference at the default, so ISP A's routes win;
#   - OURS holds the one prefix edge announces, the shop's 198.51.100.0/24;
#   - NOT-OURS's first line refuses the shop's prefix "le 32": the prefix and
#     every longer one inside it, down to single addresses;
#   - FROM-ISPA gives ISP A's routes local preference 200, above the
#     default 100.
on edge tee /etc/frr/frr.conf > /dev/null << 'EOF'
frr version 8.4.4
frr defaults traditional
hostname edge
log syslog informational
service integrated-vtysh-config
!
router bgp 65001
 bgp router-id 198.51.100.1
 timers bgp 3 9
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 timers connect 5
 neighbor 192.0.2.6 remote-as 65020
 neighbor 192.0.2.6 timers connect 5
 !
 address-family ipv4 unicast
  network 198.51.100.0/24
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.2 route-map TO-ISPS out
  neighbor 192.0.2.6 route-map FROM-ISPB in
  neighbor 192.0.2.6 route-map TO-ISPS out
 exit-address-family
exit
!
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
!
route-map TO-ISPS permit 10
 match ip address prefix-list OURS
exit
!
route-map FROM-ISPA permit 10
 match ip address prefix-list NOT-OURS
 set local-preference 200
exit
!
route-map FROM-ISPB permit 10
 match ip address prefix-list NOT-OURS
exit
!
EOF
sudo systemctl restart frr@edge
# Look, once edge's kernel sends the cloud's traffic to ISP A (the sessions
# take a few seconds to come back after the restart).
for _ in $(seq 1 30); do on edge ip route get 203.0.113.10 | grep 'via 192.0.2.2' > /dev/null && break; sleep 1; done
on edge vtysh -c 'show bgp ipv4 unicast'
