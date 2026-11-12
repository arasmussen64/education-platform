# Wrong: the connection's gaps filled and the service enabled, but vti0
# typed by hand instead of filling in the network file, whose gaps stay: the
# next boot has no vti0.
on vpn sed -i 's/keyingtries = ___/keyingtries = 0/; s/start_action = ___/start_action = start/; s/close_action = ___/close_action = start/; s/dpd_action = ___/dpd_action = restart/' /etc/swanctl/conf.d/cloud.conf
on vpn ip link add vti0 type vti local 198.51.100.10 remote 203.0.113.10 key 42
on vpn ip addr add 169.254.21.2/30 dev vti0
on vpn ip link set vti0 up
sudo systemctl enable --now strongswan@vpn
for _ in $(seq 1 40); do on office curl -s -m 2 http://10.20.1.10/ && break; sleep 1; done
