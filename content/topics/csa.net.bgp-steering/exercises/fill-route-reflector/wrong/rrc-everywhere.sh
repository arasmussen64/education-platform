# Wrong: core's three gaps are right, but dc2's gap gets the same word,
# route-reflector-client, instead of next-hop-self. dc2's routes from the
# cloud then reach core and access with the cloud's own address on dx2 as
# their next hop, which nothing inside the data centre can reach, so they
# are never used: when dc1's circuit goes, the office has no way out.
sudo sed -i 's/^  neighbor \(10\.0\.[123]\.2\) ___$/  neighbor \1 route-reflector-client/' /etc/netns/core/frr/frr.conf
sudo sed -i 's/^  neighbor 10\.0\.3\.1 ___$/  neighbor 10.0.3.1 route-reflector-client/' /etc/netns/dc2/frr/frr.conf
sudo systemctl restart frr@core frr@dc2
