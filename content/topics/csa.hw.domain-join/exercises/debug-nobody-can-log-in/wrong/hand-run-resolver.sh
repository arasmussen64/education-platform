# Wrong: the broken forwarders are left in their file; the site's resolver
# service is stopped and dnsmasq is started by hand, skipping that file and
# given the right forwarders on its command line. Everything works until
# the next boot, which starts the service again with the broken file.
sudo systemctl stop dnsmasq
sudo dnsmasq --conf-dir=/etc/dnsmasq.d,ad.conf --server=/ad.shop.test/10.0.9.10 --server=/9.0.10.in-addr.arpa/10.0.9.10
sleep 1
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
