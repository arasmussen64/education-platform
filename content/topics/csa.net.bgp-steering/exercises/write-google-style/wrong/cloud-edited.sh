# Wrong: the cloud's router changed instead of depot's announcements. In
# the cloud's own console, the routes that arrive over ic2 are given a
# higher local preference, so the cloud sends over ic2 alone. The cloud's
# router wasn't the learner's to change, and its choice is now made by
# local preference, not by the MED depot sends.
on cloud vtysh << 'EOF' > /dev/null
configure terminal
route-map FROM-IC2 permit 10
 set local-preference 200
exit
router bgp 64900
 address-family ipv4 unicast
  neighbor 169.254.70.1 route-map FROM-IC2 in
end
EOF
