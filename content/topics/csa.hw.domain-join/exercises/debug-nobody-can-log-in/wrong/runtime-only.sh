# Wrong: the names and the machine's account are fixed properly, and the
# domain group is let into SSH through a drop-in and an environment file
# under /run (where systemctl edit --runtime puts a drop-in), handing sshd
# an extra AllowGroups on its command line. It works until the next reboot,
# which empties /run, and then alice and carol are refused again.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
echo 'SSHD_OPTS=-oAllowGroups=linux-admins@ad.shop.test' | sudo tee /run/ssh-access.env > /dev/null
sudo mkdir -p /run/systemd/system/ssh.service.d
printf '[Service]\nEnvironmentFile=/run/ssh-access.env\n' | sudo tee /run/systemd/system/ssh.service.d/access.conf > /dev/null
sudo systemctl daemon-reload
sudo systemctl restart ssh
