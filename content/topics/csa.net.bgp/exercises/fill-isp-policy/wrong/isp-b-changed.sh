# Wrong: edge's third gap is left empty, and instead ISP B's router was
# changed to stop sending its slip, and saved. ISP B's router isn't the
# shop's to change, and the next ISP to send a slip gets in.
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
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24
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
on ispb vtysh -c 'configure terminal' -c 'no route-map TO-SHOP permit 20' -c 'end' -c 'write memory' > /dev/null
