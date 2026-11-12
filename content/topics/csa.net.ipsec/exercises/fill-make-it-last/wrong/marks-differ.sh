# Wrong: vti0's key is 43, but the connection marks its SAs 42. The tunnel
# comes up, yet nothing routed into vti0 matches its SA, so BGP's packets
# and the office's go nowhere.
on vpn sed -i 's/key ___$/key 43/; s|ip addr add ___ dev vti0|ip addr add 169.254.21.2/30 dev vti0|' /etc/network/up
on vpn sed -i 's/keyingtries = ___/keyingtries = 0/; s/start_action = ___/start_action = start/; s/close_action = ___/close_action = start/; s/dpd_action = ___/dpd_action = restart/' /etc/swanctl/conf.d/cloud.conf
sudo systemctl enable strongswan@vpn
sudo netlab restart
for _ in $(seq 1 15); do on office curl -s -m 2 http://10.20.1.10/ && break; sleep 1; done
