# Wrong: the names and SSH's list are fixed, but after joining again the
# two members the prompt names are permitted one by one in SSSD's rule,
# instead of the group. alice and carol get in; dana, the group's third
# member, is refused, and so would be whoever joins the group next month.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit alice@ad.shop.test carol@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
