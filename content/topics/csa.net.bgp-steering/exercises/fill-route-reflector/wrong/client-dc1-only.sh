# Wrong: the two words are mixed up in core's file. dc1 is made a
# route-reflector client, but access and dc2 get next-hop-self, which on
# core changes nothing. A reflector passes a client's routes to everyone, so
# access still learns dc1's way to the cloud; but routes between two
# non-clients, access and dc2, are never passed on, so when dc1's circuit
# goes, access has no way out through dc2.
sudo sed -i -e 's/^  neighbor 10\.0\.2\.2 ___$/  neighbor 10.0.2.2 route-reflector-client/' \
  -e 's/^  neighbor \(10\.0\.[13]\.2\) ___$/  neighbor \1 next-hop-self/' /etc/netns/core/frr/frr.conf
sudo sed -i 's/^  neighbor 10\.0\.3\.1 ___$/  neighbor 10.0.3.1 next-hop-self/' /etc/netns/dc2/frr/frr.conf
sudo systemctl restart frr@core frr@dc2
