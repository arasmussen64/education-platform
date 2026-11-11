# Wrong: the two members the prompt names are permitted one by one, instead
# of the group. alice and carol get in and bob is kept out, but dana, the
# group's third member, is refused, and so would be whoever joins the group
# next month.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo pam-auth-update --enable mkhomedir
sudo realm permit alice@ad.shop.test carol@ad.shop.test
