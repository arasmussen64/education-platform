# Wrong: the timers were typed last, once both sessions were already up,
# and saved, but the sessions were never started again. The file is right,
# so the next restart would be too, yet the sessions running now agreed
# their timers when they began: 60 and 180, FRR's defaults.
on edge vtysh << 'EOF' > /dev/null
configure terminal
ip prefix-list OURS seq 5 permit 198.51.100.0/24
ip prefix-list NOT-OURS seq 5 deny 198.51.100.0/24 le 32
ip prefix-list NOT-OURS seq 10 permit 0.0.0.0/0 le 32
route-map TO-ISPS permit 10
 match ip address prefix-list OURS
exit
route-map FROM-ISPA permit 10
 match ip address prefix-list NOT-OURS
 set local-preference 200
exit
route-map FROM-ISPB permit 10
 match ip address prefix-list NOT-OURS
exit
router bgp 65001
 bgp router-id 198.51.100.1
 neighbor 192.0.2.2 remote-as 65010
 neighbor 192.0.2.2 timers connect 5
 neighbor 192.0.2.6 remote-as 65020
 neighbor 192.0.2.6 timers connect 5
 address-family ipv4 unicast
  network 198.51.100.0/24
  neighbor 192.0.2.2 route-map FROM-ISPA in
  neighbor 192.0.2.2 route-map TO-ISPS out
  neighbor 192.0.2.6 route-map FROM-ISPB in
  neighbor 192.0.2.6 route-map TO-ISPS out
end
EOF
# Both sessions up (two lines of the summary say so by their uptime
# column; a session that isn't up shows a state word there instead).
for _ in $(seq 1 40); do
  up=$(on edge vtysh -c 'show bgp summary json' | python3 -c 'import json, sys; print(sum(p.get("state") == "Established" for p in json.load(sys.stdin).get("ipv4Unicast", {}).get("peers", {}).values()))')
  [ "$up" = 2 ] && break
  sleep 1
done
on edge vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 timers bgp 3 9
end
write memory
EOF
