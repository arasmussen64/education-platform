# Wrong: the names and the machine's account are fixed properly, but SSH's
# file is left as it was: its socket and service are stopped and sshd is
# started by hand, with the domain group added on its command line. Logins
# work until the next boot, which starts SSH again from its files, and then
# alice and carol are refused again.
sudo sed -i 's/10\.0\.9\.11/10.0.9.10/' /etc/dnsmasq.d/ad.conf
sudo systemctl restart dnsmasq
sudo realm leave
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
sudo systemctl stop ssh.socket ssh.service
sudo mkdir -p /run/sshd
sudo /usr/sbin/sshd -o AllowGroups=linux-admins@ad.shop.test
