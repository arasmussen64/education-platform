# Wrong: the names and the SSH rule are fixed, but the machine's own key
# still doesn't match its account, so SSSD stays offline and nobody from the
# domain gets in.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
sudo systemctl restart sssd
sleep 5
