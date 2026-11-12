sudo sed -i '/neigh replace 10.0.2.30/d; /ip link set prn down/d' /etc/netlab/r2/up
printf 'flush ruleset\ntable inet mangle {\n  chain forward {\n    type filter hook forward priority mangle; policy accept;\n    tcp flags syn tcp option maxseg size set rt mtu\n  }\n}\n' | sudo tee /etc/netlab/r2/nftables.conf > /dev/null
sudo systemctl restart netlab; sleep 1
