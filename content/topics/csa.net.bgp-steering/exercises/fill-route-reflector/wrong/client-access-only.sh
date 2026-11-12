# Wrong: the two words are mixed up the other way in core's file. access is
# made a route-reflector client, but dc1 and dc2 get next-hop-self, which on
# core changes nothing. Every traffic check passes: a reflector passes a
# client's routes to everyone and everyone's routes to its clients (RFC
# 4456), so access hears dc1's and dc2's ways to the cloud and they hear the
# office's networks. But dc1 and dc2 aren't clients, as gaps 2 and 3 asked:
# core never passes either of them the other's routes.
sudo sed -i -e 's/^  neighbor 10\.0\.1\.2 ___$/  neighbor 10.0.1.2 route-reflector-client/' \
  -e 's/^  neighbor \(10\.0\.[23]\.2\) ___$/  neighbor \1 next-hop-self/' /etc/netns/core/frr/frr.conf
sudo sed -i 's/^  neighbor 10\.0\.3\.1 ___$/  neighbor 10.0.3.1 next-hop-self/' /etc/netns/dc2/frr/frr.conf
sudo systemctl restart frr@core frr@dc2
