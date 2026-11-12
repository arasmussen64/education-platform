sudo sed -i 's/^ip route add default via 10.0.2.1$/ip route add default via 10.0.2.1 mtu 1476/' /etc/netlab/web/up
sudo sed -i '/neigh replace 10.0.2.30/d; /ip link set prn down/d' /etc/netlab/r2/up
sudo systemctl restart netlab; sleep 1
