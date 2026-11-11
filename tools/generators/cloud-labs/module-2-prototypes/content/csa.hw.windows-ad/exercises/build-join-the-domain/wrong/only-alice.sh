# Wrong: permits one person by name instead of the group, so the group's
# other member, carol, is refused, and so is whoever joins the group next.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit alice@ad.shop.test
