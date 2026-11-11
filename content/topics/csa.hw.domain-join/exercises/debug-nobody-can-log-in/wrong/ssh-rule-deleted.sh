# Wrong: the SSH restriction that was in the way is deleted rather than
# corrected, so every local account can log in over SSH again, ben too.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
sudo rm /etc/ssh/sshd_config.d/60-access.conf
sudo systemctl try-reload-or-restart ssh
