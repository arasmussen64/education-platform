# Wrong: instead of next-hop-self on dc1, core and access are given routes
# to circuit 1's cable typed into their kernels, so they can reach the cloud's
# address on it. It works until the next boot, which loses them.
on dc2 vtysh << 'EOF' > /dev/null
configure terminal
route-map TO-CLOUD permit 10
 no set community
 set as-path prepend 65001 65001
end
write memory
EOF
on dc1 vtysh << 'EOF' > /dev/null
configure terminal
bfd
 profile CIRCUIT
  receive-interval 300
  transmit-interval 300
 exit
exit
end
write memory
EOF
on core ip route add 169.254.30.0/30 via 10.0.2.2
on access ip route add 169.254.30.0/30 via 10.0.1.1
