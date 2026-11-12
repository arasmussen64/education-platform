# Wrong: dc2 prepends and dc1's BFD is fixed, but dc1 still passes the
# cloud's routes to core with the cloud's own address as their next hop,
# which nothing inside the data centre can reach, so the data centre's
# traffic still leaves through dc2.
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
