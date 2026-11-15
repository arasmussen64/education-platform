# Wrong: gap 6 filled with clear, strongSwan's default: when the provider
# stops answering, vpn closes the tunnel and does nothing more, so it stays
# down after the path is back, until someone types swanctl --initiate.
on vpn sed -i 's/key ___$/key 42/; s|ip addr add ___ dev vti0|ip addr add 169.254.21.2/30 dev vti0|' /etc/network/up
on vpn sed -i 's/keyingtries = ___/keyingtries = 0/; s/start_action = ___/start_action = start/; s/close_action = ___/close_action = start/; s/dpd_action = ___/dpd_action = clear/' /etc/swanctl/conf.d/cloud.conf
sudo systemctl enable strongswan@vpn
sudo netlab restart
for _ in $(seq 1 40); do on office curl -s -m 2 http://10.20.1.10/ && break; sleep 1; done
