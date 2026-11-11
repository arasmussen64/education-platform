# Wrong: the SSH group list is replaced with the domain group instead of
# having it added, so the local operator, kim, is locked out of SSH now.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
