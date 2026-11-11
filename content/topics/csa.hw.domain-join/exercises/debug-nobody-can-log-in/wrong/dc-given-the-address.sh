# Wrong: the forwarders are left pointing at 10.0.9.11, and dc1 is given
# that address as well, by hand, and restarted so that it answers there.
# Names work until the next boot, which makes dc1's network again with
# only 10.0.9.10, and then lab can't find the domain.
sudo ip -n dc addr add 10.0.9.11/24 dev eth0
sudo systemctl restart lab-dc
sleep 3
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
