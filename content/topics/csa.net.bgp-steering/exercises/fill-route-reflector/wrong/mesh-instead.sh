# Wrong: instead of making core a reflector, access is given sessions of its
# own with dc1 and dc2, a full mesh in the making: it works, and every new
# router would need a session with every other one.
sudo sed -i '/^  neighbor 10\.0\.[123]\.2 ___$/d' /etc/netns/core/frr/frr.conf
sudo sed -i 's/^  neighbor 10\.0\.3\.1 ___$/  neighbor 10.0.3.1 next-hop-self/' /etc/netns/dc2/frr/frr.conf
sudo systemctl restart frr@core frr@dc2
on access vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 neighbor 10.0.2.2 remote-as 65001
 neighbor 10.0.2.2 timers connect 5
 neighbor 10.0.3.2 remote-as 65001
 neighbor 10.0.3.2 timers connect 5
end
write memory
EOF
for dc in dc1 dc2; do
  on "$dc" vtysh << 'EOF' > /dev/null
configure terminal
router bgp 65001
 neighbor 10.0.1.2 remote-as 65001
 neighbor 10.0.1.2 timers connect 5
 address-family ipv4 unicast
  neighbor 10.0.1.2 next-hop-self
end
write memory
EOF
done
