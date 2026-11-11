# Wrong: the site's resolver service is stopped and dnsmasq is started by
# hand, with the forwarders on its command line. Everything works until the
# next boot, which starts the service again, with no forwarders, and then
# lab can't find the domain.
sudo systemctl stop dnsmasq
sudo dnsmasq --conf-dir=/etc/dnsmasq.d --server=/ad.shop.test/10.0.9.10 --server=/9.0.10.in-addr.arpa/10.0.9.10
sleep 1
dig +short _ldap._tcp.ad.shop.test SRV
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test
