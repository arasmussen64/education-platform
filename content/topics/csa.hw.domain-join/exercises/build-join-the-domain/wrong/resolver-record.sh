# Wrong: only the domain's own zone is forwarded, and dc1's address is given
# its name by a record typed into the site's resolver (ptr-record=, the kind
# of line site.conf uses for intranet.shop.internal) in place of the reverse
# zone's forwarder. It answers today, until dc1's address changes or a
# second controller arrives.
printf 'server=/ad.shop.test/10.0.9.10\nptr-record=10.9.0.10.in-addr.arpa,dc1.ad.shop.test\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
dig +short -x 10.0.9.10
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit -g linux-admins@ad.shop.test
