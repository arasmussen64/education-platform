# Wrong: lab stops asking the site's resolver and asks dc1 directly, with
# /etc/resolv.conf rewritten by hand. Everything answers today, but the
# lab's network writes resolv.conf afresh at every boot, as a cloud
# network's DHCP does, so after the next reboot lab can't find the domain.
sudo sh -c 'echo nameserver 10.0.9.10 > /etc/resolv.conf'
dig +short _ldap._tcp.ad.shop.test SRV
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test
