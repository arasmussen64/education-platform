# Wrong: instead of the login step that makes a home directory at each
# person's first login, alice's and carol's homes are made by hand. They
# land in them, but dana, the group's third member, and whoever joins the
# group next, log in to no home at all.
printf 'server=/ad.shop.test/10.0.9.10\nserver=/9.0.10.in-addr.arpa/10.0.9.10\n' | sudo tee /etc/dnsmasq.d/ad.conf > /dev/null
sudo systemctl restart dnsmasq
echo 'Shop-Admin-1' | sudo realm join -U Administrator ad.shop.test
sudo realm permit -g linux-admins@ad.shop.test
for person in alice carol; do
  sudo mkdir -p "/home/$person@ad.shop.test"
  sudo chown "$person@ad.shop.test:domain users@ad.shop.test" "/home/$person@ad.shop.test"
  sudo chmod 750 "/home/$person@ad.shop.test"
done
