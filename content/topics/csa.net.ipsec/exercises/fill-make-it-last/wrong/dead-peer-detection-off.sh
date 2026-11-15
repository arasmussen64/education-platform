# Wrong: every gap filled with the right word, but the dpd_delay line was
# deleted along the way, though the prompt says to replace each ___ and
# nothing else. Without it vpn never asks whether the provider is still
# there, so dpd_action has nothing to act on: when the path goes dead, vpn
# holds a tunnel that carries nothing for as long as the outage lasts.
on vpn sed -i 's/key ___$/key 42/; s|ip addr add ___ dev vti0|ip addr add 169.254.21.2/30 dev vti0|' /etc/network/up
on vpn sed -i 's/keyingtries = ___/keyingtries = 0/; s/start_action = ___/start_action = start/; s/close_action = ___/close_action = start/; s/dpd_action = ___/dpd_action = restart/' /etc/swanctl/conf.d/cloud.conf
on vpn sed -i '/dpd_delay/d' /etc/swanctl/conf.d/cloud.conf
sudo systemctl enable strongswan@vpn
sudo netlab restart
for _ in $(seq 1 40); do on office curl -s -m 2 http://10.20.1.10/ && break; sleep 1; done
