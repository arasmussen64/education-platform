# Wrong: both files are filled in right, but FRR was never restarted on core
# or dc2, so they still run what they loaded at boot, gaps and all.
sudo sed -i 's/^  neighbor \(10\.0\.[123]\.2\) ___$/  neighbor \1 route-reflector-client/' /etc/netns/core/frr/frr.conf
sudo sed -i 's/^  neighbor 10\.0\.3\.1 ___$/  neighbor 10.0.3.1 next-hop-self/' /etc/netns/dc2/frr/frr.conf
