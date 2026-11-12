# The reference: fill in the six gaps, enable the IPsec service, and reboot
# the network to prove it all comes back. "sed -i 's/OLD/NEW/' FILE"
# replaces OLD with NEW in the file, the same edit as typing it in nano;
# each s/.../.../ below fills one gap.

# 1 and 2: vti0's key, which must be the connection's mark (42), and vpn's
# inside address from the sheet, with its length.
on vpn sed -i 's/key ___$/key 42/; s|ip addr add ___ dev vti0|ip addr add 169.254.21.2/30 dev vti0|' /etc/network/up
# 3 to 6: keep trying at the start, start at boot, start again when the
# provider closes the tunnel, and start again when it stops answering.
on vpn sed -i 's/keyingtries = ___/keyingtries = 0/; s/start_action = ___/start_action = start/; s/close_action = ___/close_action = start/; s/dpd_action = ___/dpd_action = restart/' /etc/swanctl/conf.d/cloud.conf
on vpn cat /etc/network/up
on vpn grep -n '_action\|keyingtries' /etc/swanctl/conf.d/cloud.conf

# The IPsec service starts at every boot from now on, and the network is
# rebuilt as a reboot would: vti0 from the network file, then the services.
sudo systemctl enable strongswan@vpn
sudo netlab restart
for _ in $(seq 1 40); do on office curl -s -m 2 http://10.20.1.10/ && break; sleep 1; done
on vpn swanctl --list-sas
on vpn ip route show proto bgp
