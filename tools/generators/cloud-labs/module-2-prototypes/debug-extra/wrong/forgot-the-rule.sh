# Wrong: all three faults are fixed, but joining again reset who may log in,
# and the rule was never put back. SSH still stops bob; nothing else does.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
