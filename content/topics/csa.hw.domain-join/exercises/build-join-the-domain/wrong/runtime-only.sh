# Wrong: the forwarders are handed to the site's resolver in a drop-in under
# /run (where systemctl edit --runtime puts one) instead of a file in
# /etc/dnsmasq.d. Everything works until the next reboot, which empties
# /run, and then lab can't find the domain.
sudo mkdir -p /run/systemd/system/dnsmasq.service.d
printf '[Service]\nEnvironment="DNSMASQ_OPTS=--server=/ad.shop.test/10.0.9.10 --server=/9.0.10.in-addr.arpa/10.0.9.10"\n' | sudo tee /run/systemd/system/dnsmasq.service.d/ad.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart dnsmasq
dig +short _ldap._tcp.ad.shop.test SRV
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test
