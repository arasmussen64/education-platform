# Wrong: the broken forwarders are left as they are, and lab stops asking
# the site's resolver: /etc/resolv.conf is rewritten by hand to ask dc1.
# The other two faults are fixed properly. It works today; the lab's
# network writes resolv.conf afresh at every boot, as a cloud network's
# DHCP does, so after the next reboot nobody from the domain gets in again.
sudo sh -c 'echo nameserver 10.0.9.10 > /etc/resolv.conf'
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
printf '# Only these groups may log in over SSH.\nAllowGroups ssh-users linux-admins@ad.shop.test\n' | sudo tee /etc/ssh/sshd_config.d/60-access.conf > /dev/null
sudo systemctl try-reload-or-restart ssh
