echo 'ip link set eth0 mtu 1476' | sudo tee -a /etc/netlab/web/up > /dev/null
sudo sed -i '/neigh replace 10.0.2.30/d; /ip link set prn down/d' /etc/netlab/r2/up
sudo systemctl restart netlab; sleep 1
