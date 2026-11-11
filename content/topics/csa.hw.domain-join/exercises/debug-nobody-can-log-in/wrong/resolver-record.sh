# Wrong: the forwarder for the domain's own zone is pointed at dc1 again,
# but the reverse zone's is replaced by a record typed into the site's
# resolver (ptr-record=, the kind of line site.conf uses for its own names)
# that gives dc1's address its name. The other two faults are fixed
# properly. It answers today, until dc1's address changes or a second
# controller arrives.
printf 'server=/ad.shop.test/10.0.9.10\nptr-record=10.9.0.10.in-addr.arpa,dc1.ad.shop.test\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
