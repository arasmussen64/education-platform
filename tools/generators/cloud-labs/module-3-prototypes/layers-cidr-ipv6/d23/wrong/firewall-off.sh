sudo sed -i 's/policy drop/policy accept/' /etc/netlab/web/nftables.conf
sudo sed -i '/neigh replace 10.0.2.30/d; /ip link set prn down/d' /etc/netlab/r2/up
sudo systemctl restart netlab; sleep 1
